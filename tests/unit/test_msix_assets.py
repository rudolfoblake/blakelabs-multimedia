from pathlib import Path

from PIL import Image

from scripts.generate_msix_assets import generate_assets


def test_generate_msix_assets_creates_required_dimensions(tmp_path: Path) -> None:
    generate_assets(tmp_path)

    expected = {
        "StoreLogo.png": (50, 50),
        "Square44x44Logo.png": (44, 44),
        "Square150x150Logo.png": (150, 150),
    }
    for name, dimensions in expected.items():
        with Image.open(tmp_path / name) as image:
            assert image.size == dimensions
            assert image.mode == "RGBA"
