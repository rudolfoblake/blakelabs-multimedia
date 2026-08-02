from __future__ import annotations

import logging
from collections.abc import Callable
from pathlib import Path
from uuid import uuid4

from PySide6.QtCore import QProcess

from blakelabs_multimedia.application.ports.media_probe import CancelHandle
from blakelabs_multimedia.domain.media import MediaAsset
from blakelabs_multimedia.infrastructure.ffmpeg.binary_resolver import (
    BinaryNotFoundError,
    FfmpegBinaryResolver,
)
from blakelabs_multimedia.infrastructure.ffmpeg.probe_parser import (
    InvalidProbeOutputError,
    parse_ffprobe_json,
)

LOGGER = logging.getLogger(__name__)


class _QtProcessHandle:
    def __init__(self, process: QProcess) -> None:
        self._process = process

    def cancel(self) -> None:
        if self._process.state() != QProcess.ProcessState.NotRunning:
            self._process.kill()


class _NoopHandle:
    def cancel(self) -> None:
        return None


class QtFfprobeMediaProbe:
    """FFprobe adapter using Qt's non-blocking process integration."""

    def __init__(self, resolver: FfmpegBinaryResolver) -> None:
        self._resolver = resolver
        self._processes: dict[str, QProcess] = {}

    def probe(
        self,
        path: Path,
        *,
        completed: Callable[[MediaAsset], None],
        failed: Callable[[str], None],
    ) -> CancelHandle:
        try:
            binary = self._resolver.ffprobe()
        except BinaryNotFoundError as exc:
            failed(str(exc))
            return _NoopHandle()

        process_id = uuid4().hex
        process = QProcess()
        process.setProgram(str(binary))
        process.setArguments(
            [
                "-v",
                "error",
                "-print_format",
                "json",
                "-show_format",
                "-show_streams",
                str(path),
            ]
        )
        process.setProcessChannelMode(QProcess.ProcessChannelMode.SeparateChannels)
        self._processes[process_id] = process

        stdout = bytearray()
        stderr = bytearray()
        finished_once = False

        def read_stdout() -> None:
            stdout.extend(bytes(process.readAllStandardOutput()))

        def read_stderr() -> None:
            stderr.extend(bytes(process.readAllStandardError()))

        def cleanup() -> None:
            self._processes.pop(process_id, None)
            process.deleteLater()

        def fail_once(message: str) -> None:
            nonlocal finished_once
            if finished_once:
                return
            finished_once = True
            failed(message)
            cleanup()

        def finish(exit_code: int, _exit_status: QProcess.ExitStatus) -> None:
            nonlocal finished_once
            if finished_once:
                return
            read_stdout()
            read_stderr()
            if exit_code != 0:
                detail = stderr.decode(errors="replace").strip()
                fail_once(detail or f"FFprobe exited with code {exit_code}.")
                return
            try:
                asset = parse_ffprobe_json(path, bytes(stdout))
            except InvalidProbeOutputError as exc:
                fail_once(str(exc))
                return
            finished_once = True
            completed(asset)
            cleanup()

        def process_error(error: QProcess.ProcessError) -> None:
            LOGGER.warning("FFprobe process error for %s: %s", path, error)
            fail_once(process.errorString() or "Unable to start FFprobe.")

        process.readyReadStandardOutput.connect(read_stdout)
        process.readyReadStandardError.connect(read_stderr)
        process.finished.connect(finish)
        process.errorOccurred.connect(process_error)
        process.start()
        return _QtProcessHandle(process)
