# Architecture

BlakeLabs Multimedia is a modular desktop application, not a set of button callbacks wrapped around shell commands. It starts as a modular monolith with strict dependency direction and replaceable adapters.

## Dependency direction

```text
presentation ------> application ---> domain
infrastructure ----> application ---> domain
bootstrap composes concrete implementations
```

### Domain

Pure Python entities and values: media assets, job states, processing requests, progress and conversion presets. Domain code has no Qt or FFmpeg imports.

### Application

Use cases, ports and orchestration services. `ProcessingQueue` owns sequencing and cancellation routing while depending on `MediaProcessorPort`.

### Infrastructure

Adapters for FFprobe, FFmpeg, command construction, progress parsing, binary resolution and platform packaging. Raw process output never leaks beyond this boundary.

### Presentation

PySide6 controllers, list models and QML. Controllers translate user intent into use cases; models expose observable queue state; QML owns responsive layout and transitions.

### Bootstrap

The composition root wires probe, processing, queue and presentation objects. It also provides a timed offscreen startup mode used by CI.

## Processing flow

```text
Drop file
  -> ProbeMedia
  -> QtFfprobeMediaProbe
  -> MediaAsset
  -> preset selection
  -> ProcessingRequest
  -> ProcessingQueue
  -> QtFfmpegMediaProcessor
  -> temporary output
  -> atomic replace
  -> completed output
```

## Responsiveness rules

- The GUI thread only handles Qt events and lightweight model updates.
- FFprobe and FFmpeg always run through asynchronous `QProcess` instances.
- Production code does not use `waitForFinished()`, `subprocess.run()` or blocking process reads.
- Progress streams from `-progress pipe:1`.
- Cancellation is part of the application port contract.
- A force-kill fallback runs after graceful termination without blocking the caller.

## Output integrity

- Source files are never used as output paths.
- Collision-safe filenames are selected before processing.
- FFmpeg writes to a hidden temporary file with the final container extension.
- `os.replace` publishes the result only after successful process exit.
- Failed and cancelled jobs delete partial output.

## Preset model

Presets are immutable domain values containing identity, accepted media kinds, output extension and FFmpeg arguments. QML receives serialized display metadata and never assembles commands.

## Packaging boundary

Development resolves binaries in this order:

1. Explicit environment variables
2. Binaries included in application resources
3. System `PATH`

Release scripts download FFmpeg before Nuitka creates standalone distributions. Windows is wrapped with Inno Setup; Linux is distributed as a standalone compressed directory in the MVP.

## Testing strategy

- Domain and application: fast unit tests with fake ports
- Infrastructure: parser and command-construction tests
- Presentation: full offscreen QML startup in CI
- Packaging: independent Windows and Linux workflows
- Future: generated-media integration tests and visual regression baselines
