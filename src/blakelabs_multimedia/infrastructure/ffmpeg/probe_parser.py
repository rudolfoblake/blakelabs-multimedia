from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from blakelabs_multimedia.domain.media import MediaAsset, MediaKind


class InvalidProbeOutputError(ValueError):
    """Raised when FFprobe returns malformed or incomplete JSON."""


def parse_ffprobe_json(path: Path, payload: bytes | str) -> MediaAsset:
    """Convert FFprobe JSON into a stable domain model."""
    try:
        raw = json.loads(payload)
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise InvalidProbeOutputError("FFprobe returned invalid JSON.") from exc

    if not isinstance(raw, dict):
        raise InvalidProbeOutputError("FFprobe returned an unexpected payload.")

    streams = raw.get("streams") or []
    format_data = raw.get("format") or {}
    if not isinstance(streams, list) or not isinstance(format_data, dict):
        raise InvalidProbeOutputError("FFprobe metadata has an unexpected shape.")

    video = _first_stream(streams, "video")
    audio = _first_stream(streams, "audio")
    image = video if video and _is_still_image(video, format_data) else None

    if image:
        kind = MediaKind.IMAGE
    elif video:
        kind = MediaKind.VIDEO
    elif audio:
        kind = MediaKind.AUDIO
    else:
        kind = MediaKind.UNKNOWN

    return MediaAsset(
        path=path,
        kind=kind,
        container=_string(format_data.get("format_name")) or path.suffix.lstrip("."),
        size_bytes=_integer(format_data.get("size")) or _safe_size(path),
        duration_seconds=_duration(format_data, video, audio),
        video_codec=_string(video.get("codec_name")) if video else None,
        audio_codec=_string(audio.get("codec_name")) if audio else None,
        width=_integer(video.get("width")) if video else None,
        height=_integer(video.get("height")) if video else None,
        channels=_integer(audio.get("channels")) if audio else None,
        sample_rate_hz=_integer(audio.get("sample_rate")) if audio else None,
    )


def _first_stream(streams: list[Any], codec_type: str) -> dict[str, Any] | None:
    return next(
        (
            stream
            for stream in streams
            if isinstance(stream, dict) and stream.get("codec_type") == codec_type
        ),
        None,
    )


def _duration(
    format_data: dict[str, Any],
    video: dict[str, Any] | None,
    audio: dict[str, Any] | None,
) -> float | None:
    for value in (
        format_data.get("duration"),
        video.get("duration") if video else None,
        audio.get("duration") if audio else None,
    ):
        try:
            if value is not None:
                parsed = float(value)
                return parsed if parsed >= 0 else None
        except (TypeError, ValueError):
            continue
    return None


def _is_still_image(video: dict[str, Any], format_data: dict[str, Any]) -> bool:
    duration = _duration(format_data, video, None)
    frame_count = _integer(video.get("nb_frames"))
    return frame_count == 1 or duration == 0


def _safe_size(path: Path) -> int:
    try:
        return path.stat().st_size
    except OSError:
        return 0


def _integer(value: object) -> int | None:
    try:
        return int(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def _string(value: object) -> str | None:
    return str(value) if value not in (None, "") else None
