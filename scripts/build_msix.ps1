param(
  [switch]$SkipStandalone
)

$ErrorActionPreference = "Stop"
$PSNativeCommandUseErrorActionPreference = $true
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

if (-not $SkipStandalone) {
  & (Join-Path $PSScriptRoot "build_windows.ps1")
}

$Standalone = Join-Path $Root "build/windows/BlakeLabsMultimedia"
if (-not (Test-Path $Standalone)) {
  throw "Windows standalone application was not found: $Standalone"
}

$BuildRoot = Join-Path $Root "build/msix"
$Layout = Join-Path $BuildRoot "layout"
$AppDirectory = Join-Path $Layout "App"
$AssetsDirectory = Join-Path $Layout "Assets"
$Output = Join-Path $BuildRoot "BlakeLabsMultimedia-Store-x64.msix"

if (Test-Path $BuildRoot) {
  Remove-Item $BuildRoot -Recurse -Force
}
New-Item -ItemType Directory -Path $AppDirectory | Out-Null
New-Item -ItemType Directory -Path $AssetsDirectory | Out-Null

Copy-Item (Join-Path $Standalone "*") $AppDirectory -Recurse -Force

uv run python scripts/generate_msix_assets.py --output $AssetsDirectory
uv run python scripts/render_msix_manifest.py `
  --template installer/msix/AppxManifest.xml.template `
  --project pyproject.toml `
  --output (Join-Path $Layout "AppxManifest.xml")

$KitsRoot = Join-Path ${env:ProgramFiles(x86)} "Windows Kits/10/bin"
if (-not (Test-Path $KitsRoot)) {
  throw "Windows SDK was not found at $KitsRoot"
}

$MakeAppx = Get-ChildItem -Path $KitsRoot -Filter makeappx.exe -Recurse |
  Where-Object { $_.Directory.Name -eq "x64" } |
  Sort-Object {
    try {
      [version]$_.Directory.Parent.Name
    }
    catch {
      [version]"0.0.0.0"
    }
  } -Descending |
  Select-Object -First 1

if ($null -eq $MakeAppx) {
  throw "MakeAppx.exe was not found in the installed Windows SDK."
}

& $MakeAppx.FullName pack /o /v /d $Layout /p $Output
if ($LASTEXITCODE -ne 0 -or -not (Test-Path $Output)) {
  throw "MakeAppx failed to create the Microsoft Store package."
}

$Hash = Get-FileHash $Output -Algorithm SHA256
Write-Host "Unsigned Microsoft Store package: $Output"
Write-Host "SHA256: $($Hash.Hash)"
