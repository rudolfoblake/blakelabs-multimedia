#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

uv sync --group build
uv run python scripts/fetch_ffmpeg.py --platform linux

BUILD_ROOT="$ROOT/build/linux"
RUNTIME_ROOT="$ROOT/src/blakelabs_multimedia/resources/bin/linux-x64"
FFMPEG="$RUNTIME_ROOT/ffmpeg"
FFPROBE="$RUNTIME_ROOT/ffprobe"

for binary in "$FFMPEG" "$FFPROBE"; do
  if [[ ! -x "$binary" ]]; then
    printf 'Required FFmpeg runtime was not downloaded or is not executable: %s\n' "$binary" >&2
    exit 1
  fi
done

rm -rf "$BUILD_ROOT"
mkdir -p "$BUILD_ROOT"

uv run python -m nuitka \
  --standalone \
  --assume-yes-for-downloads \
  --enable-plugin=pyside6 \
  --include-qt-plugins=qml \
  --include-data-dir=src/blakelabs_multimedia/presentation/qml=blakelabs_multimedia/presentation/qml \
  --include-data-dir=src/blakelabs_multimedia/resources=blakelabs_multimedia/resources \
  --include-data-files="$FFMPEG=blakelabs_multimedia/resources/bin/linux-x64/ffmpeg" \
  --include-data-files="$FFPROBE=blakelabs_multimedia/resources/bin/linux-x64/ffprobe" \
  --output-filename=blakelabs-multimedia \
  --output-dir="$BUILD_ROOT" \
  src/blakelabs_multimedia/__main__.py

GENERATED="$BUILD_ROOT/__main__.dist"
PRODUCT="$BUILD_ROOT/BlakeLabsMultimedia"
test -d "$GENERATED"
mv "$GENERATED" "$PRODUCT"

PACKAGED_RUNTIME="$PRODUCT/blakelabs_multimedia/resources/bin/linux-x64"
for binary in "$PACKAGED_RUNTIME/ffmpeg" "$PACKAGED_RUNTIME/ffprobe"; do
  if [[ ! -f "$binary" ]]; then
    printf 'Required FFmpeg runtime is missing from packaged application: %s\n' "$binary" >&2
    exit 1
  fi
  chmod +x "$binary"
done

"$PACKAGED_RUNTIME/ffprobe" -hide_banner -version | head -n 1
"$PACKAGED_RUNTIME/ffmpeg" -hide_banner -version | head -n 1

tar -C "$BUILD_ROOT" -czf "$BUILD_ROOT/BlakeLabsMultimedia-linux-x64.tar.gz" BlakeLabsMultimedia
printf 'Linux bundle with bundled FFmpeg runtime: %s\n' "$BUILD_ROOT/BlakeLabsMultimedia-linux-x64.tar.gz"
