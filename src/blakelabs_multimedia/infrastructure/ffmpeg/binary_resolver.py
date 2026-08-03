from __future__ import annotations

import os
import platform
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
        platform_name = packaged_platform_name()
        if platform_name is not None:
            for packaged in packaged_binary_candidates(executable_name, platform_name):
                if packaged.is_file():
                    return packaged.resolve()

        system_binary = shutil.which(binary_name)
        if system_binary:
            return Path(system_binary).resolve()

        raise BinaryNotFoundError(
            f"{binary_name} was not found. Install FFmpeg or set {environment_key}."
        )


def packaged_binary_candidates(executable_name: str, platform_name: str) -> tuple[Path, ...]:
    """Return supported locations for a binary bundled with a desktop build."""
    package_relative = Path("resources") / "bin" / platform_name / executable_name
    candidates = [
        Path(sys.executable).resolve().parent / "blakelabs_multimedia" / package_relative,
        Path(__file__).resolve().parents[2] / package_relative,
        Path(
            str(
                files("blakelabs_multimedia").joinpath(
                    "resources", "bin", platform_name, executable_name
                )
            )
        ),
    ]

    unique_candidates: list[Path] = []
    seen: set[Path] = set()
    for candidate in candidates:
        resolved = candidate.resolve()
        if resolved not in seen:
            seen.add(resolved)
            unique_candidates.append(resolved)
    return tuple(unique_candidates)


def packaged_platform_name(
    system_platform: str | None = None,
    machine: str | None = None,
) -> str | None:
    current_platform = system_platform or sys.platform
    current_machine = (machine or platform.machine()).lower().replace("_", "-")

    if current_platform == "win32":
        return "windows-x64" if current_machine in {"amd64", "x86-64", "x64"} else None
    if current_platform.startswith("linux"):
        return "linux-x64" if current_machine in {"amd64", "x86-64", "x64"} else None
    if current_platform == "darwin":
        if current_machine in {"arm64", "aarch64"}:
            return "macos-arm64"
        if current_machine in {"amd64", "x86-64", "x64"}:
            return "macos-x64"
    return None
