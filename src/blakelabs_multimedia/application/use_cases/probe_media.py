from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from blakelabs_multimedia.application.ports.media_probe import CancelHandle, MediaProbePort
from blakelabs_multimedia.domain.media import MediaAsset


class _CompletedHandle:
    def cancel(self) -> None:
        return None


class ProbeMedia:
    """Validate an input path and delegate asynchronous metadata probing."""

    def __init__(self, probe: MediaProbePort) -> None:
        self._probe = probe

    def execute(
        self,
        path: Path,
        *,
        completed: Callable[[MediaAsset], None],
        failed: Callable[[str], None],
    ) -> CancelHandle:
        normalized = path.expanduser().resolve()
        if not normalized.exists():
            failed("The selected file no longer exists.")
            return _CompletedHandle()
        if not normalized.is_file():
            failed("Only local files are supported in this version.")
            return _CompletedHandle()

        return self._probe.probe(normalized, completed=completed, failed=failed)
