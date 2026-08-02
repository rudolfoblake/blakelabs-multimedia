# BlakeLabs Multimedia

A native, cross-platform multimedia workspace by **Blake Labs**.

BlakeLabs Multimedia is being built in Python with PySide6, Qt Quick/QML and FFmpeg. The goal is a premium Windows and Linux application for conversion, compression, extraction, trimming and other practical media operations without exposing users to command-line complexity.

## Current foundation

The first executable vertical slice includes:

- Responsive Blake Labs desktop shell
- Drag-and-drop and multi-file selection
- Non-blocking FFprobe analysis through `QProcess`
- Observable session queue
- Clean architecture boundaries
- Unit tests and pull-request quality gates

Conversion is intentionally scheduled for a focused follow-up PR.

## Architecture

```text
presentation -> application -> domain
infrastructure -> application -> domain
bootstrap -> composition only
```

The GUI never builds FFmpeg commands and long-running processes never block the UI thread. See [docs/architecture.md](docs/architecture.md) for the full boundary rules.

## Development

Requirements:

- Python 3.12+
- `uv`
- FFmpeg available on `PATH` during development

```bash
uv sync --all-groups
uv run blakelabs-multimedia
```

Override binary discovery when needed:

```bash
BLAKELABS_FFPROBE=/path/to/ffprobe uv run blakelabs-multimedia
BLAKELABS_FFMPEG=/path/to/ffmpeg uv run blakelabs-multimedia
```

## Quality gates

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest
```

## Roadmap

Development is split into focused pull requests. See [docs/roadmap.md](docs/roadmap.md).

## Contributing

Read [CONTRIBUTING.md](CONTRIBUTING.md). Feature development goes through focused branches and draft pull requests.

## License

License selection is pending. Until a license is added, no permission is granted to copy, modify or redistribute the source.
