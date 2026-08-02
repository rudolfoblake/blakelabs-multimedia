from pathlib import Path

import pytest
from PIL import Image
from scripts.fetch_ffmpeg import (
    UnsupportedPlatformError,
    macos_binary_url,
    normalize_macos_architecture,
)
from scripts.generate_macos_icon import generate_macos_icon

from blakelabs_multimedia.infrastructure.ffmpeg.binary_resolver import packaged_platform_name


def test_macos_architecture_normalization() -> None:
    assert normalize_macos_architecture("arm64") == "arm64"
    assert normalize_macos_architecture("aarch64") == "arm64"
    assert normalize_macos_architecture("x86_64") == "x64"
    assert normalize_macos_architecture("amd64") == "x64"


def test_macos_architecture_rejects_unknown_values() -> None:
    with pytest.raises(UnsupportedPlatformError):
        normalize_macos_architecture("powerpc")


def test_macos_binary_urls_are_architecture_specific() -> None:
    assert macos_binary_url("ffmpeg", "arm64").endswith("/ffmpeg-darwin-arm64.gz")
    assert macos_binary_url("ffprobe", "x64").endswith("/ffprobe-darwin-x64.gz")


def test_packaged_platform_names_cover_both_mac_architectures() -> None:
    assert packaged_platform_name("darwin", "arm64") == "macos-arm64"
    assert packaged_platform_name("darwin", "x86_64") == "macos-x64"
    assert packaged_platform_name("darwin", "powerpc") is None


def test_macos_icon_is_generated_at_store_quality(tmp_path: Path) -> None:
    output = tmp_path / "BlakeLabsMultimedia.png"
    generate_macos_icon(output)

    with Image.open(output) as image:
        assert image.size == (1024, 1024)
        assert image.mode == "RGBA"
