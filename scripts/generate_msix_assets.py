from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw

BACKGROUND = (11, 15, 13, 255)
ACCENT = (124, 255, 143, 255)


def render_logo(width: int, height: int) -> Image.Image:
    scale = 4
    canvas_width = width * scale
    canvas_height = height * scale
    canvas = Image.new("RGBA", (canvas_width, canvas_height), (0, 0, 0, 0))
    drawing = ImageDraw.Draw(canvas)

    margin = round(min(canvas_width, canvas_height) * 0.06)
    radius = round(min(canvas_width, canvas_height) * 0.22)
    drawing.rounded_rectangle(
        (margin, margin, canvas_width - margin, canvas_height - margin),
        radius=radius,
        fill=BACKGROUND,
    )

    mark_x = round(canvas_width * 0.28)
    mark_y = round(canvas_height * 0.20)
    mark_width = round(canvas_width * 0.44)
    mark_height = round(canvas_height * 0.60)
    stem_width = round(mark_width * 0.22)
    drawing.rounded_rectangle(
        (mark_x, mark_y, mark_x + stem_width, mark_y + mark_height),
        radius=max(1, stem_width // 2),
        fill=ACCENT,
    )

    lobe_width = round(mark_width * 0.72)
    lobe_height = round(mark_height * 0.44)
    for lobe_y in (mark_y, mark_y + mark_height - lobe_height):
        drawing.rounded_rectangle(
            (
                mark_x + round(stem_width * 0.55),
                lobe_y,
                mark_x + round(stem_width * 0.55) + lobe_width,
                lobe_y + lobe_height,
            ),
            radius=max(1, lobe_height // 2),
            fill=ACCENT,
        )
        drawing.rectangle(
            (
                mark_x + round(stem_width * 0.55),
                lobe_y,
                mark_x + stem_width,
                lobe_y + lobe_height,
            ),
            fill=ACCENT,
        )

    return canvas.resize((width, height), Image.Resampling.LANCZOS)


def generate_assets(output_directory: Path) -> None:
    output_directory.mkdir(parents=True, exist_ok=True)
    sizes = {
        "StoreLogo.png": (50, 50),
        "Square44x44Logo.png": (44, 44),
        "Square150x150Logo.png": (150, 150),
    }
    for name, size in sizes.items():
        render_logo(*size).save(output_directory / name, optimize=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Blake Labs MSIX logo assets.")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    generate_assets(args.output)
    print(f"Generated MSIX assets at {args.output}")


if __name__ == "__main__":
    main()
