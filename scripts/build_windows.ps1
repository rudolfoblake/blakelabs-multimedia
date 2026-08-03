$ErrorActionPreference = "Stop"
$PSNativeCommandUseErrorActionPreference = $true
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

uv sync --group build
uv run python scripts/fetch_ffmpeg.py --platform windows

$Version = uv run python -c "import tomllib; print(tomllib.load(open('pyproject.toml','rb'))['project']['version'])"
$BuildRoot = Join-Path $Root "build/windows"
$BrandingRoot = Join-Path $Root "build/branding"
$Icon = Join-Path $BrandingRoot "BlakeLabsMultimedia.ico"
$RuntimeRoot = Join-Path $Root "src/blakelabs_multimedia/resources/bin/windows-x64"
$Ffmpeg = Join-Path $RuntimeRoot "ffmpeg.exe"
$Ffprobe = Join-Path $RuntimeRoot "ffprobe.exe"

foreach ($Binary in @($Ffmpeg, $Ffprobe)) {
  if (-not (Test-Path -LiteralPath $Binary -PathType Leaf)) {
    throw "Required FFmpeg runtime was not downloaded: $Binary"
  }
}

if (Test-Path $BuildRoot) { Remove-Item $BuildRoot -Recurse -Force }
New-Item -ItemType Directory -Path $BuildRoot | Out-Null
New-Item -ItemType Directory -Path $BrandingRoot -Force | Out-Null
uv run python -m scripts.generate_windows_icon --output $Icon

uv run python -m nuitka `
  --standalone `
  --assume-yes-for-downloads `
  --enable-plugin=pyside6 `
  --include-qt-plugins=qml `
  --include-data-dir=src/blakelabs_multimedia/presentation/qml=blakelabs_multimedia/presentation/qml `
  --include-data-dir=src/blakelabs_multimedia/resources=blakelabs_multimedia/resources `
  --include-data-files="$Ffmpeg=blakelabs_multimedia/resources/bin/windows-x64/ffmpeg.exe" `
  --include-data-files="$Ffprobe=blakelabs_multimedia/resources/bin/windows-x64/ffprobe.exe" `
  --windows-console-mode=disable `
  --windows-icon-from-ico=$Icon `
  --company-name="Blake Labs" `
  --product-name="BlakeLabs Multimedia" `
  --file-description="Professional local audio and video converter" `
  --copyright="Copyright © 2026 Blake Labs" `
  --file-version="$Version.0" `
  --product-version="$Version.0" `
  --output-filename=BlakeLabsMultimedia.exe `
  --output-dir=$BuildRoot `
  src/blakelabs_multimedia/__main__.py

$Generated = Join-Path $BuildRoot "__main__.dist"
$Product = Join-Path $BuildRoot "BlakeLabsMultimedia"
if (-not (Test-Path $Generated)) { throw "Nuitka output directory was not created: $Generated" }
if (Test-Path $Product) { Remove-Item $Product -Recurse -Force }
Move-Item $Generated $Product

$PackagedRuntime = Join-Path $Product "blakelabs_multimedia/resources/bin/windows-x64"
$PackagedFfmpeg = Join-Path $PackagedRuntime "ffmpeg.exe"
$PackagedFfprobe = Join-Path $PackagedRuntime "ffprobe.exe"
foreach ($Binary in @($PackagedFfmpeg, $PackagedFfprobe)) {
  if (-not (Test-Path -LiteralPath $Binary -PathType Leaf)) {
    throw "Required FFmpeg runtime is missing from packaged application: $Binary"
  }
}

& $PackagedFfprobe -hide_banner -version | Select-Object -First 1
if ($LASTEXITCODE -ne 0) { throw "Packaged ffprobe could not execute" }
& $PackagedFfmpeg -hide_banner -version | Select-Object -First 1
if ($LASTEXITCODE -ne 0) { throw "Packaged ffmpeg could not execute" }

Write-Host "Standalone application with bundled FFmpeg runtime: $Product"
