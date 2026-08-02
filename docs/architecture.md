# Architecture

BlakeLabs Multimedia is a modular desktop application, not a collection of UI callbacks around shell commands. The initial shape is a modular monolith with strict dependency direction and replaceable adapters.

## Dependency direction

```text
presentation ───────┐
                    v
              application ---> domain
                    ^
                    |
infrastructure -----┘

bootstrap composes concrete implementations at runtime.
```

### Domain

Pure Python entities and value objects. This layer knows what a media asset and processing job are, but does not know Qt, FFmpeg, operating systems or persistence.

### Application

Use cases and ports. It validates and coordinates work, while depending only on abstractions for probing, transcoding, storage and process execution.

### Infrastructure

Adapters for FFmpeg/FFprobe, filesystem access, settings, platform integration and packaging concerns. FFmpeg JSON and process details terminate here.

### Presentation

PySide6 controllers, list models and QML. Presentation owns user interaction and view state. It calls use cases and never constructs raw FFmpeg commands.

### Bootstrap

The composition root creates the Qt application, chooses adapters and exposes only presentation-facing objects to QML.

## Module growth

The first vertical slice lives in the shared layers. As capabilities grow, code moves into cohesive modules without changing the dependency rule:

```text
modules/
  conversion/
  trimming/
  audio_tools/
  batch_queue/
  presets/
  diagnostics/
```

Each module may contain domain, application and adapter packages. Shared code is promoted only after at least two real consumers exist; speculative `utils` packages are forbidden.

## Responsiveness model

- QML rendering and lightweight state updates stay on the GUI thread.
- FFmpeg and FFprobe run through asynchronous `QProcess` adapters.
- CPU-heavy Python work uses explicit worker executors and returns immutable results.
- Cancellation is part of every long-running port contract.
- Queue state is observable and independent from individual screens.
- Process output is streamed; the UI never waits on `communicate()`, `waitForFinished()` or blocking filesystem scans.

## FFmpeg boundary

Commands are produced and interpreted inside infrastructure adapters. The rest of the system works with typed domain objects and progress events. This keeps future options open:

- bundled or system FFmpeg
- CPU or hardware encoders
- local execution or remote workers
- CLI and desktop frontends sharing the same application core

## UI architecture

QML components consume narrow Qt models/controllers:

- Controllers expose user intents as slots.
- Models expose observable data through roles.
- QML owns layout, transitions and local visual state.
- Business rules do not live in JavaScript expressions.
- Screens adapt by available width rather than targeting fixed resolutions.

## Testing strategy

- Domain: fast unit tests with no Qt runtime.
- Application: fake ports and deterministic callback tests.
- Infrastructure: parser tests with committed sanitized fixtures; process integration tests use tiny generated media.
- Presentation: model tests plus smoke tests under an offscreen Qt platform.
- Packaging: clean Windows and Linux runners build artifacts independently.
