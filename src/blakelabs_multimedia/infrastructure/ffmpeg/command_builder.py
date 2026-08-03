from __future__ import annotations

from pathlib import Path
from uuid import UUID

from blakelabs_multimedia.domain.conversion import (
    ConversionOptions,
    PresetGroup,
    ProcessingRequest,
)


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
    output_arguments = _apply_conversion_options(
        list(request.preset.ffmpeg_args),
        request.options,
        request.preset.group,
        request.preset.extension,
    )
    if request.preset.group is PresetGroup.VIDEO:
        output_arguments.extend(("-avoid_negative_ts", "make_zero"))

    return [
        "-hide_banner",
        "-nostdin",
        "-y",
        "-fflags",
        "+genpts",
        "-i",
        str(request.source),
        "-ignore_unknown",
        *output_arguments,
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


def _apply_conversion_options(
    arguments: list[str],
    options: ConversionOptions,
    group: PresetGroup,
    extension: str,
) -> list[str]:
    if not options.preserve_metadata:
        _replace_pair(arguments, "-map_metadata", "-1")

    has_audio = group is not PresetGroup.QUICK_TOOL
    if has_audio:
        if options.audio_bitrate_kbps is not None and extension in {"mp3", "mp4", "webm"}:
            _remove_pair(arguments, "-q:a")
            _replace_pair(arguments, "-b:a", f"{options.audio_bitrate_kbps}k")
        if options.audio_sample_rate_hz is not None:
            _replace_pair(arguments, "-ar", str(options.audio_sample_rate_hz))
        if options.audio_channels is not None:
            _replace_pair(arguments, "-ac", str(options.audio_channels))
        if options.normalize_audio:
            _replace_pair(arguments, "-af", "loudnorm=I=-16:LRA=11:TP=-1.5")

    if group is PresetGroup.VIDEO:
        if options.video_bitrate_kbps is not None:
            _remove_pair(arguments, "-crf")
            _replace_pair(arguments, "-b:v", f"{options.video_bitrate_kbps}k")
            _replace_pair(arguments, "-maxrate", f"{options.video_bitrate_kbps}k")
            _replace_pair(arguments, "-bufsize", f"{options.video_bitrate_kbps * 2}k")
        elif options.video_crf is not None:
            _remove_pair(arguments, "-maxrate")
            _remove_pair(arguments, "-bufsize")
            _replace_pair(arguments, "-crf", str(options.video_crf))

        if options.video_encoder_preset is not None:
            _replace_pair(arguments, "-preset", options.video_encoder_preset)
        if options.video_max_width is not None:
            _replace_pair(
                arguments,
                "-vf",
                f"scale=min({options.video_max_width}\\,iw):-2",
            )

    return arguments


def _replace_pair(arguments: list[str], option: str, value: str) -> None:
    _remove_pair(arguments, option)
    arguments.extend((option, value))


def _remove_pair(arguments: list[str], option: str) -> None:
    index = 0
    while index < len(arguments):
        if arguments[index] != option:
            index += 1
            continue
        del arguments[index]
        if index < len(arguments):
            del arguments[index]
