# Third-party notices

BlakeLabs Multimedia uses PySide6/Qt and executes FFmpeg/FFprobe as separate processes.

## Qt / PySide6

PySide6 is available under LGPLv3/GPLv3 and commercial licensing. Distribution packages must preserve the applicable Qt and PySide6 notices and replacement rights required by the selected license.

## FFmpeg

Development can use a system FFmpeg installation or paths configured through `BLAKELABS_FFMPEG` and `BLAKELABS_FFPROBE`.

Windows and Linux build scripts download BtbN GPL FFmpeg builds. macOS build scripts download the architecture-specific static binaries published by the `eugeneware/ffmpeg-static` project, currently from release `b6.1.1`. That project sources its macOS binaries from long-running third-party FFmpeg builders and publishes the matching build and license metadata when available.

The bundled runtimes include GPL components such as `libx264`, which are used by the default MP4 presets. FFmpeg and included libraries retain their own licenses. Before commercial release, review each generated package, preserve the included license notices and provide the corresponding source offer or source location required by those licenses.

The application does not link against FFmpeg libraries; it starts FFmpeg and FFprobe as independent processes.
