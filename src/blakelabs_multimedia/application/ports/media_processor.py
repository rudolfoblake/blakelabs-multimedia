from __future__ import annotations

from pathlib import Path
from typing import Protocol

from blakelabs_multimedia.application.ports.media_probe import CancelHandle
from blakelabs_multimedia.domain.conversion import ProcessingProgress, ProcessingRequest


class ProcessingObserver(Protocol):
    def started(self) -> None: ...

    def progressed(self, progress: ProcessingProgress) -> None: ...

    def completed(self, output: Path) -> None: ...

    def failed(self, message: str) -> None: ...

    def cancelled(self) -> None: ...


class MediaProcessorPort(Protocol):
    def process(self, request: ProcessingRequest, observer: ProcessingObserver) -> CancelHandle:
        """Start processing and return immediately."""
