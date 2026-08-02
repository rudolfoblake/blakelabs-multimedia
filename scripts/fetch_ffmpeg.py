from __future__ import annotations

import argparse
import gzip
import platform
import shutil
import stat
import tarfile
import tempfile
import urllib.error
import urllib.request
import zipfile
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESOURCE_ROOT = ROOT / "src" / "blakelabs_multimedia" / "resources" / "bin"
BTBN_BASE_URL = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest"
MACOS_RELEASE_TAG = "b6.1.1"
MACOS_BASE_URL = (
    f"https://github.com/eugeneware/ffmpeg-static/releases/download/{MACOS_RELEASE_TAG}"
)


class UnsupportedPlatformError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class ArchiveRuntime:
    archive_name: str
    destination: Path
    executable_names: tuple[str, ...]

    @property
    def url(self) -> str:
        return f"{BTBN_BASE_URL}/{self.archive_name}"


def main() -> None:
    parser = argparse.ArgumentParser(description="Download reproducible FFmpeg runtime binaries.")
    parser.add_argument("--platform", choices=("windows", "linux", "macos"), required=True)
    parser.add_argument("--arch", choices=("x64", "arm64"))
    args = parser.parse_args()
    install_ffmpeg(args.platform, args.arch)


def install_ffmpeg(platform_name: str, architecture: str | None = None) -> None:
    if platform_name == "macos":
        _install_macos_runtime(normalize_macos_architecture(architecture))
        return

    runtime = archive_runtime(platform_name)
    runtime.destination.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="blakelabs-ffmpeg-") as temporary_directory:
        temporary = Path(temporary_directory)
        archive = temporary / runtime.archive_name
        _download(runtime.url, archive)
        extraction = temporary / "extracted"
        extraction.mkdir()
        _extract_archive(archive, extraction)
        _copy_executables(extraction, runtime.destination, runtime.executable_names)


def archive_runtime(platform_name: str) -> ArchiveRuntime:
    if platform_name == "windows":
        return ArchiveRuntime(
            archive_name="ffmpeg-master-latest-win64-gpl.zip",
            destination=RESOURCE_ROOT / "windows-x64",
            executable_names=("ffmpeg.exe", "ffprobe.exe"),
        )
    if platform_name == "linux":
        return ArchiveRuntime(
            archive_name="ffmpeg-master-latest-linux64-gpl.tar.xz",
            destination=RESOURCE_ROOT / "linux-x64",
            executable_names=("ffmpeg", "ffprobe"),
        )
    raise UnsupportedPlatformError(platform_name)


def normalize_macos_architecture(architecture: str | None) -> str:
    raw = architecture or platform.machine()
    normalized = raw.lower().replace("_", "-")
    if normalized in {"arm64", "aarch64"}:
        return "arm64"
    if normalized in {"x64", "x86-64", "amd64"}:
        return "x64"
    raise UnsupportedPlatformError(f"Unsupported macOS architecture: {raw}")


def macos_binary_url(executable_name: str, architecture: str) -> str:
    if executable_name not in {"ffmpeg", "ffprobe"}:
        raise ValueError(f"Unsupported FFmpeg executable: {executable_name}")
    normalized_architecture = normalize_macos_architecture(architecture)
    return f"{MACOS_BASE_URL}/{executable_name}-darwin-{normalized_architecture}.gz"


def _install_macos_runtime(architecture: str) -> None:
    destination = RESOURCE_ROOT / f"macos-{architecture}"
    destination.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="blakelabs-ffmpeg-macos-") as temporary_directory:
        temporary = Path(temporary_directory)
        for executable_name in ("ffmpeg", "ffprobe"):
            compressed = temporary / f"{executable_name}.gz"
            _download(macos_binary_url(executable_name, architecture), compressed)
            target = destination / executable_name
            with gzip.open(compressed, "rb") as source, target.open("wb") as output:
                shutil.copyfileobj(source, output)
            _make_executable(target)
            print(f"Installed {target.relative_to(ROOT)}")

        metadata_base = f"{MACOS_BASE_URL}/darwin-{architecture}"
        _download_optional(metadata_base + ".README", destination / "FFMPEG_BUILD_README.txt")
        _download_optional(metadata_base + ".LICENSE", destination / "FFMPEG_LICENSE.txt")


def _extract_archive(archive: Path, extraction: Path) -> None:
    if archive.suffix == ".zip":
        with zipfile.ZipFile(archive) as bundle:
            bundle.extractall(extraction)
        return
    with tarfile.open(archive) as bundle:
        bundle.extractall(extraction, filter="data")


def _copy_executables(
    extraction: Path,
    destination: Path,
    executable_names: tuple[str, ...],
) -> None:
    for executable_name in executable_names:
        matches = list(extraction.rglob(executable_name))
        if not matches:
            raise FileNotFoundError(
                f"{executable_name} was not present in downloaded FFmpeg archive"
            )
        target = destination / executable_name
        shutil.copy2(matches[0], target)
        _make_executable(target)
        print(f"Installed {target.relative_to(ROOT)}")


def _make_executable(path: Path) -> None:
    path.chmod(path.stat().st_mode | stat.S_IEXEC)


def _download(url: str, destination: Path) -> None:
    request = urllib.request.Request(url, headers={"User-Agent": "BlakeLabs-Multimedia-Build"})
    with (
        urllib.request.urlopen(request, timeout=120) as response,
        destination.open("wb") as output,
    ):
        shutil.copyfileobj(response, output)


def _download_optional(url: str, destination: Path) -> None:
    try:
        _download(url, destination)
    except urllib.error.HTTPError as exc:
        if exc.code != 404:
            raise
        print(f"Optional metadata was not available: {url}")


if __name__ == "__main__":
    main()
