from __future__ import annotations

import argparse
from collections.abc import Iterable
from pathlib import Path

from PIL import Image, ImageDraw

BACKGROUND = (7, 10, 11, 255)
SURFACE = (13, 18, 19, 255)
BORDER = (43, 57, 62, 255)
WHITE = (244, 247, 248, 255)
ACCENT = (34, 211, 238, 255)
EYE_HIGHLIGHT = (221, 251, 255, 255)

Point = tuple[float, float]


def render_logo(width: int, height: int) -> Image.Image:
    scale = 4
    canvas_width = width * scale
    canvas_height = height * scale
    canvas = Image.new("RGBA", (canvas_width, canvas_height), (0, 0, 0, 0))
    drawing = ImageDraw.Draw(canvas)

    side = min(canvas_width, canvas_height)
    left = (canvas_width - side) // 2
    top = (canvas_height - side) // 2
    margin = round(side * 0.045)
    radius = round(side * 0.21)
    bounds = (left + margin, top + margin, left + side - margin, top + side - margin)
    drawing.rounded_rectangle(
        bounds,
        radius=radius,
        fill=BACKGROUND,
        outline=BORDER,
        width=max(1, side // 180),
    )

    inset = round(side * 0.18)
    mark_left = left + inset
    mark_top = top + inset
    mark_size = side - inset * 2
    _draw_alien(drawing, mark_left, mark_top, mark_size)

    return canvas.resize((width, height), Image.Resampling.LANCZOS)


def _draw_alien(drawing: ImageDraw.ImageDraw, left: int, top: int, size: int) -> None:
    def point(x: float, y: float) -> Point:
        return (left + size * x / 100, top + size * y / 100)

    head_segments = (
        ((50, 7), (28, 8), (14, 20), (10, 40)),
        ((10, 40), (6, 61), (18, 81), (37, 91)),
        ((37, 91), (45, 96), (55, 96), (63, 91)),
        ((63, 91), (82, 81), (94, 61), (90, 40)),
        ((90, 40), (86, 20), (72, 8), (50, 7)),
    )
    head_points: list[Point] = []
    for segment in head_segments:
        sampled = list(_sample_cubic(*(point(*coordinates) for coordinates in segment), steps=22))
        if head_points:
            sampled = sampled[1:]
        head_points.extend(sampled)

    stroke_width = max(2, round(size * 0.055))
    drawing.line(head_points, fill=WHITE, width=stroke_width, joint="curve")

    left_eye = [point(21, 39), point(44, 33), point(39, 48), point(25, 47)]
    right_eye = [point(79, 39), point(56, 33), point(61, 48), point(75, 47)]
    drawing.polygon(left_eye, fill=ACCENT)
    drawing.polygon(right_eye, fill=ACCENT)

    highlight_radius = max(1, round(size * 0.024))
    for center in (point(31, 38), point(69, 38)):
        drawing.ellipse(
            (
                center[0] - highlight_radius,
                center[1] - highlight_radius,
                center[0] + highlight_radius,
                center[1] + highlight_radius,
            ),
            fill=EYE_HIGHLIGHT,
        )

    monogram_width = max(2, round(size * 0.052))
    drawing.line((point(36, 58), point(36, 79)), fill=WHITE, width=monogram_width)
    drawing.arc(
        (point(34, 56)[0], point(55, 56)[1], point(54, 69)[0], point(54, 69)[1]),
        start=270,
        end=90,
        fill=WHITE,
        width=monogram_width,
    )
    drawing.arc(
        (point(34, 66)[0], point(55, 66)[1], point(56, 81)[0], point(56, 81)[1]),
        start=270,
        end=90,
        fill=WHITE,
        width=monogram_width,
    )
    drawing.line(
        (point(57, 58), point(57, 78), point(72, 78)),
        fill=WHITE,
        width=monogram_width,
        joint="curve",
    )


def _sample_cubic(
    start: Point,
    control_one: Point,
    control_two: Point,
    end: Point,
    *,
    steps: int,
) -> Iterable[Point]:
    for index in range(steps + 1):
        t = index / steps
        inverse = 1 - t
        yield (
            inverse**3 * start[0]
            + 3 * inverse**2 * t * control_one[0]
            + 3 * inverse * t**2 * control_two[0]
            + t**3 * end[0],
            inverse**3 * start[1]
            + 3 * inverse**2 * t * control_one[1]
            + 3 * inverse * t**2 * control_two[1]
            + t**3 * end[1],
        )


def generate_assets(output_directory: Path) -> None:
    output_directory.mkdir(parents=True, exist_ok=True)
    sizes = {
        "StoreLogo.png": (50, 50),
        "Square44x44Logo.png": (44, 44),
        "Square150x150Logo.png": (150, 150),
        "Square310x310Logo.png": (310, 310),
        "Wide310x150Logo.png": (310, 150),
    }
    for name, size in sizes.items():
        render_logo(*size).save(output_directory / name, optimize=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Blake Labs alien MSIX assets.")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    generate_assets(args.output)
    print(f"Generated MSIX assets at {args.output}")


if __name__ == "__main__":
    main()
