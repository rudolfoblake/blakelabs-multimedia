from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Protocol

from blakelabs_multimedia.domain.media import MediaAsset


class CancelHandle(Protocol):
    """Handle returned by asynchronous operations."""

    def cancel(self) -> None:
        """Request cancellation without blocking the caller."""


class MediaProbePort(Protocol):
    """Asynchronously normalize media metadata."""

    def probe(
        self,
        path: Path,
        *,
        completed: Callable[[MediaAsset], None],
        failed: Callable[[str], None],
    ) -> CancelHandle:
        """Start probing and return immediately."""
