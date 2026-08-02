# Roadmap

PR #1 delivers the complete first MVP in one review surface, while preserving strict internal module boundaries.

## Included in MVP PR #1

- Clean architecture and contribution workflow
- Premium responsive Qt Quick/QML workspace
- Asynchronous media probing
- Typed preset catalog
- Universal FFmpeg input path
- MP4, WebM, MP3, FLAC, WAV and GIF outputs
- Sequential processing queue
- Progress, speed and ETA parsing
- Cancellation and temporary-file cleanup
- Atomic output publishing and collision-safe names
- Remembered output folder and selected preset
- Automated lint, formatting, type, unit and QML startup checks
- Windows standalone build and installer definition
- Linux standalone bundle
- Build-time FFmpeg acquisition

## Next after MVP

### Editing tools

- Accurate and stream-copy trimming
- Join audio/video files
- Rotate, crop and aspect-ratio tools
- Loudness normalization and fades
- Subtitle extraction, embedding and burning
- Thumbnail and frame extraction

### Processing depth

- Hardware encoder detection and fallback
- Parallel audio jobs with configurable limits
- Pause/resume semantics where technically possible
- Retry and durable crash recovery
- Disk-space estimation and output-size prediction

### Productization

- Signed Windows builds
- AppImage and `.deb`
- Auto-update channel
- PT-BR and English localization
- Visual regression tests
- Accessibility and full keyboard-navigation audit
- Release license decision and complete third-party attribution bundle
