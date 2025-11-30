# 3vee-server
Web server for 3v: voss volume voxelator

For a deep technical walkthrough of the stack (PHP UI, Python job layer, vossvolvox binaries, and MariaDB logging) see [ARCHITECTURE.md](ARCHITECTURE.md).

## Containerized Web Server

You can spin up the full stack (Apache + PHP UI, Python job runners, MariaDB, and the freshly built `vossvolvox` binaries) with Docker or Podman.

### Prerequisites
- Docker Engine 24+ **or** Podman 4+ with Compose support.
- Enough RAM/disk to compile `vossvolvox` and run MariaDB (2 GiB free is plenty).

### Build & Run
Ensure the VossVolvox sources are checked out inside this repository (the Dockerfile calls `make -C vossvolvox/src all`):
```bash
git clone https://github.com/vosslab/vossvolvox.git vossvolvox
```

```bash
# from the repo root
mkdir -p output                      # persist job artifacts on the host
docker compose up --build            # or: podman compose up --build
```

The compose file exposes Apache on port `8080`, so the UI is available at `http://localhost:8080/php/volumeCalc.php` (and the other PHP entry points under `/php`). Jobs write into `output/` which is bind-mounted so logs/results survive container rebuilds.

### What the containers do
- `web`: built from the included `Dockerfile`. It installs Apache + PHP, Python 2 with `numpy/scipy/MySQLdb`, builds the bundled `vossvolvox` sources, installs the helper scripts/data expected by `ThreeVLib`, rewrites `sinedon/sinedon.cfg` based on `THREEV_DB_*` variables, boots Apache, and automatically runs `sinedon/maketables.py threevdata` against the DB on startup.
- `db`: vanilla `mariadb:10.6` with credentials defined in `docker-compose.yml`. Data lives in the named volume `db-data`.

### Environment overrides
You can control how the web container connects to MariaDB via the following environment variables (set them in `docker-compose.yml` or when invoking `docker compose`):

| Variable | Default | Purpose |
| --- | --- | --- |
| `THREEV_DB_HOST` | `db` | Hostname/IP of MariaDB |
| `THREEV_DB_NAME` | `threevdata` | Database name to use/create |
| `THREEV_DB_USER` | `vossman` | Database user |
| `THREEV_DB_PASSWORD` | `vossman` | Password for the DB user |
| `THREEV_SKIP_DB_WAIT` | `0` | Set to `1` to skip the startup wait-for-DB loop |
| `THREEV_SKIP_DB_INIT` | `0` | Set to `1` to skip running `maketables.py` on boot |

Use `podman compose` instead of `docker compose` if you prefer Podman—the files are compatible.

> **Note:** The Docker build automatically downloads and installs UCSF Chimera 1.19 (OSMesa build) into `/opt/chimera` and exports `CHIMERA=/opt/chimera` so the Python imaging helpers can find it. Make sure you are licensed/permitted to use Chimera in this manner in your environment. EMAN/`proc3d` is still not bundled; mount or install it separately if you need those features.
