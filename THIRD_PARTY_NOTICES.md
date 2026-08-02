# Third-party notices

BlakeLabs Multimedia uses PySide6/Qt and executes FFmpeg/FFprobe as separate processes.

## Qt / PySide6

PySide6 is available under LGPLv3/GPLv3 and commercial licensing. Distribution packages must preserve the applicable Qt and PySide6 notices and replacement rights required by the selected license.

## FFmpeg

Development can use a system FFmpeg installation or paths configured through `BLAKELABS_FFMPEG` and `BLAKELABS_FFPROBE`.

Official build scripts currently download the BtbN `gpl` FFmpeg build so the bundled runtime includes `libx264` and the codecs used by the default presets. FFmpeg and included libraries retain their own licenses. Before a commercial release, review the generated build, ship its license files and provide the corresponding source offer or source location required by those licenses.

The application does not link against FFmpeg libraries; it starts FFmpeg and FFprobe as independent processes.
