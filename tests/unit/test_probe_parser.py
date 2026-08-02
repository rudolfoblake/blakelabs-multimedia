from pathlib import Path

import pytest

from blakelabs_multimedia.domain.media import MediaKind
from blakelabs_multimedia.infrastructure.ffmpeg.probe_parser import (
    InvalidProbeOutputError,
    parse_ffprobe_json,
)


def test_parse_video_metadata(tmp_path: Path) -> None:
    path = tmp_path / "sample.mp4"
    path.write_bytes(b"123")
    payload = """
    {
      "streams": [
        {"codec_type": "video", "codec_name": "h264", "width": 1920, "height": 1080},
        {"codec_type": "audio", "codec_name": "aac", "channels": 2, "sample_rate": "48000"}
      ],
      "format": {"format_name": "mov,mp4,m4a", "duration": "12.5", "size": "2048"}
    }
    """

    asset = parse_ffprobe_json(path, payload)

    assert asset.kind is MediaKind.VIDEO
    assert asset.duration_seconds == 12.5
    assert asset.width == 1920
    assert asset.audio_codec == "aac"
    assert asset.size_bytes == 2048


def test_parse_audio_metadata(tmp_path: Path) -> None:
    path = tmp_path / "sample.flac"
    path.write_bytes(b"123")
    payload = """
    {
      "streams": [{"codec_type": "audio", "codec_name": "flac", "channels": 2}],
      "format": {"format_name": "flac", "duration": "4.0"}
    }
    """

    asset = parse_ffprobe_json(path, payload)

    assert asset.kind is MediaKind.AUDIO
    assert asset.video_codec is None
    assert asset.size_bytes == 3


def test_invalid_json_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(InvalidProbeOutputError):
        parse_ffprobe_json(tmp_path / "broken", "not-json")
