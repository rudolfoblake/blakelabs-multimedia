# Changelog

All notable changes to BlakeLabs Multimedia will be documented here.

## [0.4.0] - 2026-08-02

### Added

- Professional advanced settings panel with persistent local preferences
- CRF and fixed-bitrate video control
- Maximum video resolution and encoder-speed control
- Audio bitrate, sample-rate and channel control
- One-pass -16 LUFS loudness normalization
- Optional metadata removal
- Blake Labs alien logo in the application header and drop zone
- Generated alien icons for Windows EXE, Inno Setup, Microsoft Store and macOS
- Store square and wide tile artwork
- Real camera-style MOV to H.264/AAC conversion smoke test
- User guide, advanced conversion reference, privacy policy and terms of use
- Actionable queue errors with direct access to local Diagnostics

### Changed

- Rebuilt the visual system around the Blake Labs Control black/cyan language
- Updated MP4 presets for primary-stream mapping, VFR handling and broad device compatibility
- Improved WebM and audio stream selection
- Updated product and installer metadata to version 0.4.0
- Rewrote the README as professional product documentation

### Fixed

- MOV files with camera-style MJPEG video and PCM audio now convert through MP4 Universal
- Odd video dimensions are normalized before H.264 encoding
- Unsupported subtitle and data streams no longer break normal video output
- Missing or negative timestamps are normalized
- Large muxing queues no longer fail on files with complex stream timing
- FFmpeg failures now preserve a complete local log and show a useful summary in the queue

## [0.3.1] - 2026-08-02

### Added

- Native responsive Qt Quick/QML workspace
- FFprobe metadata analysis without blocking the interface
- FFmpeg conversion engine with structured progress reporting
- Seven video, audio and GIF presets
- Sequential background queue with cancellation
- Collision-safe and atomic output handling
- Remembered preset and output directory
- Windows installer and Linux standalone build pipelines
- Automated lint, formatting, typing, unit and QML startup checks
- Microsoft Store MSIX packaging with the assigned Blake Labs product identity
- Deterministic Store manifest version rendering and generated logo assets
- Partner Center submission and restricted-capability documentation
- Native macOS `.app` and DMG packaging for Apple Silicon and Intel
- Architecture-aware bundled FFmpeg resolution on macOS
- macOS bundle signing verification and offscreen startup validation
- Persistent rotating diagnostics logs in the platform app-data directory
- Real-media QML smoke tests with rendered screenshots
- Packaged Windows smoke test using the bundled FFprobe runtime

### Changed

- Replaced the decorative sidebar and placeholder navigation with a focused conversion workspace
- Simplified copy, alignment, preset selection and queue hierarchy
- Replaced the self-sizing nested `ListView` with a stable layout-backed queue
- Limited FFprobe metadata fields and output size for predictable analysis

### Fixed

- Media analysis can now be cancelled and times out after 15 seconds
- Unexpected probe failures surface a clear error instead of leaving files stuck in analysis
- The UI now repaints the queued file before starting metadata analysis
- File-picker messaging no longer claims unsupported image conversion
