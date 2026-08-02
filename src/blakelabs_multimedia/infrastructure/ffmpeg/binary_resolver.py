from __future__ import annotations

import os
import shutil
import sys
from importlib.resources import files
from pathlib import Path


class BinaryNotFoundError(RuntimeError):
    """Raised when an FFmpeg-family executable cannot be resolved."""


class FfmpegBinaryResolver:
    """Resolve bundled, explicitly configured or system FFmpeg binaries."""

    def ffprobe(self) -> Path:
        return self._resolve("ffprobe", "BLAKELABS_FFPROBE")

    def ffmpeg(self) -> Path:
        return self._resolve("ffmpeg", "BLAKELABS_FFMPEG")

    def _resolve(self, binary_name: str, environment_key: str) -> Path:
        configured = os.getenv(environment_key)
        if configured:
            candidate = Path(configured).expanduser()
            if candidate.is_file():
                return candidate.resolve()
            raise BinaryNotFoundError(f"{environment_key} points to a missing file: {candidate}")

        executable_name = f"{binary_name}.exe" if sys.platform == "win32" else binary_name
        platform_name = "windows-x64" if sys.platform == "win32" else "linux-x64"
        packaged = files("blakelabs_multimedia").joinpath(
            "resources", "bin", platform_name, executable_name
        )
        if packaged.is_file():
            return Path(str(packaged))

        system_binary = shutil.which(binary_name)
        if system_binary:
            return Path(system_binary).resolve()

        raise BinaryNotFoundError(
            f"{binary_name} was not found. Install FFmpeg or set {environment_key}."
        )
