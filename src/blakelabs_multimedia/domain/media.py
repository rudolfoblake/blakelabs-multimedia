from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path


class MediaKind(StrEnum):
    """High-level media classification independent of the source container."""

    VIDEO = "video"
    AUDIO = "audio"
    IMAGE = "image"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class MediaAsset:
    """Normalized metadata for one local media asset."""

    path: Path
    kind: MediaKind
    container: str
    size_bytes: int
    duration_seconds: float | None = None
    video_codec: str | None = None
    audio_codec: str | None = None
    width: int | None = None
    height: int | None = None
    channels: int | None = None
    sample_rate_hz: int | None = None

    @property
    def filename(self) -> str:
        return self.path.name
