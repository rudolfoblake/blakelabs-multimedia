from __future__ import annotations

import logging
from collections.abc import Callable
from pathlib import Path
from uuid import uuid4

from PySide6.QtCore import QProcess, QTimer

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
PROBE_TIMEOUT_MS = 15_000
MAX_PROBE_OUTPUT_BYTES = 2 * 1024 * 1024


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
                "-nostdin",
                "-show_entries",
                (
                    "format=format_name,duration,size:"
                    "stream=codec_type,codec_name,width,height,duration,"
                    "nb_frames,channels,sample_rate"
                ),
                "-of",
                "json",
                str(path),
            ]
        )
        process.setProcessChannelMode(QProcess.ProcessChannelMode.SeparateChannels)
        self._processes[process_id] = process

        timeout = QTimer(process)
        timeout.setSingleShot(True)
        timeout.setInterval(PROBE_TIMEOUT_MS)
        stdout = bytearray()
        stderr = bytearray()
        finished_once = False

        def cleanup() -> None:
            timeout.stop()
            self._processes.pop(process_id, None)
            process.deleteLater()

        def fail_once(message: str) -> None:
            nonlocal finished_once
            if finished_once:
                return
            finished_once = True
            LOGGER.error("Media probe failed for %s: %s", path, message)
            failed(message)
            cleanup()

        def append_output(target: bytearray, payload: bytes, stream_name: str) -> None:
            if finished_once or not payload:
                return
            target.extend(payload)
            if len(target) > MAX_PROBE_OUTPUT_BYTES:
                process.kill()
                fail_once(f"Media analysis returned too much {stream_name} data.")

        def read_stdout() -> None:
            append_output(
                stdout,
                bytes(process.readAllStandardOutput().data()),
                "metadata",
            )

        def read_stderr() -> None:
            append_output(
                stderr,
                bytes(process.readAllStandardError().data()),
                "diagnostic",
            )

        def finish(exit_code: int, exit_status: QProcess.ExitStatus) -> None:
            nonlocal finished_once
            if finished_once:
                return
            read_stdout()
            read_stderr()
            if exit_status == QProcess.ExitStatus.CrashExit:
                fail_once("Media analysis stopped unexpectedly.")
                return
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
            LOGGER.info("Media probe completed for %s", path)
            completed(asset)
            cleanup()

        def process_error(error: QProcess.ProcessError) -> None:
            LOGGER.warning("FFprobe process error for %s: %s", path, error)
            fail_once(process.errorString() or "Unable to start media analysis.")

        def timed_out() -> None:
            if finished_once:
                return
            LOGGER.warning("FFprobe timed out for %s", path)
            process.kill()
            fail_once("Media analysis timed out after 15 seconds.")

        process.readyReadStandardOutput.connect(read_stdout)
        process.readyReadStandardError.connect(read_stderr)
        process.finished.connect(finish)
        process.errorOccurred.connect(process_error)
        timeout.timeout.connect(timed_out)
        process.start()
        timeout.start()
        return _QtProcessHandle(process)
