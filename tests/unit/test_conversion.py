from pathlib import Path
from uuid import uuid4

from blakelabs_multimedia.domain.conversion import ProcessingRequest, find_preset
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


def test_probe_command_is_bounded_and_non_interactive(tmp_path: Path) -> None:
    source = tmp_path / "track.wav"
    arguments = build_ffprobe_arguments(source)
    assert arguments[-1] == str(source)
    assert "-nostdin" in arguments
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
