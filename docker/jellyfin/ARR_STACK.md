# BlakeLabs Media Automation Stack

This extends the existing Jellyfin deployment without changing Jellyfin persistence or media paths.

## Services

| Service | Purpose | Local URL |
| --- | --- | --- |
| Jellyfin | Media server | http://localhost:8096 |
| Seerr | Request/discovery UI for Jellyfin | http://localhost:5055 |
| Radarr | Movie library automation | http://localhost:7878 |
| Sonarr | Series library automation | http://localhost:8989 |
| Prowlarr | Indexer manager/proxy | http://localhost:9696 |
| qBittorrent | Torrent download client | http://localhost:8080 |

Use the torrent/download components only for content you are authorized to obtain and share.

## Data flow

```text
Seerr
  -> Radarr (movies) / Sonarr (series)
  -> Prowlarr (indexer management)
  -> qBittorrent (downloads)
  -> host Movies / Series folders
  -> Jellyfin sees the same host folders read-only
```

The Compose network lets services talk to one another using service names instead of host IP addresses.

## Persistence

All application state is kept outside the containers in named volumes:

- `blakelabs-jellyfin-config`
- `blakelabs-jellyfin-cache`
- `blakelabs-qbittorrent-config`
- `blakelabs-radarr-config`
- `blakelabs-sonarr-config`
- `blakelabs-prowlarr-config`
- `blakelabs-seerr-config`

Normal `docker compose down` keeps all of these. Do not use `down -v` unless you intentionally want to delete application state.

## Host folders

Radarr and Jellyfin share the same movie host folder:

- Radarr: `/movies` (read/write)
- Jellyfin: `/media/movies` (read-only)

Sonarr and Jellyfin share the same series host folder:

- Sonarr: `/tv` (read/write)
- Jellyfin: `/media/series` (read-only)

qBittorrent, Radarr, and Sonarr share the same download folder as `/downloads`.

On the current Windows machine the intended layout is typically:

```dotenv
JELLYFIN_MOVIES_PATH=D:/Movies
JELLYFIN_SERIES_PATH=D:/Series
JELLYFIN_MUSIC_PATH=D:/Music
DOWNLOADS_PATH=D:/Downloads
```

## Start everything

From the repository root:

```powershell
docker compose --env-file docker/jellyfin/.env -f docker/jellyfin/compose.yml pull
docker compose --env-file docker/jellyfin/.env -f docker/jellyfin/compose.yml up -d
```

Check:

```powershell
docker compose --env-file docker/jellyfin/.env -f docker/jellyfin/compose.yml ps
```

## Minimum first-run configuration

The containers, networking, ports, persistent volumes, and shared paths are already configured by the repository. The remaining UI setup is intentionally limited to credentials/API keys and the indexers you are legally entitled to use.

### 1. qBittorrent

Open `http://localhost:8080`.

LinuxServer's qBittorrent image prints the temporary Web UI password in its startup logs. Retrieve it with:

```powershell
docker logs blakelabs-qbittorrent 2>&1 | Select-String -Pattern "password|temporary" -CaseSensitive:$false
```

Log in and set a permanent Web UI password.

Recommended categories:

- `radarr`
- `sonarr`

Both use `/downloads` inside the containers.

### 2. Radarr

Open `http://localhost:7878`.

Set the root folder to:

```text
/movies
```

Add qBittorrent as the download client using Docker-internal networking:

```text
Host: qbittorrent
Port: 8080
Category: radarr
```

Use the qBittorrent username/password you set in step 1.

The Radarr API key is under **Settings -> General -> Security**. You will use it in Prowlarr and Seerr.

### 3. Sonarr

Open `http://localhost:8989`.

Set the root folder to:

```text
/tv
```

Add qBittorrent:

```text
Host: qbittorrent
Port: 8080
Category: sonarr
```

The Sonarr API key is under **Settings -> General -> Security**.

### 4. Prowlarr

Open `http://localhost:9696`.

Add only indexers you are authorized to use.

Then add the applications:

```text
Radarr URL: http://radarr:7878
Sonarr URL: http://sonarr:8989
```

Paste each application's API key. Prowlarr can then synchronize the selected indexers to Radarr and Sonarr.

### 5. Seerr

Open `http://localhost:5055` and choose Jellyfin during onboarding.

Because Seerr and Jellyfin are on the same Compose network, use:

```text
Jellyfin internal URL: http://jellyfin:8096
```

Sign in with a Jellyfin administrator account and select the movie/series libraries.

Add the download-management services using:

```text
Radarr host: radarr
Radarr port: 7878
Sonarr host: sonarr
Sonarr port: 8989
SSL: off for these internal Docker connections
```

Paste the Radarr and Sonarr API keys, select their root folders and quality profiles, and mark each as the default server.

Once that is done, requests in Seerr flow to Radarr/Sonarr and completed imports appear automatically in the same host folders already scanned by Jellyfin.

## Internal service addresses

Do not use `localhost` when one container talks to another. Use these names:

```text
http://jellyfin:8096
http://seerr:5055
http://radarr:7878
http://sonarr:8989
http://prowlarr:9696
http://qbittorrent:8080
```

`localhost` is only for opening each UI from the Windows host/browser.

## Update

```powershell
docker compose --env-file docker/jellyfin/.env -f docker/jellyfin/compose.yml pull
docker compose --env-file docker/jellyfin/.env -f docker/jellyfin/compose.yml up -d
```

## Stop without losing configuration

```powershell
docker compose --env-file docker/jellyfin/.env -f docker/jellyfin/compose.yml down
```

## Important

Never use the following casually:

```powershell
docker compose --env-file docker/jellyfin/.env -f docker/jellyfin/compose.yml down -v
```

The `-v` option deletes named volumes and therefore application configuration/database state.
