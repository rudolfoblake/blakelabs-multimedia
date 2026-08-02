# Changelog

All notable changes to BlakeLabs Multimedia will be documented here.

## [Unreleased]

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
