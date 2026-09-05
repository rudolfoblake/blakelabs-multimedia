# Jellyfin Docker

Portable Jellyfin setup for BlakeLabs Multimedia. The same Compose file is designed to run on Docker Desktop for Windows and on Docker Compose for Linux/macOS.

The Compose project also includes an optional-but-ready media automation/request stack: **Seerr + Radarr + Sonarr + Prowlarr + qBittorrent**. See [`ARR_STACK.md`](./ARR_STACK.md) for the minimal first-run wiring. Jellyfin's existing persistence and read-only media mounts are preserved.

## What is persistent

Jellyfin application state is stored in Docker named volumes:

- `blakelabs-jellyfin-config` -> Jellyfin configuration and database
- `blakelabs-jellyfin-cache` -> cache and transcoding data

The automation services also use their own named config volumes. Normal `docker compose down` keeps them all.

Your media files are never copied into the Jellyfin container. Host folders are bind-mounted **read-only** into Jellyfin. Radarr/Sonarr receive write access only to their corresponding host library folder so they can import completed downloads.

Inside Jellyfin the library paths are always:

| Library | Container path | Host setting |
| --- | --- | --- |
| Movies | `/media/movies` | `JELLYFIN_MOVIES_PATH` |
| Series | `/media/series` | `JELLYFIN_SERIES_PATH` |
| Music | `/media/music` | `JELLYFIN_MUSIC_PATH` |
| Other | `/media/other` | `JELLYFIN_OTHER_MEDIA_PATH` |

## First run on Windows

From the repository root in PowerShell:

```powershell
Copy-Item docker/jellyfin/.env.example docker/jellyfin/.env
notepad docker/jellyfin/.env
```

Set the paths for the drives/folders on that machine. Use forward slashes:

```dotenv
JELLYFIN_MOVIES_PATH=D:/Movies
JELLYFIN_SERIES_PATH=D:/Series
JELLYFIN_MUSIC_PATH=D:/Music
JELLYFIN_OTHER_MEDIA_PATH=D:/Other
DOWNLOADS_PATH=D:/Downloads
```

If a path contains spaces, quote the value:

```dotenv
JELLYFIN_MOVIES_PATH="D:/My Movies"
```

Then start the stack:

```powershell
docker compose --env-file docker/jellyfin/.env -f docker/jellyfin/compose.yml up -d
```

Jellyfin:

```text
http://localhost:8096
```

During Jellyfin's setup wizard, point each library to `/media/movies`, `/media/series`, `/media/music`, or `/media/other`. The Windows drive letters never need to be entered inside Jellyfin itself.

For Seerr/Radarr/Sonarr/Prowlarr/qBittorrent first-run setup, follow [`ARR_STACK.md`](./ARR_STACK.md).

## Linux/macOS example

```bash
cp docker/jellyfin/.env.example docker/jellyfin/.env
```

Example paths:

```dotenv
JELLYFIN_MOVIES_PATH=/mnt/media/movies
JELLYFIN_SERIES_PATH=/mnt/media/series
JELLYFIN_MUSIC_PATH=/mnt/media/music
JELLYFIN_OTHER_MEDIA_PATH=/mnt/media/other
DOWNLOADS_PATH=/mnt/media/downloads
```

Start with the same Compose command:

```bash
docker compose --env-file docker/jellyfin/.env -f docker/jellyfin/compose.yml up -d
```

## Everyday commands

Start or recreate:

```bash
docker compose --env-file docker/jellyfin/.env -f docker/jellyfin/compose.yml up -d
```

Stop while keeping settings:

```bash
docker compose --env-file docker/jellyfin/.env -f docker/jellyfin/compose.yml down
```

View Jellyfin logs:

```bash
docker compose --env-file docker/jellyfin/.env -f docker/jellyfin/compose.yml logs -f jellyfin
```

Update images and restart:

```bash
docker compose --env-file docker/jellyfin/.env -f docker/jellyfin/compose.yml pull
docker compose --env-file docker/jellyfin/.env -f docker/jellyfin/compose.yml up -d
```

Check status:

```bash
docker compose --env-file docker/jellyfin/.env -f docker/jellyfin/compose.yml ps
```

## Changing disks later

1. Stop the stack with `docker compose ... down`.
2. Edit `docker/jellyfin/.env`.
3. Change only the host-side path, for example `D:/Movies` to `H:/Movies`.
4. Run `docker compose ... up -d` again.

The Jellyfin container paths stay stable, so the Jellyfin libraries do not need to be redesigned every time a Windows drive letter changes.

## Local fallback directories

The example environment file defaults to folders under `docker/jellyfin/runtime`. This lets the Compose project start even before real disks are configured. The runtime directory and local `.env` are intentionally ignored by Git.

## Ports

- `8096/tcp` -> Jellyfin web UI and HTTP API
- `7359/udp` -> Jellyfin local-network discovery
- `5055/tcp` -> Seerr
- `7878/tcp` -> Radarr
- `8989/tcp` -> Sonarr
- `9696/tcp` -> Prowlarr
- `8080/tcp` -> qBittorrent Web UI
- `6881/tcp+udp` -> qBittorrent incoming torrent traffic

Published ports can be changed in `.env` without editing the Compose file.

## Important Docker Desktop note

Docker Desktop must be allowed to access the Windows folder/drive used in each bind mount. If Docker reports that a media path cannot be mounted, verify that the drive exists, the folder is accessible to the current Windows user, and Docker Desktop has permission to use it.

## Removing everything

Normal `down` keeps all named configuration volumes. To deliberately remove Docker-managed application state as well:

```bash
docker compose --env-file docker/jellyfin/.env -f docker/jellyfin/compose.yml down -v
```

Do not use `-v` unless you intentionally want to delete the configuration/database state for this stack.
