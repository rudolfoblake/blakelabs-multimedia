from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from pathlib import Path
from uuid import UUID

from PySide6.QtCore import QProcess, QTimer

from blakelabs_multimedia.application.ports.media_probe import CancelHandle
from blakelabs_multimedia.application.ports.media_processor import ProcessingObserver
from blakelabs_multimedia.domain.conversion import ProcessingRequest
from blakelabs_multimedia.infrastructure.ffmpeg.binary_resolver import (
    BinaryNotFoundError,
    FfmpegBinaryResolver,
)
from blakelabs_multimedia.infrastructure.ffmpeg.command_builder import (
    build_ffmpeg_arguments,
    temporary_output_path,
)
from blakelabs_multimedia.infrastructure.ffmpeg.progress_parser import FfmpegProgressParser

LOGGER = logging.getLogger(__name__)


@dataclass(slots=True)
class _ProcessContext:
    request: ProcessingRequest
    observer: ProcessingObserver
    process: QProcess
    temporary_output: Path
    parser: FfmpegProgressParser
    stderr: bytearray
    settled: bool = False
    cancel_requested: bool = False


class _QtProcessHandle:
    def __init__(self, context: _ProcessContext) -> None:
        self._context = context

    def cancel(self) -> None:
        context = self._context
        if context.settled or context.process.state() == QProcess.ProcessState.NotRunning:
            return
        context.cancel_requested = True
        context.process.terminate()

        def force_kill() -> None:
            if context.process.state() != QProcess.ProcessState.NotRunning:
                context.process.kill()

        QTimer.singleShot(1500, force_kill)


class _NoopHandle:
    def cancel(self) -> None:
        return None


class QtFfmpegMediaProcessor:
    """Non-blocking FFmpeg adapter with atomic output publication."""

    def __init__(self, resolver: FfmpegBinaryResolver) -> None:
        self._resolver = resolver
        self._contexts: dict[UUID, _ProcessContext] = {}

    def process(self, request: ProcessingRequest, observer: ProcessingObserver) -> CancelHandle:
        try:
            binary = self._resolver.ffmpeg()
        except BinaryNotFoundError as exc:
            observer.failed(str(exc))
            return _NoopHandle()

        request.output.parent.mkdir(parents=True, exist_ok=True)
        temporary_output = temporary_output_path(request.output, request.job_id)
        temporary_output.unlink(missing_ok=True)

        process = QProcess()
        process.setProgram(str(binary))
        process.setArguments(build_ffmpeg_arguments(request, temporary_output))
        process.setProcessChannelMode(QProcess.ProcessChannelMode.SeparateChannels)
        context = _ProcessContext(
            request=request,
            observer=observer,
            process=process,
            temporary_output=temporary_output,
            parser=FfmpegProgressParser(request.duration_seconds),
            stderr=bytearray(),
        )
        self._contexts[request.job_id] = context

        def read_stdout() -> None:
            chunk = bytes(process.readAllStandardOutput().data())
            for progress in context.parser.feed(chunk):
                observer.progressed(progress)

        def read_stderr() -> None:
            context.stderr.extend(process.readAllStandardError().data())

        def cleanup() -> None:
            self._contexts.pop(request.job_id, None)
            process.deleteLater()

        def fail_once(message: str) -> None:
            if context.settled:
                return
            context.settled = True
            temporary_output.unlink(missing_ok=True)
            observer.failed(message)
            cleanup()

        def cancel_once() -> None:
            if context.settled:
                return
            context.settled = True
            temporary_output.unlink(missing_ok=True)
            observer.cancelled()
            cleanup()

        def finish(exit_code: int, _exit_status: QProcess.ExitStatus) -> None:
            if context.settled:
                return
            read_stdout()
            read_stderr()
            if context.cancel_requested:
                cancel_once()
                return
            if exit_code != 0 or not temporary_output.exists():
                detail = context.stderr.decode(errors="replace").strip()
                fail_once(_last_meaningful_line(detail) or f"FFmpeg exited with code {exit_code}.")
                return
            try:
                os.replace(temporary_output, request.output)
            except OSError as exc:
                fail_once(f"Could not publish output file: {exc}")
                return
            context.settled = True
            observer.completed(request.output)
            cleanup()

        def process_error(error: QProcess.ProcessError) -> None:
            LOGGER.warning("FFmpeg process error for %s: %s", request.source, error)
            if error == QProcess.ProcessError.FailedToStart:
                fail_once(process.errorString() or "Unable to start FFmpeg.")

        process.started.connect(observer.started)
        process.readyReadStandardOutput.connect(read_stdout)
        process.readyReadStandardError.connect(read_stderr)
        process.finished.connect(finish)
        process.errorOccurred.connect(process_error)
        process.start()
        return _QtProcessHandle(context)


def _last_meaningful_line(message: str) -> str:
    lines = [line.strip() for line in message.splitlines() if line.strip()]
    return lines[-1] if lines else ""
