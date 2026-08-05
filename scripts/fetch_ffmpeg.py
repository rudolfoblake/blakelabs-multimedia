from __future__ import annotations

import argparse
import gzip
import hashlib
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
USER_AGENT = "BlakeLabs-Multimedia-Build"

# Runtime releases and digests are intentionally pinned. Do not replace these tags
# or hashes with "latest": release builds must be reproducible and auditable.
BTBN_REPOSITORY = "BtbN/FFmpeg-Builds"
BTBN_RELEASE_TAG = "autobuild-2025-10-31-13-40"
BTBN_BASE_URL = f"https://github.com/{BTBN_REPOSITORY}/releases/download/{BTBN_RELEASE_TAG}"

MACOS_REPOSITORY = "eugeneware/ffmpeg-static"
MACOS_RELEASE_TAG = "b6.1.1"
MACOS_BASE_URL = f"https://github.com/{MACOS_REPOSITORY}/releases/download/{MACOS_RELEASE_TAG}"

PINNED_SHA256: dict[tuple[str, str, str], str] = {
    (
        BTBN_REPOSITORY,
        BTBN_RELEASE_TAG,
        "ffmpeg-n8.0-30-g71007e6c12-win64-gpl-8.0.zip",
    ): "05ecc01bb03ef1f4d908c3c982512f07f888848429be6e9662a5a7c558c60b4f",
    (
        BTBN_REPOSITORY,
        BTBN_RELEASE_TAG,
        "ffmpeg-n8.0-30-g71007e6c12-linux64-gpl-8.0.tar.xz",
    ): "832449c3f81d0b92db2ee5a3ef5708298d57e238e9534991edcbcecce2e82d94",
    (
        MACOS_REPOSITORY,
        MACOS_RELEASE_TAG,
        "ffmpeg-darwin-arm64.gz",
    ): "8923876afa8db5585022d7860ec7e589af192f441c56793971276d450ed3bbfa",
    (
        MACOS_REPOSITORY,
        MACOS_RELEASE_TAG,
        "ffprobe-darwin-arm64.gz",
    ): "d986a8ec7b030899fe66a8a288ed809a3543338705a3ce178cfb85869c5d80be",
    (
        MACOS_REPOSITORY,
        MACOS_RELEASE_TAG,
        "ffmpeg-darwin-x64.gz",
    ): "929b375c1182d956c51f7ac25e0b2b0411fb01f6f407aa15c9758efeb4242106",
    (
        MACOS_REPOSITORY,
        MACOS_RELEASE_TAG,
        "ffprobe-darwin-x64.gz",
    ): "d4da574d6e2e197bd259b47d69cf262df9e312af24ad960444f6d806d3d4c186",
}


class UnsupportedPlatformError(RuntimeError):
    pass


class IntegrityError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class ArchiveRuntime:
    repository: str
    release_tag: str
    archive_name: str
    destination: Path
    executable_names: tuple[str, ...]

    @property
    def url(self) -> str:
        return (
            f"https://github.com/{self.repository}/releases/download/"
            f"{self.release_tag}/{self.archive_name}"
        )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Download pinned and integrity-verified FFmpeg runtime binaries."
    )
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
        expected_sha256 = pinned_asset_sha256(
            runtime.repository,
            runtime.release_tag,
            runtime.archive_name,
        )
        _download(runtime.url, archive)
        _verify_sha256(archive, expected_sha256)
        extraction = temporary / "extracted"
        extraction.mkdir()
        _extract_archive(archive, extraction)
        _copy_executables(extraction, runtime.destination, runtime.executable_names)


def archive_runtime(platform_name: str) -> ArchiveRuntime:
    if platform_name == "windows":
        return ArchiveRuntime(
            repository=BTBN_REPOSITORY,
            release_tag=BTBN_RELEASE_TAG,
            archive_name="ffmpeg-n8.0-30-g71007e6c12-win64-gpl-8.0.zip",
            destination=RESOURCE_ROOT / "windows-x64",
            executable_names=("ffmpeg.exe", "ffprobe.exe"),
        )
    if platform_name == "linux":
        return ArchiveRuntime(
            repository=BTBN_REPOSITORY,
            release_tag=BTBN_RELEASE_TAG,
            archive_name="ffmpeg-n8.0-30-g71007e6c12-linux64-gpl-8.0.tar.xz",
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


def pinned_asset_sha256(repository: str, release_tag: str, asset_name: str) -> str:
    key = (repository, release_tag, asset_name)
    try:
        return PINNED_SHA256[key]
    except KeyError as exc:
        raise IntegrityError(
            f"No pinned SHA-256 is configured for {repository}@{release_tag}/{asset_name}"
        ) from exc


def _install_macos_runtime(architecture: str) -> None:
    destination = RESOURCE_ROOT / f"macos-{architecture}"
    destination.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="blakelabs-ffmpeg-macos-") as temporary_directory:
        temporary = Path(temporary_directory)
        for executable_name in ("ffmpeg", "ffprobe"):
            asset_name = f"{executable_name}-darwin-{architecture}.gz"
            compressed = temporary / asset_name
            expected_sha256 = pinned_asset_sha256(
                MACOS_REPOSITORY,
                MACOS_RELEASE_TAG,
                asset_name,
            )
            _download(macos_binary_url(executable_name, architecture), compressed)
            _verify_sha256(compressed, expected_sha256)
            target = destination / executable_name
            with gzip.open(compressed, "rb") as source, target.open("wb") as output:
                shutil.copyfileobj(source, output)
            _make_executable(target)
            print(f"Installed {target.relative_to(ROOT)}")

        metadata_base = f"{MACOS_BASE_URL}/darwin-{architecture}"
        _download_optional(metadata_base + ".README", destination / "FFMPEG_BUILD_README.txt")
        _download_optional(metadata_base + ".LICENSE", destination / "FFMPEG_LICENSE.txt")


def _verify_sha256(path: Path, expected_sha256: str) -> None:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    actual_sha256 = digest.hexdigest()
    if actual_sha256 != expected_sha256.lower():
        raise IntegrityError(
            f"SHA-256 mismatch for {path.name}: expected {expected_sha256}, "
            f"received {actual_sha256}"
        )
    print(f"Verified SHA-256 for {path.name}: {actual_sha256}")


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
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
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
