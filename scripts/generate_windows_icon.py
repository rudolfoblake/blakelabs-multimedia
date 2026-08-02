from __future__ import annotations

import argparse
from pathlib import Path

from scripts.generate_msix_assets import render_logo


def generate_windows_icon(output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    source = render_logo(1024, 1024)
    source.save(
        output,
        format="ICO",
        sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)],
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate the Blake Labs alien Windows icon.")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    generate_windows_icon(args.output)
    print(f"Generated Windows icon at {args.output}")


if __name__ == "__main__":
    main()
