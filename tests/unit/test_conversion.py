from pathlib import Path
from uuid import uuid4

from blakelabs_multimedia.domain.conversion import (
    ConversionOptions,
    ProcessingRequest,
    find_preset,
)
from blakelabs_multimedia.infrastructure.ffmpeg.command_builder import (
    build_ffmpeg_arguments,
    build_ffprobe_arguments,
    choose_output_path,
    temporary_output_path,
)


def test_output_path_never_replaces_source(tmp_path: Path) -> None:
    source = tmp_path / "track.mp3"
    source.write_bytes(b"audio")
    output = choose_output_path(source, "mp3")
    assert output != source
    assert output.name == "track-converted.mp3"


def test_probe_command_requests_only_bounded_metadata(tmp_path: Path) -> None:
    source = tmp_path / "track.wav"
    arguments = build_ffprobe_arguments(source)
    assert arguments[-1] == str(source)
    assert "-nostdin" not in arguments
    assert "-show_streams" not in arguments
    assert "-show_entries" in arguments
    entries = arguments[arguments.index("-show_entries") + 1]
    assert "format_name" in entries
    assert "codec_type" in entries
    assert "tags" not in entries


def test_command_uses_progress_pipe_and_temporary_output(tmp_path: Path) -> None:
    source = tmp_path / "movie.mkv"
    output = tmp_path / "movie-converted.mp4"
    job_id = uuid4()
    request = ProcessingRequest(job_id, source, output, 10.0, find_preset("mp4-balanced"))
    temporary = temporary_output_path(output, job_id)
    arguments = build_ffmpeg_arguments(request, temporary)
    assert arguments[-1] == str(temporary)
    assert arguments[arguments.index("-progress") + 1] == "pipe:1"
    assert "libx264" in arguments
    assert arguments[arguments.index("-map") + 1] == "0:v:0"
    assert "-ignore_unknown" in arguments
    assert "+genpts" in arguments
    assert "scale=trunc(iw/2)*2:trunc(ih/2)*2" in arguments
    assert arguments[arguments.index("-max_muxing_queue_size") + 1] == "4096"


def test_advanced_options_override_professional_preset(tmp_path: Path) -> None:
    source = tmp_path / "camera.mov"
    output = tmp_path / "camera-converted.mp4"
    job_id = uuid4()
    request = ProcessingRequest(
        job_id,
        source,
        output,
        10.0,
        find_preset("mp4-balanced"),
        ConversionOptions(
            audio_bitrate_kbps=320,
            audio_sample_rate_hz=44100,
            audio_channels=1,
            video_bitrate_kbps=8000,
            video_encoder_preset="slow",
            video_max_width=1920,
            normalize_audio=True,
            preserve_metadata=False,
        ),
    )
    arguments = build_ffmpeg_arguments(request, temporary_output_path(output, job_id))

    assert "-crf" not in arguments
    assert arguments[arguments.index("-b:v") + 1] == "8000k"
    assert arguments[arguments.index("-maxrate") + 1] == "8000k"
    assert arguments[arguments.index("-bufsize") + 1] == "16000k"
    assert arguments[arguments.index("-b:a") + 1] == "320k"
    assert arguments[arguments.index("-ar") + 1] == "44100"
    assert arguments[arguments.index("-ac") + 1] == "1"
    assert arguments[arguments.index("-preset") + 1] == "slow"
    assert arguments[arguments.index("-vf") + 1] == "scale=min(1920\\,iw):-2"
    assert arguments[arguments.index("-af") + 1].startswith("loudnorm=")
    assert arguments[arguments.index("-map_metadata") + 1] == "-1"


def test_lossless_output_ignores_lossy_audio_bitrate(tmp_path: Path) -> None:
    source = tmp_path / "track.wav"
    output = tmp_path / "track-converted.flac"
    job_id = uuid4()
    request = ProcessingRequest(
        job_id,
        source,
        output,
        10.0,
        find_preset("audio-flac"),
        ConversionOptions(audio_bitrate_kbps=320, audio_sample_rate_hz=96000),
    )
    arguments = build_ffmpeg_arguments(request, temporary_output_path(output, job_id))

    assert "320k" not in arguments
    assert arguments[arguments.index("-ar") + 1] == "96000"
