# BlakeLabs Multimedia

A premium native audio and video workspace by **Blake Labs**.

BlakeLabs Multimedia turns FFmpeg into a clean Windows and Linux desktop application. Files stay local, the interface stays responsive, and the user does not need to understand codecs, filters or terminal syntax.

## Downloads

Permanent Windows and Linux installers are published on the repository's **Releases** page.

Each project version creates:

- `BlakeLabsMultimedia-Setup-x64.exe` — native Windows installer
- `BlakeLabsMultimedia-linux-x64.tar.gz` — standalone Linux bundle

Release files remain attached to the tagged version instead of expiring like temporary GitHub Actions artifacts.

## MVP capabilities

- Drag-and-drop and multi-file selection
- Asynchronous FFprobe inspection
- Sequential background processing without blocking the UI
- Real progress, encoding speed and ETA
- Cancellation with incomplete-output cleanup
- Atomic output publishing: originals are never overwritten
- Configurable output directory remembered with native settings
- Seven built-in recipes: MP4 Universal, MP4 Compact, WebM, MP3, FLAC, WAV and GIF
- Windows standalone build and Inno Setup installer
- Linux standalone compressed bundle
- Bundled FFmpeg/FFprobe in release builds, with system and environment-variable fallback for development

## Architecture

```text
presentation -> application -> domain
infrastructure -> application -> domain
bootstrap -> composition only
```

The project is a modular monolith. QML owns layout and animation, Python application services coordinate jobs, and FFmpeg details terminate inside infrastructure adapters. See [docs/architecture.md](docs/architecture.md).

## Development

Requirements:

- Python 3.12+
- `uv`
- FFmpeg on `PATH`, or explicit binary paths

```bash
uv sync --group dev
uv run blakelabs-multimedia
```

Override binary discovery:

```bash
BLAKELABS_FFPROBE=/path/to/ffprobe BLAKELABS_FFMPEG=/path/to/ffmpeg uv run blakelabs-multimedia
```

## Quality gates

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src scripts
uv run pytest --cov --cov-report=term-missing
```

CI also starts the complete QML application using Qt's offscreen platform. This catches missing imports, broken bindings and composition failures.

## Native builds

### Windows installer

```powershell
./scripts/build_windows.ps1
choco install innosetup -y
iscc installer/windows/blakelabs-multimedia.iss
```

Output: `build/installer/BlakeLabsMultimedia-Setup-x64.exe`.

### Linux bundle

```bash
./scripts/build_linux.sh
```

Output: `build/linux/BlakeLabsMultimedia-linux-x64.tar.gz`.

The `Native builds and releases` workflow validates both packages in pull requests. After a version bump reaches `main`, it creates the corresponding GitHub Release and permanently attaches both files.

## Output safety

- Input files are never used as output paths.
- Output names use `-converted` and a numeric suffix when needed.
- FFmpeg writes to a hidden temporary file.
- The final file appears only after FFmpeg exits successfully.
- Cancellation and failure remove partial output.

## Contributing

Read [CONTRIBUTING.md](CONTRIBUTING.md). Development uses branches and pull requests, even when several MVP capabilities are delivered in one PR.

## Third-party software

Read [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) before redistribution. Release builds currently bundle a GPL FFmpeg variant because the default MP4 presets use `libx264`.

## License

License selection for the BlakeLabs Multimedia source is pending. Until a license is added, no permission is granted to copy, modify or redistribute the source.
