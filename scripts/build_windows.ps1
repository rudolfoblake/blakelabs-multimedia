$ErrorActionPreference = "Stop"
$PSNativeCommandUseErrorActionPreference = $true
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

uv sync --group build
uv run python scripts/fetch_ffmpeg.py --platform windows

$BuildRoot = Join-Path $Root "build/windows"
if (Test-Path $BuildRoot) { Remove-Item $BuildRoot -Recurse -Force }
New-Item -ItemType Directory -Path $BuildRoot | Out-Null

uv run python -m nuitka `
  --standalone `
  --assume-yes-for-downloads `
  --enable-plugin=pyside6 `
  --include-qt-plugins=qml `
  --include-data-dir=src/blakelabs_multimedia/presentation/qml=blakelabs_multimedia/presentation/qml `
  --include-data-dir=src/blakelabs_multimedia/resources=blakelabs_multimedia/resources `
  --windows-console-mode=disable `
  --output-filename=BlakeLabsMultimedia.exe `
  --output-dir=$BuildRoot `
  src/blakelabs_multimedia/__main__.py

$Generated = Join-Path $BuildRoot "__main__.dist"
$Product = Join-Path $BuildRoot "BlakeLabsMultimedia"
if (-not (Test-Path $Generated)) { throw "Nuitka output directory was not created: $Generated" }
if (Test-Path $Product) { Remove-Item $Product -Recurse -Force }
Move-Item $Generated $Product
Write-Host "Standalone application: $Product"
