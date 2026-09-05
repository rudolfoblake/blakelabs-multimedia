# Jellyfin Docker

Portable Jellyfin setup for BlakeLabs Multimedia. The same Compose file is designed to run on Docker Desktop for Windows and on Docker Compose for Linux/macOS.

## What is persistent

Jellyfin application state is stored in Docker named volumes:

- `blakelabs-jellyfin-config` -> Jellyfin configuration and database
- `blakelabs-jellyfin-cache` -> cache and transcoding data

Your media files are never copied into Docker. Host folders are bind-mounted **read-only** into the container.

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
JELLYFIN_MOVIES_PATH=D:/Media/Movies
JELLYFIN_SERIES_PATH=E:/Series
JELLYFIN_MUSIC_PATH=F:/Music
JELLYFIN_OTHER_MEDIA_PATH=G:/Media
```

If a path contains spaces, quote the value:

```dotenv
JELLYFIN_MOVIES_PATH="D:/My Movies"
```

Then start Jellyfin:

```powershell
docker compose --env-file docker/jellyfin/.env -f docker/jellyfin/compose.yml up -d
```

Open:

```text
http://localhost:8096
```

During Jellyfin's setup wizard, point each library to `/media/movies`, `/media/series`, `/media/music`, or `/media/other`. The Windows drive letters never need to be entered inside Jellyfin itself.

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

Stop while keeping Jellyfin settings:

```bash
docker compose --env-file docker/jellyfin/.env -f docker/jellyfin/compose.yml down
```

View logs:

```bash
docker compose --env-file docker/jellyfin/.env -f docker/jellyfin/compose.yml logs -f jellyfin
```

Update the image and restart:

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
3. Change only the host-side path, for example `D:/Media/Movies` to `H:/Movies`.
4. Run `docker compose ... up -d` again.

The container path stays `/media/movies`, so the Jellyfin library does not need to be redesigned every time a Windows drive letter changes.

## Local fallback directories

The example environment file defaults to folders under `docker/jellyfin/runtime/media`. This lets the Compose project start even before real disks are configured. The runtime directory and local `.env` are intentionally ignored by Git.

## Ports

- `8096/tcp` -> Jellyfin web UI and HTTP API
- `7359/udp` -> local-network client discovery

Both published ports can be changed in `.env` without editing the Compose file.

## Important Docker Desktop note

Docker Desktop must be allowed to access the Windows folder/drive used in each bind mount. If Docker reports that a media path cannot be mounted, verify that the drive exists, the folder is accessible to the current Windows user, and Docker Desktop has permission to use it.

## Removing everything

Normal `down` keeps your Jellyfin configuration. To deliberately remove the Jellyfin Docker volumes as well:

```bash
docker compose --env-file docker/jellyfin/.env -f docker/jellyfin/compose.yml down -v
```

Do not use `-v` unless you intend to delete Jellyfin's Docker-managed configuration/cache for this stack.
