import pytest
from scripts.fetch_ffmpeg import (
    BTBN_RELEASE_TAG,
    BTBN_REPOSITORY,
    MACOS_RELEASE_TAG,
    MACOS_REPOSITORY,
    IntegrityError,
    pinned_asset_sha256,
)


@pytest.mark.parametrize(
    ("repository", "release_tag", "asset_name", "expected_sha256"),
    (
        (
            BTBN_REPOSITORY,
            BTBN_RELEASE_TAG,
            "ffmpeg-n8.0-30-g71007e6c12-win64-gpl-8.0.zip",
            "05ecc01bb03ef1f4d908c3c982512f07f888848429be6e9662a5a7c558c60b4f",
        ),
        (
            BTBN_REPOSITORY,
            BTBN_RELEASE_TAG,
            "ffmpeg-n8.0-30-g71007e6c12-linux64-gpl-8.0.tar.xz",
            "832449c3f81d0b92db2ee5a3ef5708298d57e238e9534991edcbcecce2e82d94",
        ),
        (
            MACOS_REPOSITORY,
            MACOS_RELEASE_TAG,
            "ffmpeg-darwin-arm64.gz",
            "8923876afa8db5585022d7860ec7e589af192f441c56793971276d450ed3bbfa",
        ),
        (
            MACOS_REPOSITORY,
            MACOS_RELEASE_TAG,
            "ffprobe-darwin-arm64.gz",
            "d986a8ec7b030899fe66a8a288ed809a3543338705a3ce178cfb85869c5d80be",
        ),
        (
            MACOS_REPOSITORY,
            MACOS_RELEASE_TAG,
            "ffmpeg-darwin-x64.gz",
            "929b375c1182d956c51f7ac25e0b2b0411fb01f6f407aa15c9758efeb4242106",
        ),
        (
            MACOS_REPOSITORY,
            MACOS_RELEASE_TAG,
            "ffprobe-darwin-x64.gz",
            "d4da574d6e2e197bd259b47d69cf262df9e312af24ad960444f6d806d3d4c186",
        ),
    ),
)
def test_pinned_ffmpeg_assets_have_expected_digests(
    repository: str,
    release_tag: str,
    asset_name: str,
    expected_sha256: str,
) -> None:
    assert pinned_asset_sha256(repository, release_tag, asset_name) == expected_sha256


def test_unpinned_ffmpeg_asset_is_rejected() -> None:
    with pytest.raises(IntegrityError, match="No pinned SHA-256"):
        pinned_asset_sha256(MACOS_REPOSITORY, MACOS_RELEASE_TAG, "unexpected-runtime.gz")
