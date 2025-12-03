# Container Guide

This document captures every gory detail required to build, run, and hack on the 3V web stack inside containers. It expands on the short README blurb and assumes you want to understand (and possibly customize) the full workflow.

## 1. Repository Layout Recap
```
3vee-server/
├── Dockerfile              # Builds the web image (Apache + PHP + Python2 stack + vossvolvox + headless Python renderer)
├── docker-compose.yml      # Orchestrates the web + MariaDB services
├── docker/entrypoint.sh    # Web container bootstrap (DB wait, sinedon config, maketables)
├── output/                 # Recommended host bind mount (job artifacts/logs)
├── php/                    # Web entry points + php/tests smoke scripts
├── py/                     # Python job runners, libs, and tests
└── vossvolvox/             # (optional) Only needed if you want to hack on the C++ sources locally
```

During the image build we automatically clone `https://github.com/vosslab/vossvolvox.git` inside the container and compile it, so the local checkout only matters if you plan to modify those sources yourself.

## 2. Prerequisites
- Modern container runtime:
  - **Docker** Engine ≥ 24 *or*
  - **Podman** ≥ 4 with Compose plug-in (`podman compose`) and, on macOS/Windows, a Podman machine/VM.
- CPU/RAM: ~2 GiB free RAM and ~5 GiB disk space (compiling `vossvolvox`, installing Python deps, MariaDB data volume).
- Internet access (the build downloads Debian packages, Python deps, etc.).

### Podman specifics
- On Linux, Podman can run rootless natively. On macOS/Windows, Podman spins up a VM; check with `podman machine ls`, start it via `podman machine start <name>` if it is stopped, and only run `podman machine init --now --user-mode-networking` when creating a new VM to ensure host ports forward into the guest.
- Rootless Podman cannot bind privileged ports (<1024). We expose Apache on 8080 by default, so rootless setups are fine.
- Compose plugin: install via `brew install podman podman-compose` (macOS) or the distro package (`dnf install podman-compose`, etc.).
- The repo ships `build_podman_image.sh` at the root. It wraps the common steps (stop the current stack, start the DB, rebuild/run the `web` container, and tee the logs to `logs/podman-compose-<timestamp>.log`), defaulting to the host architecture unless `ARCH` is set.

## 2.1 Quick Commands
Want the shortest path? Copy/paste the following (adjust for Docker vs Podman):

### Docker (Linux/macOS/Windows)
```bash
git clone https://github.com/vosslab/3vee-server.git
cd 3vee-server
mkdir -p output
./docker/prefetch-assets.sh
docker compose up --build
# open http://localhost:8080/php/volumeCalc.php
```

### Podman (Linux)
```bash
git clone https://github.com/vosslab/3vee-server.git
cd 3vee-server
mkdir -p output
./docker/prefetch-assets.sh
podman compose up --build
# open http://localhost:8080/php/volumeCalc.php
```

### Podman (macOS with VM)
```bash
brew install podman podman-compose
podman machine ls                      # check existing machines
podman machine init --now --user-mode-networking   # only if you need a new VM
podman machine start podman-machine-default   # start the VM if it's stopped
git clone https://github.com/vosslab/3vee-server.git
cd 3vee-server
mkdir -p output
./docker/prefetch-assets.sh
podman compose up --build
# open http://localhost:8080/php/volumeCalc.php
```

All three variants expose Apache on port 8080 and mount `./output` so results persist.

## 3. Building the Web Image
Both Docker and Podman respect the same `Dockerfile`. The build stage:
1. Uses `debian:trixie` (aka Debian 13) as the base.
2. Installs Apache, PHP, MariaDB client, Meshlab, ImageMagick, Xvfb, build tooling, and dev libraries.
3. Builds CPython `PY2_VERSION` (default `2.7.18`) from source under `/opt/python2`, then installs pinned legacy packages (`numpy==1.16.6`, `scipy==1.2.3`, `mysqlclient==1.4.6`, `Pillow==6.2.2`).
4. Clones `vossvolvox` (default branch `master`, override via `--build-arg VOSSVOLVOX_REF=<ref>`), builds the C++ tools, and copies the resulting `*.exe` binaries plus helper data/scripts into `/var/www/html/3vee/bin`, `/dat`, `/sh`.
5. Configures Apache with a single vhost pointed at `/var/www/html/3vee`.

Build command (Docker):
```bash
docker compose build web
```
Podman equivalent:
```bash
podman compose build web
```
If you want to build without Compose, run `docker build -t threev-web .` or `podman build -t threev-web .` but you’ll need to wire up the DB manually.

Need a specific revision? Build args:
- `VOSSVOLVOX_REF` / `VOSSVOLVOX_REPO` – clone a particular branch/tag or fork of vossvolvox (default ref `master`).

## 4. Runtime Topology
`docker-compose.yml` defines two services:

| Service | Image | Purpose |
| --- | --- | --- |
| `db` | `mariadb:10.6` | Standalone MariaDB instance seeded via standard env vars. Data lives in volume `db-data`. |
| `web` | locally built | Apache + PHP UI + Python job runners + vossvolvox binaries. Binds `./output` into `/var/www/html/3vee/output`. |

The MariaDB service now uses Compose’ `logging.driver: "none"` setting so its verbose startup messages stay out of `compose up` output; run `docker compose logs db` (or `podman compose logs db`) when you need to inspect the database logs.

Port mapping: `8080:80` (host → container). Adjust in `docker-compose.yml` if you already use 8080.

### Environment variables
The web container honors these variables (set them in Compose or via `docker run -e ...`):

| Variable | Default | Description |
| --- | --- | --- |
| `THREEV_DB_HOST` | `db` | MariaDB hostname/IP. The entrypoint rewrites `py/sinedon/sinedon.cfg` accordingly. |
| `THREEV_DB_NAME` | `threevdata` | Database to use/create. |
| `THREEV_DB_USER` | `vossman` | DB user. Must match the credentials configured on the DB service. |
| `THREEV_DB_PASSWORD` | `vossman` | DB password. |
| `THREEV_SKIP_DB_WAIT` | `0` | Set to `1` to skip waiting for the DB at startup. |
| `THREEV_SKIP_DB_INIT` | `0` | Set to `1` to skip running `python py/sinedon/maketables.py threevdata`. |

By default the entrypoint probes MariaDB with `mysql --skip-ssl --ssl-verify-server-cert=0`, waiting ~20 s between six attempts. This avoids SSL handshake hiccups commonly seen in Podman/Docker-for-mac environments; monitor `compose logs web` if you need to confirm the wait loop’s status.

The MariaDB service uses the standard `MARIADB_*` env vars to create the same database/user at first boot. Change both sides in tandem.

## 5. Running via Compose
1. Create a host directory for job output (optional but recommended):
   ```bash
   mkdir -p output
   ```
2. Start both services:
   ```bash
   docker compose up    # or: podman compose up
   ```
   Add `--build` the first time or whenever the Dockerfile changes.
3. Visit `http://localhost:8080/php/volumeCalc.php` (or any other PHP entry point). Job results show up under `output/<jobid>/` on the host.
4. Stop the stack with `Ctrl+C`. Add `-d` to run detached and `docker compose down` to stop/remove containers.

### Rootless Podman on macOS
- Use `podman machine ls` to confirm the default VM exists; start it via `podman machine start podman-machine-default` (or recreate with `podman machine init --now --user-mode-networking` if missing). User-mode networking forwards host ports such as 8080 automatically.
- `podman compose up` runs inside the Podman VM. Use `podman machine ssh` if you need to inspect files inside.
- Bind mounts (`./output`) live on the host; Podman syncs them via VirtFS. Large output directories can be slow—consider `podman volume create` and adjust the Compose file if needed.

## 6. One-off Commands & Debugging
- **Shell inside web container:** `docker compose exec web bash` (or `podman compose exec`). Useful for inspecting `/var/www/html/3vee/output`, Apache logs, etc.
- **Logs:** `docker compose logs -f web db` (tail both services). Apache logs live at `/var/log/apache2/3vee-error.log` inside the container.
- **Rebuilding after code changes:** rebuild the image (`docker compose build web`) then restart (`docker compose up`). The host bind mount means PHP/py code edits are visible immediately; rebuilding is only necessary when dependencies or the Dockerfile change.

## 7. Customizing the Stack
- **Changing the exposed port:** edit `docker-compose.yml`, replace `"8080:80"` with another mapping (e.g., `"8000:80"`). For Podman rootless you can also map to high ports per user preferences.
- **Custom DB credentials:** update both `docker-compose.yml` (environment for `db` + `web`) and, if you set `THREEV_SKIP_DB_INIT=1`, ensure the DB is initialized manually.
- Rendering is headless Python; no Chimera/EMAN required. If you install extra tools (e.g., for visualization), adjust the Dockerfile as needed.
- **Python runtime:** Debian packages install Python 3 plus `numpy`, `scipy`, `mysqlclient`, and `Pillow`. If you need different versions, adjust the apt/pip steps in the Dockerfile.

## 8. Security Notes
- The Chimera installer is fetched over HTTPS from its official distributor. Verify licensing fits your use case before redistributing the image.
- MariaDB credentials are stored in plain text inside `docker-compose.yml` for convenience. Supply secrets via environment variables or Docker secrets if deploying beyond local dev.
- The container runs Apache as `www-data`. Job outputs land in `/var/www/html/3vee/output`; ensure you trust inputs because PHP pages launch shell commands on submitted values.

## 9. Troubleshooting Checklist
| Symptom | Likely Cause | Fix |
| --- | --- | --- |
| `web` container exits immediately | DB not ready, wrong credentials | Check `docker compose logs web`, ensure `db` is healthy, verify `THREEV_DB_*` match `MARIADB_*`. |
| Jobs stay in “Preparing” state | Python process failed | Inspect `/var/www/html/3vee/output/<jobdir>/shell-*.log` inside `output/` or via `compose exec web`. |
| No images rendered | Chimera/Meshlab missing | Confirm `/opt/chimera/bin/chimera` exists (it should), check `chimeraRun.log`, ensure `xvfb` is installed. |
| Podman on macOS cannot reach localhost:8080 | Port forwarding disabled | Run `podman machine stop`, then `podman machine init --now --port-forwarding`. |

## 10. Manual `docker run` Example (Advanced)
If you prefer not to use Compose, run the DB and web containers manually:
```bash
# DB
docker run -d --name threev-db \
  -e MARIADB_ROOT_PASSWORD=rootpass \
  -e MARIADB_DATABASE=threevdata \
  -e MARIADB_USER=vossman \
  -e MARIADB_PASSWORD=vossman \
  -v threev-db-data:/var/lib/mysql \
  mariadb:10.6

# Web
docker run -d --name threev-web --link threev-db:db \
  -e THREEV_DB_HOST=db \
  -e THREEV_DB_NAME=threevdata \
  -e THREEV_DB_USER=vossman \
  -e THREEV_DB_PASSWORD=vossman \
  -p 8080:80 \
  -v $(pwd)/output:/var/www/html/3vee/output \
  threev-server_web:latest
```
Replace `threev-server_web:latest` with whatever tag `docker build` produced.

## 11. Updating the Base Image
When dependencies change (new Debian release, new Chimera, etc.):
1. Edit the Dockerfile URLs/versions.
2. `docker compose build --no-cache web` to rebuild from scratch.
3. `docker compose up` to redeploy. Remember to recreate the DB container if the schema or credentials change (`docker compose down -v`).

## 12. Cleanup
- Stop stack: `docker compose down` (add `-v` to delete DB data volume).
- Remove dangling images: `docker image prune` (or `podman image prune`).
- Reset Podman VM: `podman machine stop; podman machine rm; podman machine init --now`.

With these steps you should be able to build and run the entire 3V web workflow in either Docker or Podman, rootless or otherwise.
