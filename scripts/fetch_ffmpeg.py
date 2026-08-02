from __future__ import annotations

import argparse
import shutil
import stat
import tarfile
import tempfile
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESOURCE_ROOT = ROOT / "src" / "blakelabs_multimedia" / "resources" / "bin"
BASE_URL = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest"


class UnsupportedPlatformError(RuntimeError):
    pass


def main() -> None:
    parser = argparse.ArgumentParser(description="Download reproducible FFmpeg runtime binaries.")
    parser.add_argument("--platform", choices=("windows", "linux"), required=True)
    args = parser.parse_args()
    install_ffmpeg(args.platform)


def install_ffmpeg(platform_name: str) -> None:
    if platform_name == "windows":
        archive_name = "ffmpeg-master-latest-win64-gpl.zip"
        destination = RESOURCE_ROOT / "windows-x64"
        executable_names = ("ffmpeg.exe", "ffprobe.exe")
    elif platform_name == "linux":
        archive_name = "ffmpeg-master-latest-linux64-gpl.tar.xz"
        destination = RESOURCE_ROOT / "linux-x64"
        executable_names = ("ffmpeg", "ffprobe")
    else:
        raise UnsupportedPlatformError(platform_name)

    destination.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="blakelabs-ffmpeg-") as temporary_directory:
        temporary = Path(temporary_directory)
        archive = temporary / archive_name
        _download(f"{BASE_URL}/{archive_name}", archive)
        extraction = temporary / "extracted"
        extraction.mkdir()
        if archive.suffix == ".zip":
            with zipfile.ZipFile(archive) as bundle:
                bundle.extractall(extraction)
        else:
            with tarfile.open(archive) as bundle:
                bundle.extractall(extraction, filter="data")

        for executable_name in executable_names:
            matches = list(extraction.rglob(executable_name))
            if not matches:
                raise FileNotFoundError(f"{executable_name} was not present in {archive_name}")
            target = destination / executable_name
            shutil.copy2(matches[0], target)
            target.chmod(target.stat().st_mode | stat.S_IEXEC)
            print(f"Installed {target.relative_to(ROOT)}")


def _download(url: str, destination: Path) -> None:
    request = urllib.request.Request(url, headers={"User-Agent": "BlakeLabs-Multimedia-Build"})
    with urllib.request.urlopen(request, timeout=120) as response:
        with destination.open("wb") as output:
            shutil.copyfileobj(response, output)


if __name__ == "__main__":
    main()
