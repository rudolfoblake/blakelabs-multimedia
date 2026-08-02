#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

uv sync --group build
uv run python scripts/fetch_ffmpeg.py --platform linux

BUILD_ROOT="$ROOT/build/linux"
rm -rf "$BUILD_ROOT"
mkdir -p "$BUILD_ROOT"

uv run python -m nuitka \
  --standalone \
  --assume-yes-for-downloads \
  --enable-plugin=pyside6 \
  --include-package=blakelabs_multimedia \
  --include-data-dir=src/blakelabs_multimedia/presentation/qml=blakelabs_multimedia/presentation/qml \
  --include-data-dir=src/blakelabs_multimedia/resources=blakelabs_multimedia/resources \
  --output-filename=blakelabs-multimedia \
  --output-dir="$BUILD_ROOT" \
  src/blakelabs_multimedia/__main__.py

mv "$BUILD_ROOT/__main__.dist" "$BUILD_ROOT/BlakeLabsMultimedia"
tar -C "$BUILD_ROOT" -czf "$BUILD_ROOT/BlakeLabsMultimedia-linux-x64.tar.gz" BlakeLabsMultimedia
printf 'Linux bundle: %s\n' "$BUILD_ROOT/BlakeLabsMultimedia-linux-x64.tar.gz"
