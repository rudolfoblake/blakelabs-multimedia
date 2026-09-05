$ErrorActionPreference = 'Stop'

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot '..\..\..')
$compose = Join-Path $repoRoot 'docker\jellyfin\compose.yml'
$envFile = Join-Path $repoRoot 'docker\jellyfin\.env'

$composeArgs = @('-f', $compose)
if (Test-Path $envFile) {
    $composeArgs = @('--env-file', $envFile) + $composeArgs
}

Write-Host "=== BlakeLabs Media Stack ===" -ForegroundColor Cyan
docker compose @composeArgs ps

Write-Host "`nLocal UIs" -ForegroundColor Cyan
Write-Host "Jellyfin    http://localhost:8096"
Write-Host "Seerr       http://localhost:5055"
Write-Host "Radarr      http://localhost:7878"
Write-Host "Sonarr      http://localhost:8989"
Write-Host "Prowlarr    http://localhost:9696"
Write-Host "qBittorrent http://localhost:8080"

Write-Host "`nPersistent volumes" -ForegroundColor Cyan
@(
    'blakelabs-jellyfin-config',
    'blakelabs-jellyfin-cache',
    'blakelabs-qbittorrent-config',
    'blakelabs-radarr-config',
    'blakelabs-sonarr-config',
    'blakelabs-prowlarr-config',
    'blakelabs-seerr-config'
) | ForEach-Object {
    $exists = docker volume ls -q --filter "name=^$($_)$"
    if ($exists) { Write-Host "[OK] $_" } else { Write-Host "[--] $_" }
}

Write-Host "`nqBittorrent first-run credential hint" -ForegroundColor Cyan
$qb = docker ps -aq --filter 'name=^/blakelabs-qbittorrent$'
if ($qb) {
    docker logs blakelabs-qbittorrent 2>&1 | Select-String -Pattern 'password|temporary' -CaseSensitive:$false | Select-Object -Last 8
} else {
    Write-Host 'qBittorrent container has not been created yet.'
}
