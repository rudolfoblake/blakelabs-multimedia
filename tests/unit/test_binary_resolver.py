from pathlib import Path

import pytest

from blakelabs_multimedia.infrastructure.ffmpeg import binary_resolver
from blakelabs_multimedia.infrastructure.ffmpeg.binary_resolver import FfmpegBinaryResolver


def test_resolves_binary_bundled_next_to_packaged_executable(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    packaged_executable = tmp_path / "BlakeLabsMultimedia.exe"
    packaged_executable.touch()
    bundled_ffprobe = (
        tmp_path / "blakelabs_multimedia" / "resources" / "bin" / "windows-x64" / "ffprobe.exe"
    )
    bundled_ffprobe.parent.mkdir(parents=True)
    bundled_ffprobe.touch()

    monkeypatch.delenv("BLAKELABS_FFPROBE", raising=False)
    monkeypatch.setattr(binary_resolver.sys, "executable", str(packaged_executable))
    monkeypatch.setattr(binary_resolver.sys, "platform", "win32")
    monkeypatch.setattr(binary_resolver.platform, "machine", lambda: "AMD64")
    monkeypatch.setattr(binary_resolver.shutil, "which", lambda _binary_name: None)

    assert FfmpegBinaryResolver().ffprobe() == bundled_ffprobe.resolve()


def test_explicit_binary_override_still_has_priority(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    configured_ffmpeg = tmp_path / "custom-ffmpeg"
    configured_ffmpeg.touch()
    monkeypatch.setenv("BLAKELABS_FFMPEG", str(configured_ffmpeg))

    assert FfmpegBinaryResolver().ffmpeg() == configured_ffmpeg.resolve()
