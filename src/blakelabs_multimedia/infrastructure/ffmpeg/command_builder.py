from __future__ import annotations

from pathlib import Path
from uuid import UUID

from blakelabs_multimedia.domain.conversion import ProcessingRequest


def build_ffprobe_arguments(source: Path) -> list[str]:
    return [
        "-v",
        "error",
        "-show_entries",
        (
            "format=format_name,duration,size:"
            "stream=codec_type,codec_name,width,height,duration,"
            "nb_frames,channels,sample_rate"
        ),
        "-of",
        "json",
        str(source),
    ]


def build_ffmpeg_arguments(request: ProcessingRequest, temporary_output: Path) -> list[str]:
    return [
        "-hide_banner",
        "-nostdin",
        "-y",
        "-i",
        str(request.source),
        *request.preset.ffmpeg_args,
        "-progress",
        "pipe:1",
        "-nostats",
        str(temporary_output),
    ]


def choose_output_path(source: Path, extension: str, output_directory: Path | None = None) -> Path:
    directory = output_directory or source.parent
    directory.mkdir(parents=True, exist_ok=True)
    base = directory / f"{source.stem}-converted.{extension.lstrip('.')}"
    if not base.exists() and base.resolve() != source.resolve():
        return base
    counter = 2
    while True:
        candidate = directory / f"{source.stem}-converted-{counter}.{extension.lstrip('.')}"
        if not candidate.exists() and candidate.resolve() != source.resolve():
            return candidate
        counter += 1


def temporary_output_path(output: Path, job_id: UUID) -> Path:
    return output.with_name(f".{output.stem}.{job_id.hex}.part{output.suffix}")
