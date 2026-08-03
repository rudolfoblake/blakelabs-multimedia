from __future__ import annotations

import argparse
import os
import shutil
import subprocess
from pathlib import Path
from uuid import uuid4

from blakelabs_multimedia.domain.conversion import ProcessingRequest, find_preset
from blakelabs_multimedia.infrastructure.ffmpeg.command_builder import (
    build_ffmpeg_arguments,
    temporary_output_path,
)


def smoke_convert(source: Path, output: Path, preset_id: str) -> None:
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg is None:
        raise RuntimeError("ffmpeg is not available on PATH")

    preset = find_preset(preset_id)
    job_id = uuid4()
    temporary = temporary_output_path(output, job_id)
    temporary.unlink(missing_ok=True)
    request = ProcessingRequest(
        job_id=job_id,
        source=source,
        output=output,
        duration_seconds=None,
        preset=preset,
    )
    result = subprocess.run(
        [ffmpeg, *build_ffmpeg_arguments(request, temporary)],
        capture_output=True,
        text=True,
        timeout=180,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg smoke conversion failed:\n{result.stderr}")
    if not temporary.exists() or temporary.stat().st_size == 0:
        raise RuntimeError("FFmpeg exited successfully without creating media output")
    output.parent.mkdir(parents=True, exist_ok=True)
    os.replace(temporary, output)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a real preset conversion with system FFmpeg.")
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--preset", default="mp4-balanced")
    args = parser.parse_args()
    smoke_convert(args.source, args.output, args.preset)
    print(f"Converted smoke fixture to {args.output}")


if __name__ == "__main__":
    main()
