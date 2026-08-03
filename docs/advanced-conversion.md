# Advanced Conversion Reference

The built-in presets are designed to work without manual tuning. Advanced settings are overrides for users who need predictable quality, file size or production characteristics.

## Recommended video profiles

### High-quality master for general playback

- Preset: **MP4 Universal**
- Quality: **CRF 18** or **CRF 20**
- Maximum resolution: **Source / preset**
- Encoder speed: **Slow**
- Audio bitrate: **256 kbps**
- Sample rate: **48 kHz**

### Balanced everyday MP4

- Preset: **MP4 Universal**
- Quality: **CRF 22** or **Preset default**
- Encoder speed: **Medium** or **Preset default**
- Audio bitrate: **192 kbps**

### Smaller social/share file

- Preset: **MP4 Compact**
- Quality: **CRF 24**
- Maximum resolution: **720p**
- Audio bitrate: **128 kbps**

### Fixed-bitrate delivery

- Preset: **MP4 Universal**
- Video bitrate: **5 Mbps** for typical 1080p material, or **8 Mbps** for more motion/detail
- Maximum resolution: **1080p**
- Audio bitrate: **192 kbps**

A fixed video bitrate clears the CRF override. Selecting CRF clears the fixed-bitrate override.

## CRF guidance

CRF is a quality target used by H.264 and supported by the video presets.

| CRF | Typical result |
|---:|---|
| 18 | Visually lossless for many sources; larger output |
| 20 | High quality |
| 22 | Balanced default |
| 24 | Smaller output with moderate quality loss |
| 28 | Aggressive compression |

The same CRF does not guarantee the same file size across different videos. Motion, noise and detail materially affect output size.

## Encoder speed

| Setting | Behavior |
|---|---|
| Ultra fast | Fastest conversion, weakest compression efficiency |
| Fast | Good for quick previews |
| Medium | Balanced default |
| Slow | Better compression, longer processing |
| Very slow | Maximum compression effort; often small practical gains |

Encoder speed does not directly set visual quality. At the same CRF, slower modes usually produce smaller files.

## Audio guidance

### MP3

- 96 kbps: speech or small files
- 128–160 kbps: general listening
- 192 kbps: balanced high quality
- 256–320 kbps: high-quality music delivery

### Sample rate

- 44.1 kHz: music-oriented workflows
- 48 kHz: video, film and general multimedia
- 96 kHz: production or archival workflows when the source warrants it

Upsampling cannot recreate information absent from the source.

### Channels

- Preset default: uses the preset's compatibility choice
- Mono: speech and smallest output
- Stereo: music and broad consumer playback

### Loudness normalization

The application uses a one-pass `loudnorm` filter targeting approximately -16 LUFS, LRA 11 and true peak -1.5 dB. This is useful for speech, podcasts and mixed source libraries. It is not a substitute for mastering and can change the perceived dynamics of music.

## Metadata

When **Preserve source metadata** is enabled, compatible tags are copied to the output container. Unsupported tags may be omitted by FFmpeg or the destination format. Disabling the option removes mapped source metadata from the output.

## Compatibility safeguards

MP4 Universal applies:

- H.264 video with `yuv420p` pixel format;
- AAC audio at 48 kHz stereo by default;
- `avc1` tagging;
- fast-start metadata placement;
- variable-frame-rate output handling;
- even-dimension scaling;
- primary-stream mapping;
- subtitle/data-stream exclusion;
- timestamp and negative-time normalization.

These defaults prioritize playback compatibility over preserving every source stream.
