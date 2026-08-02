from pathlib import Path

from blakelabs_multimedia.domain.media import MediaAsset, MediaKind


def test_media_asset_exposes_filename() -> None:
    asset = MediaAsset(
        path=Path("/tmp/demo.mp4"),
        kind=MediaKind.VIDEO,
        container="mov,mp4",
        size_bytes=42,
    )

    assert asset.filename == "demo.mp4"
