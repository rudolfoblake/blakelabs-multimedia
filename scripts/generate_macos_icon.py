from __future__ import annotations

import argparse
from pathlib import Path

from scripts.generate_msix_assets import render_logo


def generate_macos_icon(output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    render_logo(1024, 1024).save(output, optimize=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate the Blake Labs macOS app icon.")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    generate_macos_icon(args.output)
    print(f"Generated macOS icon at {args.output}")


if __name__ == "__main__":
    main()
