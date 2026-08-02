from __future__ import annotations

import argparse
import tomllib
from pathlib import Path


class InvalidProjectVersionError(ValueError):
    pass


def normalize_msix_version(version: str) -> str:
    """Convert a PEP 440 numeric release into the four-part MSIX version format."""
    raw_parts = version.split(".")
    if not 1 <= len(raw_parts) <= 4 or any(not part.isdigit() for part in raw_parts):
        raise InvalidProjectVersionError(
            f"MSIX requires a numeric version with at most four parts, received {version!r}."
        )

    parts = [int(part) for part in raw_parts]
    if any(part > 65535 for part in parts):
        raise InvalidProjectVersionError("Each MSIX version component must be between 0 and 65535.")

    parts.extend([0] * (4 - len(parts)))
    return ".".join(str(part) for part in parts)


def read_project_version(project_file: Path) -> str:
    data = tomllib.loads(project_file.read_text(encoding="utf-8"))
    project = data.get("project")
    if not isinstance(project, dict):
        raise InvalidProjectVersionError("pyproject.toml does not contain a [project] table.")
    version = project.get("version")
    if not isinstance(version, str):
        raise InvalidProjectVersionError("[project].version must be a string.")
    return normalize_msix_version(version)


def render_manifest(template_file: Path, project_file: Path, output_file: Path) -> str:
    version = read_project_version(project_file)
    template = template_file.read_text(encoding="utf-8")
    if "{{VERSION}}" not in template:
        raise ValueError("MSIX manifest template is missing the {{VERSION}} placeholder.")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(template.replace("{{VERSION}}", version), encoding="utf-8")
    return version


def main() -> None:
    parser = argparse.ArgumentParser(description="Render the Store MSIX manifest.")
    parser.add_argument("--template", type=Path, required=True)
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    version = render_manifest(args.template, args.project, args.output)
    print(f"Rendered MSIX manifest version {version} at {args.output}")


if __name__ == "__main__":
    main()
