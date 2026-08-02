# Roadmap and PR sequence

Work is intentionally split into focused pull requests.

## PR 1 — Executable architecture foundation

- Layer boundaries and dependency rules
- Responsive QML application shell
- Non-blocking FFprobe vertical slice
- Observable media queue model
- Quality workflow and tests

## PR 2 — Design system and interaction polish

- Blake Labs component library
- Typography, motion and spacing tokens
- Keyboard navigation and accessibility pass
- Empty/loading/error/success states
- Visual regression baseline

## PR 3 — Conversion engine

- Typed conversion request and preset model
- FFmpeg command builder
- Structured `-progress` parser
- Cancellation and atomic output handling
- MP4 and audio extraction presets

## PR 4 — Durable processing queue

- Queue scheduler and concurrency policy
- Pause, resume, retry and cancellation
- Crash-safe state persistence
- Disk-space and overwrite guards

## PR 5 — Windows productization

- Bundled FFmpeg resolution
- `pyside6-deploy` configuration
- Inno Setup installer
- Start menu integration and uninstall flow
- Signed-release pipeline preparation

## PR 6 — Linux productization

- AppImage build
- Desktop entry and MIME integration
- Distribution compatibility checks
