from pathlib import Path

import pytest
from scripts.prepare_release_assets import (
    EXPECTED_RELEASE_ASSETS,
    ReleaseAssetError,
    prepare_release_assets,
)


def _write_expected_assets(source: Path) -> None:
    paths = {
        "BlakeLabsMultimedia-Setup-x64.exe": source / "installer",
        "BlakeLabsMultimedia-Store-x64.msix": source / "msix",
        "BlakeLabsMultimedia-linux-x64.tar.gz": source / "linux",
        "BlakeLabsMultimedia-macos-arm64.dmg": source / "macos-arm64",
        "BlakeLabsMultimedia-macos-x64.dmg": source / "macos-x64",
    }
    for name, directory in paths.items():
        directory.mkdir(parents=True, exist_ok=True)
        (directory / name).write_bytes(name.encode())


def test_prepare_release_assets_flattens_and_hashes_files(tmp_path: Path) -> None:
    source = tmp_path / "downloaded"
    destination = tmp_path / "upload"
    _write_expected_assets(source)

    digests = prepare_release_assets(source, destination)

    assert frozenset(digests) == EXPECTED_RELEASE_ASSETS
    assert {path.name for path in destination.iterdir()} == EXPECTED_RELEASE_ASSETS
    assert all(len(digest) == 64 for digest in digests.values())


def test_prepare_release_assets_rejects_missing_asset(tmp_path: Path) -> None:
    source = tmp_path / "downloaded"
    source.mkdir()
    (source / "BlakeLabsMultimedia-Setup-x64.exe").write_bytes(b"installer")

    with pytest.raises(ReleaseAssetError, match="missing"):
        prepare_release_assets(source, tmp_path / "upload")


def test_prepare_release_assets_rejects_duplicate_basenames(tmp_path: Path) -> None:
    source = tmp_path / "downloaded"
    _write_expected_assets(source)
    duplicate = source / "duplicate"
    duplicate.mkdir()
    (duplicate / "BlakeLabsMultimedia-Store-x64.msix").write_bytes(b"duplicate")

    with pytest.raises(ReleaseAssetError, match="Duplicate"):
        prepare_release_assets(source, tmp_path / "upload")
