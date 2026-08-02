# Contributing to BlakeLabs Multimedia

BlakeLabs Multimedia is developed through small, reviewable pull requests. Direct feature commits to `main` are not part of the normal workflow.

## Development workflow

1. Sync the latest `main`.
2. Create a focused branch using one of these prefixes:
   - `feat/` for product capabilities
   - `fix/` for bug fixes
   - `refactor/` for behavior-preserving restructuring
   - `chore/` for tooling, build and maintenance
   - `docs/` for documentation-only changes
3. Keep the branch limited to one coherent outcome.
4. Add or update tests for changed behavior.
5. Run the local quality gates.
6. Open a draft pull request early.
7. Mark it ready only after the checklist is complete.
8. Prefer squash merge so `main` remains readable.

Automation agents use the `agent/` prefix and must follow the same review and validation rules.

## Architecture rules

Dependencies point inward:

```text
presentation -> application -> domain
infrastructure -> application -> domain
bootstrap -> all composition-time modules
```

- `domain` contains pure business concepts and must not import Qt, FFmpeg wrappers, filesystem adapters or application configuration.
- `application` coordinates use cases and defines ports. It must not know concrete UI or process implementations.
- `infrastructure` implements ports for FFmpeg, storage, settings and operating-system integration.
- `presentation` owns PySide6/QML models, controllers and view state. It must not build raw FFmpeg command lines.
- `bootstrap` is the composition root where concrete dependencies are wired.
- Cross-module access must use public interfaces. Avoid importing another module's internal implementation.
- Long-running work must never execute on the GUI thread.

## Pull request size and sequencing

Prefer a sequence of focused PRs over a large mixed change. A normal PR should be understandable in one review session. Separate architecture, UI shell, FFmpeg adapters, queue execution and packaging when possible.

Every PR must explain:

- What changed
- Why it changed
- User or developer impact
- Architectural consequences
- How it was validated
- Follow-up work intentionally left out

## Local setup

Python 3.12 or newer and `uv` are required.

```bash
uv sync
uv run blakelabs-multimedia
```

## Quality gates

Run before marking a PR ready:

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest
```

When QML files change, also launch the application and verify at minimum:

- Window resize behavior
- Keyboard focus and navigation
- Drag-and-drop state
- Empty, loading, success and failure states
- No visible UI freeze during background work

## Commit style

Use concise imperative Conventional Commit messages when practical:

```text
feat: add asynchronous media probe
fix: preserve queue item ordering
refactor: isolate ffmpeg command builder
chore: configure windows packaging
```

## Definition of done

A change is done when:

- Tests and static checks pass
- Public behavior is documented
- Errors are surfaced with actionable messages
- Cancellation and cleanup are considered for background work
- Platform assumptions are explicit
- No secrets, generated binaries or personal media are committed
- The PR checklist is complete
