from typing import cast

from PySide6.QtCore import QProcess

from blakelabs_multimedia.infrastructure.ffmpeg.qt_probe import (
    _ProbeState,
    _QtProcessHandle as ProbeHandle,
)
from blakelabs_multimedia.infrastructure.ffmpeg.qt_processor import _append_bounded_tail


class _FakeProcess:
    def __init__(self, state: _ProbeState) -> None:
        self._probe_state = state
        self.killed = False

    def state(self) -> QProcess.ProcessState:
        return QProcess.ProcessState.Running

    def kill(self) -> None:
        assert self._probe_state.cancel_requested
        self.killed = True


def test_probe_cancellation_is_recorded_before_process_is_killed() -> None:
    state = _ProbeState()
    process = _FakeProcess(state)

    ProbeHandle(cast(QProcess, process), state).cancel()

    assert state.cancel_requested is True
    assert process.killed is True


def test_ffmpeg_diagnostics_keep_the_most_recent_bytes() -> None:
    diagnostics = bytearray(b"old")

    _append_bounded_tail(diagnostics, b"new", 5)

    assert diagnostics == b"ldnew"


def test_ffmpeg_diagnostics_trim_oversized_single_chunks() -> None:
    diagnostics = bytearray(b"obsolete")

    _append_bounded_tail(diagnostics, b"0123456789", 4)

    assert diagnostics == b"6789"


def test_ffmpeg_diagnostics_clear_when_disabled() -> None:
    diagnostics = bytearray(b"existing")

    _append_bounded_tail(diagnostics, b"ignored", 0)

    assert diagnostics == b""
