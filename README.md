# BlakeLabs Multimedia

**Professional local audio and video conversion, built natively by Blake Labs.**

BlakeLabs Multimedia turns FFmpeg into a focused Windows, macOS and Linux desktop product. Files stay on the device, the UI remains responsive, source files are never overwritten, and both safe presets and professional controls are available without terminal commands.

## Instagram video downloader

The repository also includes an interactive helper for downloading videos you are authorized to access from Instagram. It supports two modes:

1. Download one video/Reel by pasting its Instagram URL.
2. Download videos in batch from an Instagram account/profile.

Run it with:

```bash
uv sync
uv run python scripts/instagram_downloader.py
```

The script asks which mode to use, where to save the files, and whether to log in. Login is optional for public content and may be required for private content you are allowed to access. To avoid typing a password interactively, set `INSTAGRAM_PASSWORD` in the environment; do not commit credentials to the repository.

## Product highlights

- Local, private audio and video processing
- Drag-and-drop and multi-file queue
- Real progress, encoding speed and ETA
- Cancellation with partial-output cleanup
- Atomic output publication
- Professional presets for MP4, WebM, MP3, FLAC, WAV and GIF
- Advanced video quality, bitrate, resolution and encoder-speed controls
- Advanced audio bitrate, sample-rate, channel and loudness controls
- Persistent settings and local diagnostics
- Hardened camera-style MOV to MP4 conversion
- Native Windows EXE/MSIX, macOS DMG and Linux bundle
- Blake Labs alien branding across the application and generated packages

## Version 0.4.0

The 0.4 release moves the application from a functional converter to a professional conversion workspace.

### Professional controls

Video:

- CRF quality targets from visually lossless to compact
- Fixed video bitrate profiles
- 4K, 1080p, 720p and 480p maximum-width controls
- Encoder speed from ultra-fast to very slow

Audio:

- 96–320 kbps lossy bitrate overrides
- 44.1, 48 and 96 kHz sample rates
- mono and stereo channel controls
- one-pass loudness normalization targeting -16 LUFS
- optional source-metadata preservation

All controls can remain on **Preset default**. Advanced values are persisted locally and can be reset in one action.

### MOV compatibility

MP4 Universal now includes primary-stream mapping, timestamp regeneration, auxiliary-stream exclusion, even-dimension scaling, variable-frame-rate handling, larger muxing queues, AAC stereo output and fast-start publication. CI creates a camera-style MOV with MJPEG video and PCM audio, converts it through the real preset and verifies H.264 + AAC output.

## Downloads

Permanent native packages are published on the repository's **Releases** page.

Each project version creates:

- `BlakeLabsMultimedia-Setup-x64.exe` — native Windows installer, currently unsigned
- `BlakeLabsMultimedia-Store-x64.msix` — unsigned package for Microsoft Store submission
- `BlakeLabsMultimedia-macos-arm64.dmg` — Apple Silicon disk image
- `BlakeLabsMultimedia-macos-x64.dmg` — Intel Mac disk image
- `BlakeLabsMultimedia-linux-x64.tar.gz` — standalone Linux bundle

The Store MSIX is uploaded to Partner Center, where Microsoft signs it after certification. It is not intended for unsigned direct sideloading from GitHub.

The macOS DMGs are ad-hoc signed for bundle-integrity validation. Public distribution without Gatekeeper warnings still requires a Developer ID certificate and Apple notarization. See [macOS packaging](docs/macos.md).

Microsoft Store product: `https://apps.microsoft.com/detail/9NS1J3D51RFX`

## Documentation

- [User guide](docs/user-guide.md)
- [Advanced conversion reference](docs/advanced-conversion.md)
- [Architecture](docs/architecture.md)
- [Microsoft Store submission](docs/microsoft-store.md)
- [macOS packaging](docs/macos.md)
- [Privacy policy](docs/privacy-policy.md)
- [Terms of use](docs/terms-of-use.md)
- [Third-party notices](THIRD_PARTY_NOTICES.md)

## Built-in presets

| Preset | Output | Purpose |
|---|---|---|
| MP4 Universal | H.264 + AAC | Broad phone, TV and web compatibility |
| MP4 Compact | 720p H.264 + AAC | Smaller files for sharing and storage |
| WebM Modern | VP9 + Opus | Modern browser delivery |
| Extract MP3 | MP3 | High-quality audio extraction |
| FLAC Lossless | FLAC | Lossless archive and listening |
| WAV Studio | 24-bit PCM WAV | Editing and production |
| Animated GIF | GIF | Compact looping animation |

## Privacy and output safety

- Media files are processed locally and are not uploaded by the application.
- Input files are never used as output paths.
- Output names use `-converted` and a numeric suffix when required.
- FFmpeg writes to a hidden temporary file.
- Final output appears only after FFmpeg exits successfully.
- Cancellation and failure remove incomplete output when possible.
- Rotating diagnostics remain in the operating system's local app-data directory.

Read the full [Privacy Policy](docs/privacy-policy.md).

## Architecture

```text
presentation -> application -> domain
infrastructure -> application -> domain
bootstrap -> composition only
```

The project is a modular monolith. QML owns layout and interaction, Python application services coordinate jobs, domain models define presets and overrides, and FFmpeg details terminate inside infrastructure adapters.

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

Run quality gates:

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src scripts
uv run pytest --cov --cov-report=term-missing
```

Run a real preset conversion using system FFmpeg:

```bash
uv run python scripts/smoke_ffmpeg_conversion.py \
  --source camera.mov \
  --output camera-converted.mp4 \
  --preset mp4-balanced
```

CI also launches the complete QML application with real audio, captures the rendered UI, converts a camera-style MOV, and validates every native package.

## Native builds

### Windows installer

```powershell
./scripts/build_windows.ps1
choco install innosetup -y
iscc installer/windows/blakelabs-multimedia.iss
```

Output: `build/installer/BlakeLabsMultimedia-Setup-x64.exe`.

The build generates and embeds the Blake Labs alien `.ico` before compiling the executable and installer.

### Microsoft Store MSIX

```powershell
./scripts/build_msix.ps1
```

Output: `build/msix/BlakeLabsMultimedia-Store-x64.msix`.

Store tile assets are generated from the same alien brand mark. The package uses the identity assigned to Blake Labs and is validated by `MakeAppx.exe`.

### macOS disk images

```bash
bash scripts/build_macos.sh arm64
bash scripts/build_macos.sh x64
```

Outputs:

- `build/macos/BlakeLabsMultimedia-macos-arm64.dmg`
- `build/macos/BlakeLabsMultimedia-macos-x64.dmg`

### Linux bundle

```bash
bash scripts/build_linux.sh
```

Output: `build/linux/BlakeLabsMultimedia-linux-x64.tar.gz`.

## Contributing

Read [CONTRIBUTING.md](CONTRIBUTING.md). Development uses branches and pull requests, with native builds and quality gates required before release.

## Licensing

Third-party components retain their original licenses. Release builds currently bundle GPL FFmpeg variants because the default MP4 presets use `libx264`.

A final source-code license for BlakeLabs Multimedia is still pending. Until one is added, no permission is granted to copy, modify or redistribute the Blake Labs source code beyond rights required by applicable third-party licenses.
