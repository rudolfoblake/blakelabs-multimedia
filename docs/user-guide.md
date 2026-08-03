# BlakeLabs Multimedia — User Guide

BlakeLabs Multimedia converts audio and video locally with FFmpeg. Media files are not uploaded to Blake Labs or to a third-party service.

## Quick start

1. Select **Choose files** or drag media into the drop zone.
2. Wait until each file is marked **Ready**.
3. Select an output preset.
4. Optionally open **Advanced settings**.
5. Choose the destination folder or keep **Same folder as source**.
6. Select **Convert**.

The original file is never overwritten. New files use the suffix `-converted`, followed by a number when necessary.

## Included presets

| Preset | Best use |
|---|---|
| MP4 Universal | Phones, televisions, messaging and web playback |
| MP4 Compact | Smaller 720p files for sharing and storage |
| WebM Modern | VP9 + Opus browser delivery |
| Extract MP3 | Audio extraction from audio or video |
| FLAC Lossless | Lossless music and archive workflows |
| WAV Studio | 24-bit PCM for editing and production |
| Animated GIF | Short looping animations from video |

## Advanced settings

Advanced settings override only the relevant parts of the selected preset. Leaving a control on **Preset default** is the safest option.

Video controls:

- **Quality (CRF):** lower values produce higher quality and larger files.
- **Video bitrate:** enables a fixed bitrate workflow and disables the CRF override.
- **Maximum resolution:** prevents upscaling and limits the output width.
- **Encoder speed:** slower modes generally improve compression efficiency but take longer.

Audio controls:

- **Audio bitrate:** applies to MP3, AAC and Opus output, not FLAC or WAV.
- **Sample rate:** selects 44.1, 48 or 96 kHz.
- **Channels:** keeps the preset default, or forces mono/stereo.
- **Normalize loudness:** applies one-pass EBU-style loudness normalization targeting -16 LUFS.
- **Preserve source metadata:** retains compatible tags when enabled.

See [Advanced Conversion](advanced-conversion.md) for recommended profiles.

## Queue and diagnostics

Each queue item shows its preset, duration, file size, progress, encoding speed and ETA when available.

On failure, the card displays an actionable error. Select **Diagnostics** to open the local log folder. Logs contain technical processing details and local file paths; they are not uploaded automatically.

## MOV and camera video

Version 0.4.0 adds a hardened camera-video pipeline for MOV files, including:

- timestamp regeneration;
- selection of the primary video and audio streams;
- ignoring unsupported auxiliary streams;
- even-dimension scaling for H.264 compatibility;
- variable-frame-rate support;
- large muxing queues;
- AAC stereo output for broad playback support.

A MOV file may still fail when it is incomplete, encrypted, severely damaged or encoded with a decoder unavailable in the bundled FFmpeg build. The queue error and Diagnostics log will identify the likely cause.

## Local files and privacy

- Conversion happens on the current computer.
- No account is required.
- No media is transmitted by the application.
- Output is first written to a hidden temporary file.
- Temporary output is removed after cancellation or failure.
- The final output appears only after FFmpeg completes successfully.

## Support information

When reporting a problem, include:

- application version;
- operating system;
- selected preset and advanced settings;
- source container and codecs shown in the queue;
- the relevant Diagnostics log excerpt.

Do not share private media files unless you have intentionally removed sensitive content.
