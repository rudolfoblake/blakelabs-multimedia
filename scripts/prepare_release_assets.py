from __future__ import annotations

import argparse
import hashlib
import shutil
from pathlib import Path

EXPECTED_RELEASE_ASSETS = frozenset(
    {
        "BlakeLabsMultimedia-Setup-x64.exe",
        "BlakeLabsMultimedia-Store-x64.msix",
        "BlakeLabsMultimedia-linux-x64.tar.gz",
        "BlakeLabsMultimedia-macos-arm64.dmg",
        "BlakeLabsMultimedia-macos-x64.dmg",
    }
)


class ReleaseAssetError(RuntimeError):
    pass


def prepare_release_assets(source: Path, destination: Path) -> dict[str, str]:
    if not source.is_dir():
        raise ReleaseAssetError(f"Release asset source does not exist: {source}")

    discovered: dict[str, Path] = {}
    for asset in sorted(path for path in source.rglob("*") if path.is_file()):
        existing = discovered.get(asset.name)
        if existing is not None:
            raise ReleaseAssetError(
                f"Duplicate release asset name {asset.name!r}: {existing} and {asset}"
            )
        discovered[asset.name] = asset

    names = frozenset(discovered)
    missing = EXPECTED_RELEASE_ASSETS - names
    unexpected = names - EXPECTED_RELEASE_ASSETS
    if missing or unexpected:
        details: list[str] = []
        if missing:
            details.append(f"missing: {', '.join(sorted(missing))}")
        if unexpected:
            details.append(f"unexpected: {', '.join(sorted(unexpected))}")
        raise ReleaseAssetError("Invalid release asset set (" + "; ".join(details) + ").")

    if destination.exists():
        shutil.rmtree(destination)
    destination.mkdir(parents=True)

    digests: dict[str, str] = {}
    for name in sorted(discovered):
        target = destination / name
        shutil.copy2(discovered[name], target)
        digests[name] = _sha256(target)
    return digests


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description="Flatten and verify GitHub Release assets.")
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--destination", type=Path, required=True)
    args = parser.parse_args()

    digests = prepare_release_assets(args.source, args.destination)
    for name, digest in digests.items():
        print(f"{digest}  {args.destination / name}")


if __name__ == "__main__":
    main()
