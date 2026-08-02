from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from uuid import UUID

from blakelabs_multimedia.domain.media import MediaKind


class PresetGroup(StrEnum):
    VIDEO = "video"
    AUDIO = "audio"
    QUICK_TOOL = "quick-tool"


@dataclass(frozen=True, slots=True)
class ConversionOptions:
    """Optional user overrides applied after the selected professional preset."""

    audio_bitrate_kbps: int | None = None
    audio_sample_rate_hz: int | None = None
    audio_channels: int | None = None
    video_crf: int | None = None
    video_bitrate_kbps: int | None = None
    video_encoder_preset: str | None = None
    video_max_width: int | None = None
    normalize_audio: bool = False
    preserve_metadata: bool = True


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
    options: ConversionOptions = field(default_factory=ConversionOptions)


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
        description="H.264 + AAC with broad compatibility for phones, TVs and the web.",
        group=PresetGroup.VIDEO,
        extension="mp4",
        ffmpeg_args=(
            "-map",
            "0:v:0",
            "-map",
            "0:a:0?",
            "-map_metadata",
            "0",
            "-map_chapters",
            "0",
            "-sn",
            "-dn",
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "22",
            "-vf",
            "scale=trunc(iw/2)*2:trunc(ih/2)*2",
            "-pix_fmt",
            "yuv420p",
            "-tag:v",
            "avc1",
            "-fps_mode",
            "vfr",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-ar",
            "48000",
            "-ac",
            "2",
            "-max_muxing_queue_size",
            "4096",
            "-movflags",
            "+faststart",
        ),
        accepted_kinds=VIDEO_ONLY,
    ),
    ConversionPreset(
        id="mp4-compact",
        title="MP4 Compact",
        description="Efficient 720p H.264 output for sharing and storage.",
        group=PresetGroup.VIDEO,
        extension="mp4",
        ffmpeg_args=(
            "-map",
            "0:v:0",
            "-map",
            "0:a:0?",
            "-map_metadata",
            "0",
            "-map_chapters",
            "0",
            "-sn",
            "-dn",
            "-vf",
            "scale=min(1280\\,iw):-2",
            "-c:v",
            "libx264",
            "-preset",
            "slow",
            "-crf",
            "27",
            "-pix_fmt",
            "yuv420p",
            "-tag:v",
            "avc1",
            "-fps_mode",
            "vfr",
            "-c:a",
            "aac",
            "-b:a",
            "128k",
            "-ar",
            "48000",
            "-ac",
            "2",
            "-max_muxing_queue_size",
            "4096",
            "-movflags",
            "+faststart",
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
            "-map",
            "0:v:0",
            "-map",
            "0:a:0?",
            "-map_metadata",
            "0",
            "-sn",
            "-dn",
            "-vf",
            "scale=trunc(iw/2)*2:trunc(ih/2)*2",
            "-c:v",
            "libvpx-vp9",
            "-crf",
            "31",
            "-b:v",
            "0",
            "-row-mt",
            "1",
            "-c:a",
            "libopus",
            "-b:a",
            "128k",
            "-max_muxing_queue_size",
            "4096",
        ),
        accepted_kinds=VIDEO_ONLY,
    ),
    ConversionPreset(
        id="extract-mp3",
        title="Extract MP3",
        description="High-quality MP3 audio with source metadata preserved.",
        group=PresetGroup.AUDIO,
        extension="mp3",
        ffmpeg_args=(
            "-map",
            "0:a:0",
            "-vn",
            "-sn",
            "-dn",
            "-map_metadata",
            "0",
            "-c:a",
            "libmp3lame",
            "-q:a",
            "2",
        ),
        accepted_kinds=VIDEO_AND_AUDIO,
    ),
    ConversionPreset(
        id="audio-flac",
        title="FLAC Lossless",
        description="Lossless audio archive with metadata preserved.",
        group=PresetGroup.AUDIO,
        extension="flac",
        ffmpeg_args=(
            "-map",
            "0:a:0",
            "-vn",
            "-sn",
            "-dn",
            "-map_metadata",
            "0",
            "-c:a",
            "flac",
            "-compression_level",
            "8",
        ),
        accepted_kinds=VIDEO_AND_AUDIO,
    ),
    ConversionPreset(
        id="audio-wav",
        title="WAV Studio",
        description="24-bit PCM for editing and production workflows.",
        group=PresetGroup.AUDIO,
        extension="wav",
        ffmpeg_args=(
            "-map",
            "0:a:0",
            "-vn",
            "-sn",
            "-dn",
            "-c:a",
            "pcm_s24le",
        ),
        accepted_kinds=VIDEO_AND_AUDIO,
    ),
    ConversionPreset(
        id="gif-loop",
        title="Animated GIF",
        description="Create a compact looping GIF from a video.",
        group=PresetGroup.QUICK_TOOL,
        extension="gif",
        ffmpeg_args=(
            "-map",
            "0:v:0",
            "-an",
            "-sn",
            "-dn",
            "-vf",
            "fps=15,scale=960:-1:flags=lanczos",
            "-loop",
            "0",
        ),
        accepted_kinds=VIDEO_ONLY,
    ),
)


def find_preset(preset_id: str) -> ConversionPreset:
    for preset in DEFAULT_PRESETS:
        if preset.id == preset_id:
            return preset
    raise KeyError(f"Unknown conversion preset: {preset_id}")
