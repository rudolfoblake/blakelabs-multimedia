from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from uuid import UUID

from blakelabs_multimedia.domain.media import MediaKind


class PresetGroup(StrEnum):
    VIDEO = "video"
    AUDIO = "audio"
    QUICK_TOOL = "quick-tool"


@dataclass(frozen=True, slots=True)
class ConversionPreset:
    id: str
    title: str
    description: str
    group: PresetGroup
    extension: str
    ffmpeg_args: tuple[str, ...]
    accepted_kinds: frozenset[MediaKind]

    def accepts(self, kind: MediaKind) -> bool:
        return kind in self.accepted_kinds


@dataclass(frozen=True, slots=True)
class ProcessingRequest:
    job_id: UUID
    source: Path
    output: Path
    duration_seconds: float | None
    preset: ConversionPreset


@dataclass(frozen=True, slots=True)
class ProcessingProgress:
    ratio: float
    processed_seconds: float
    speed: float | None = None
    eta_seconds: int | None = None


VIDEO_AND_AUDIO = frozenset({MediaKind.VIDEO, MediaKind.AUDIO})
VIDEO_ONLY = frozenset({MediaKind.VIDEO})

DEFAULT_PRESETS: tuple[ConversionPreset, ...] = (
    ConversionPreset(
        id="mp4-balanced",
        title="MP4 Universal",
        description="H.264 + AAC, ideal for TVs, phones and web.",
        group=PresetGroup.VIDEO,
        extension="mp4",
        ffmpeg_args=(
            "-map", "0:v:0?", "-map", "0:a:0?", "-map_metadata", "0",
            "-c:v", "libx264", "-preset", "medium", "-crf", "22",
            "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
            "-movflags", "+faststart",
        ),
        accepted_kinds=VIDEO_ONLY,
    ),
    ConversionPreset(
        id="mp4-compact",
        title="MP4 Compact",
        description="Smaller 720p output for sharing and storage.",
        group=PresetGroup.VIDEO,
        extension="mp4",
        ffmpeg_args=(
            "-map", "0:v:0?", "-map", "0:a:0?", "-vf", "scale=min(1280\\,iw):-2",
            "-c:v", "libx264", "-preset", "slow", "-crf", "27",
            "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k",
            "-movflags", "+faststart",
        ),
        accepted_kinds=VIDEO_ONLY,
    ),
    ConversionPreset(
        id="webm-modern",
        title="WebM Modern",
        description="VP9 + Opus for efficient browser playback.",
        group=PresetGroup.VIDEO,
        extension="webm",
        ffmpeg_args=(
            "-map", "0:v:0?", "-map", "0:a:0?", "-c:v", "libvpx-vp9",
            "-crf", "31", "-b:v", "0", "-row-mt", "1",
            "-c:a", "libopus", "-b:a", "128k",
        ),
        accepted_kinds=VIDEO_ONLY,
    ),
    ConversionPreset(
        id="extract-mp3",
        title="Extract MP3",
        description="Extract audio as a high-quality MP3 file.",
        group=PresetGroup.AUDIO,
        extension="mp3",
        ffmpeg_args=("-vn", "-map_metadata", "0", "-c:a", "libmp3lame", "-q:a", "2"),
        accepted_kinds=VIDEO_AND_AUDIO,
    ),
    ConversionPreset(
        id="audio-flac",
        title="FLAC Lossless",
        description="Lossless audio archive with metadata preserved.",
        group=PresetGroup.AUDIO,
        extension="flac",
        ffmpeg_args=("-vn", "-map_metadata", "0", "-c:a", "flac", "-compression_level", "8"),
        accepted_kinds=VIDEO_AND_AUDIO,
    ),
    ConversionPreset(
        id="audio-wav",
        title="WAV Studio",
        description="24-bit PCM for editing and production workflows.",
        group=PresetGroup.AUDIO,
        extension="wav",
        ffmpeg_args=("-vn", "-c:a", "pcm_s24le"),
        accepted_kinds=VIDEO_AND_AUDIO,
    ),
    ConversionPreset(
        id="gif-loop",
        title="Animated GIF",
        description="Create a compact looping GIF from video.",
        group=PresetGroup.QUICK_TOOL,
        extension="gif",
        ffmpeg_args=("-an", "-vf", "fps=15,scale=960:-1:flags=lanczos", "-loop", "0"),
        accepted_kinds=VIDEO_ONLY,
    ),
)


def find_preset(preset_id: str) -> ConversionPreset:
    for preset in DEFAULT_PRESETS:
        if preset.id == preset_id:
            return preset
    raise KeyError(f"Unknown conversion preset: {preset_id}")
