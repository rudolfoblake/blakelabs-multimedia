from pathlib import Path

import pytest
from scripts.render_msix_manifest import (
    InvalidProjectVersionError,
    normalize_msix_version,
    render_manifest,
)


def test_normalize_msix_version_pads_to_four_parts() -> None:
    assert normalize_msix_version("0.2.0") == "0.2.0.0"


def test_normalize_msix_version_rejects_prerelease_text() -> None:
    with pytest.raises(InvalidProjectVersionError):
        normalize_msix_version("0.2.0-beta.1")


def test_render_manifest_replaces_store_version(tmp_path: Path) -> None:
    template = tmp_path / "AppxManifest.xml.template"
    project = tmp_path / "pyproject.toml"
    output = tmp_path / "layout" / "AppxManifest.xml"
    template.write_text('<Identity Version="{{VERSION}}" />', encoding="utf-8")
    project.write_text('[project]\nversion = "1.4.2"\n', encoding="utf-8")

    version = render_manifest(template, project, output)

    assert version == "1.4.2.0"
    assert output.read_text(encoding="utf-8") == '<Identity Version="1.4.2.0" />'
