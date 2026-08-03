# BlakeLabs Multimedia Privacy Policy

**Effective date:** August 2, 2026

BlakeLabs Multimedia is a desktop media-conversion application published by Blake Labs. This policy describes how the application handles information.

## Media files

BlakeLabs Multimedia processes selected audio and video files locally on the user's computer. The application does not upload media to Blake Labs or to a third-party cloud service.

## Accounts and personal information

The application does not require a Blake Labs account. The current version does not include advertising, analytics SDKs, behavioral tracking or cloud synchronization.

## Local settings

The application stores limited preferences on the device, such as:

- selected output preset;
- advanced conversion settings;
- selected output directory.

These preferences remain in the operating system's application-settings storage.

## Diagnostic logs

The application creates rotating diagnostic logs locally to help diagnose failures. Logs may contain:

- application and processing events;
- FFmpeg error output;
- local input and output file paths;
- selected preset identifiers.

Diagnostic logs are not transmitted automatically. Users choose whether to share log excerpts when requesting support. Logs should be reviewed before sharing because local paths can contain personal information.

## Third-party components

BlakeLabs Multimedia uses FFmpeg and Qt/PySide. These components run as part of the local application. Their license notices are documented in `THIRD_PARTY_NOTICES.md`.

## Data retention and deletion

Media remains wherever the user stores it. Converted output remains in the selected destination. Temporary output is removed after cancellation or failure when possible.

Users can remove local preferences and logs by uninstalling the application and deleting its application-data directory. The exact directory depends on the operating system.

## Changes

This policy may be updated when application capabilities change. Material changes should be reflected by a new effective date.

## Contact

Privacy or support questions may be submitted through the BlakeLabs Multimedia GitHub repository or the support channel listed on the Microsoft Store product page.

> This document is a product policy template and should receive appropriate legal review before commercial launch in additional jurisdictions.
