#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

requested_arch="${1:-$(uname -m)}"
case "${requested_arch}" in
  arm64|aarch64)
    arch="arm64"
    ;;
  x64|x86_64|amd64)
    arch="x64"
    ;;
  *)
    printf 'Unsupported macOS architecture: %s\n' "$requested_arch" >&2
    exit 1
    ;;
esac

machine="$(uname -m)"
if [[ "$arch" == "arm64" && "$machine" != "arm64" ]]; then
  printf 'arm64 package requires an Apple Silicon runner, got %s.\n' "$machine" >&2
  exit 1
fi
if [[ "$arch" == "x64" && "$machine" != "x86_64" ]]; then
  printf 'x64 package requires an Intel runner, got %s.\n' "$machine" >&2
  exit 1
fi

# GitHub's Intel runner has Xcode installed, but its compiler directory is not always present on
# PATH. Resolve the selected Xcode toolchain explicitly so Nuitka can locate clang consistently.
developer_dir="$(xcode-select -p)"
toolchain_bin="$developer_dir/Toolchains/XcodeDefault.xctoolchain/usr/bin"
if [[ ! -x "$toolchain_bin/clang" ]]; then
  clang_path="$(xcrun --find clang)"
  toolchain_bin="$(dirname "$clang_path")"
fi
if [[ ! -x "$toolchain_bin/clang" ]]; then
  printf 'Unable to locate clang in the selected Xcode toolchain.\n' >&2
  exit 1
fi
export DEVELOPER_DIR="$developer_dir"
export PATH="$toolchain_bin:$PATH"
export CC="$toolchain_bin/clang"
export CXX="$toolchain_bin/clang++"
"$CC" --version

version="$(python3 - <<'PY'
import tomllib
from pathlib import Path

project = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))
print(project["project"]["version"])
PY
)"

uv sync --group build
uv run python scripts/fetch_ffmpeg.py --platform macos --arch "$arch"

build_root="$ROOT/build/macos/$arch"
icon="$build_root/BlakeLabsMultimedia.png"
rm -rf "$build_root"
mkdir -p "$build_root"
uv run python -m scripts.generate_macos_icon --output "$icon"

uv run python -m nuitka \
  --mode=app \
  --assume-yes-for-downloads \
  --enable-plugin=pyside6 \
  --include-qt-plugins=qml \
  --include-data-dir=src/blakelabs_multimedia/presentation/qml=blakelabs_multimedia/presentation/qml \
  --include-data-dir=src/blakelabs_multimedia/resources=blakelabs_multimedia/resources \
  --macos-app-icon="$icon" \
  --company-name="Blake Labs" \
  --product-name="BlakeLabs Multimedia" \
  --file-version="$version.0" \
  --product-version="$version.0" \
  --output-filename=BlakeLabsMultimedia \
  --output-dir="$build_root" \
  src/blakelabs_multimedia/__main__.py

source_app="$(find "$build_root" -maxdepth 1 -type d -name '*.app' -print -quit)"
if [[ -z "$source_app" ]]; then
  printf 'Nuitka did not create a macOS application bundle.\n' >&2
  find "$build_root" -maxdepth 2 -print >&2
  exit 1
fi

product_app="$build_root/BlakeLabs Multimedia.app"
if [[ "$source_app" != "$product_app" ]]; then
  rm -rf "$product_app"
  mv "$source_app" "$product_app"
fi

plist="$product_app/Contents/Info.plist"
set_plist_value() {
  local key="$1"
  local type="$2"
  local value="$3"
  /usr/libexec/PlistBuddy -c "Set :$key $value" "$plist" >/dev/null 2>&1 || \
    /usr/libexec/PlistBuddy -c "Add :$key $type $value" "$plist"
}

set_plist_value CFBundleIdentifier string com.blakelabs.multimedia
set_plist_value CFBundleDisplayName string "BlakeLabs Multimedia"
set_plist_value CFBundleName string "BlakeLabs Multimedia"
set_plist_value CFBundleShortVersionString string "$version"
set_plist_value CFBundleVersion string "$version"
set_plist_value NSHighResolutionCapable bool true
set_plist_value NSHumanReadableCopyright string "Copyright © 2026 Blake Labs"

# Ad-hoc signing validates bundle integrity for CI and local testing. Public direct distribution
# still requires a Developer ID certificate and Apple notarization.
codesign --force --deep --sign - "$product_app"
codesign --verify --deep --strict --verbose=2 "$product_app"

executable="$(/usr/libexec/PlistBuddy -c 'Print :CFBundleExecutable' "$plist")"
QT_QPA_PLATFORM=offscreen BLAKELABS_SMOKE_EXIT_MS=400 \
  "$product_app/Contents/MacOS/$executable"

release_root="$ROOT/build/macos"
dmg_root="$build_root/dmg-root"
dmg="$release_root/BlakeLabsMultimedia-macos-$arch.dmg"
rm -rf "$dmg_root" "$dmg"
mkdir -p "$dmg_root"
cp -R "$product_app" "$dmg_root/"
ln -s /Applications "$dmg_root/Applications"
hdiutil create \
  -volname "BlakeLabs Multimedia" \
  -srcfolder "$dmg_root" \
  -ov \
  -format UDZO \
  "$dmg"

printf 'macOS %s application: %s\n' "$arch" "$product_app"
printf 'macOS %s disk image: %s\n' "$arch" "$dmg"
