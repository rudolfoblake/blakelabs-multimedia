# Microsoft Store distribution

BlakeLabs Multimedia is registered in Partner Center as an **MSIX or PWA app**.

## Store identity

These values are public package identifiers assigned by Microsoft and must match the package manifest exactly.

```text
Package/Identity/Name: BlakeLabs.blakelabs-multimedia
Package/Identity/Publisher: CN=46D61F1C-6866-4226-8C25-634333289A47
Package/Properties/PublisherDisplayName: Blake Labs
Package Family Name: BlakeLabs.blakelabs-multimedia_3afs07e5hvyyg
Store ID: 9NS1J3D51RFX
Store URL: https://apps.microsoft.com/detail/9NS1J3D51RFX
```

Do not put Partner Center passwords, access tokens, client secrets, certificates, PFX files or private keys in the repository.

## Build the Store package

Run on Windows with the Windows SDK installed:

```powershell
./scripts/build_msix.ps1
```

The script:

1. Builds the existing Nuitka standalone application.
2. Copies the standalone tree into an isolated MSIX layout.
3. Generates the Blake Labs Store logo assets.
4. Converts the project version to the required four-part MSIX version.
5. Renders `AppxManifest.xml` with the assigned Store identity.
6. Uses the newest x64 `MakeAppx.exe` found in the Windows SDK.
7. Produces `build/msix/BlakeLabsMultimedia-Store-x64.msix`.

The generated package is intentionally unsigned. Upload it to Partner Center; Microsoft signs the package after successful certification. It cannot be directly sideloaded on a normal Windows installation until it has a trusted signature.

## Manifest model

The desktop application is declared as a full-trust packaged classic app:

```xml
<Application
  Id="App"
  Executable="App\BlakeLabsMultimedia.exe"
  uap10:RuntimeBehavior="packagedClassicApp"
  uap10:TrustLevel="mediumIL" />
```

The package declares the restricted `runFullTrust` capability because the application executes FFmpeg and FFprobe as local child processes and accesses user-selected media files.

## Partner Center checklist

Upload the generated `.msix` under **Packages**. Complete the submission sections before certification:

- Pricing and availability
- Properties
- Age ratings
- Packages
- Store listings
- Submission options

In **Submission options**, review the restricted-capability declaration and add a certification note explaining that `runFullTrust` is required for a native PySide6 desktop multimedia application that invokes bundled FFmpeg/FFprobe processes and only processes files explicitly selected by the user.

## Versioning

`[project].version` in `pyproject.toml` is the source of truth. The build converts values such as `0.2.0` into `0.2.0.0` for the MSIX manifest.

Every package submitted to the same Store product must have a version greater than the previously accepted package version. Keep versions numeric and use at most four components.

## Display name

The package-level display name currently uses the reserved name `blakelabs-multimedia`. Reserve `BlakeLabs Multimedia` under **Manage app names** before changing the package-level `DisplayName` to the prettier capitalization.
