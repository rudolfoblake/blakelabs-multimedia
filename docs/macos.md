# macOS distribution

BlakeLabs Multimedia builds native application bundles and DMG disk images for both current Mac processor families:

- Apple Silicon: `BlakeLabsMultimedia-macos-arm64.dmg`
- Intel: `BlakeLabsMultimedia-macos-x64.dmg`

## Build model

Each build runs on the matching GitHub-hosted Mac architecture. Cross-compilation is intentionally rejected because Python, PySide6, Qt and native extension modules must all match the target processor.

The pipeline:

1. Installs Python dependencies with `uv`.
2. Downloads architecture-specific static FFmpeg and FFprobe binaries.
3. Generates a 1024 px Blake Labs application icon.
4. Compiles the application with Nuitka `app` mode.
5. Includes Qt Quick/QML plugins and packaged resources.
6. Applies the bundle identifier `com.blakelabs.multimedia` and version metadata.
7. Ad-hoc signs and verifies the complete application bundle.
8. Launches the bundled executable using Qt offscreen mode.
9. Produces a drag-to-Applications DMG.

## Local builds

Apple Silicon:

```bash
bash scripts/build_macos.sh arm64
```

Intel:

```bash
bash scripts/build_macos.sh x64
```

The build script must run on hardware matching the requested architecture.

## Ad-hoc signing versus public distribution

The CI build uses ad-hoc signing (`codesign --sign -`). This validates that the bundle is internally consistent and that nested native binaries can be signed, but it does not establish Blake Labs as an Apple-verified developer.

For warning-free distribution outside the Mac App Store, the release must additionally be:

1. Signed using a **Developer ID Application** certificate.
2. Signed with Hardened Runtime and a secure timestamp.
3. Submitted to Apple's notary service with `notarytool`.
4. Stapled with the returned notarization ticket.
5. Re-tested using Gatekeeper before publication.

Apple documentation:

- https://developer.apple.com/documentation/security/notarizing-macos-software-before-distribution
- https://developer.apple.com/documentation/security/customizing-the-notarization-workflow

Certificate material, private keys and notarization credentials must never be committed to Git. They should be stored as protected GitHub Actions secrets when the Blake Labs Apple Developer account is ready.

## Mac App Store

The initial macOS target is direct DMG distribution. A Mac App Store submission would be a separate productization step because App Store apps must use App Sandbox and require an App Store Connect workflow. The application currently launches bundled FFmpeg/FFprobe processes and works with user-selected media files, so sandbox behavior must be reviewed and tested before attempting Store submission.
