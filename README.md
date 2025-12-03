# 3vee-server
Web server for 3v: voss volume voxelator

For a deep technical walkthrough of the stack (PHP UI, Python job layer, vossvolvox binaries, and MariaDB logging) see [ARCHITECTURE.md](ARCHITECTURE.md).

## Containerized Web Server

You can spin up the full stack (Apache + PHP UI, Python 3 job runners, MariaDB, headless Python rendering, and the freshly built `vossvolvox` binaries) with Docker or Podman. The container builds on Debian 13 “trixie”, installs Python 3.11 from the distro, and pulls the required scientific/DB bindings from the Debian packages (`python3-numpy`, `python3-scipy`, `python3-mysqldb`, `python3-pil`, etc.).

### Prerequisites
- Docker Engine 24+ **or** Podman 4+ with Compose support.
- Enough RAM/disk to compile `vossvolvox` and run MariaDB (2 GiB free is plenty).

### Build & Run
```bash
# from the repo root
mkdir -p output                      # persist job artifacts on the host
docker compose up --build            # or: podman compose up --build
```

When you want to rebuild the web image via Podman (e.g., on macOS where the VM is already running) there is also `build_podman_image.sh` in the repo root; it tears down the existing containers, starts MariaDB in the background, and builds/runs the `web` container while streaming logs to `logs/podman-compose-<timestamp>.log`. See [CONTAINER.md](CONTAINER.md) for the full Podman workflow, including VM setup and port-forwarding tips.

The compose file exposes Apache on port `8080`, so the UI is available at `http://localhost:8080/php/volumeCalc.php` (and the other PHP entry points under `/php`). Jobs write into `output/` which is bind-mounted so logs/results survive container rebuilds.

### What the containers do
- `web`: built from the included `Dockerfile`. It installs Apache + PHP, Python 3 with `numpy/scipy/MySQLdb`, builds the bundled `vossvolvox` sources, installs the helper scripts/data expected by `ThreeVLib`, rewrites `py/sinedon/sinedon.cfg` based on `THREEV_DB_*` variables, boots Apache, and automatically runs `py/sinedon/maketables.py threevdata` against the DB on startup.
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

Use `podman compose` instead of `docker compose` if you prefer Podman—the files are compatible. The stack is pure Python for rendering and no longer depends on Chimera or EMAN, so you can build natively on arm64 or amd64; set `ARCH` in `build_podman_image.sh` only if you need to override.

The `web` container’s entrypoint probes MariaDB with `mysql --skip-ssl --ssl-verify-server-cert=0`, sleeping ~20 s between attempts (six tries total). Leave the defaults unless you have custom SSL needs; otherwise, keep an eye on `podman compose logs web` to ensure the DB is ready before Apache starts serving traffic.

## macOS x86_64 Podman via QEMU

Apple Silicon hosts may still run amd64 containers for parity. Install `podman`, `podman-compose`, and `qemu` via Homebrew, initialize a machine (`podman machine init --now --user-mode-networking`), and keep it running with `podman machine start podman-machine-default`. Use `ARCH=amd64` in `build_podman_image.sh` only if you explicitly want cross-arch builds; otherwise native arm64 works end to end. For a full checklist on preparing that machine, see `MACOS_PODMAN_QEMU.md`.

## Local Python tooling

If you run the Python job layer on a host (for linting, debugging, or manual runs), install the dependencies listed in `py/requirements.txt`. The explicit Python packages managed by that requirements file are:

```
numpy
pymysql
scipy
six
DateTime
scikit-image
matplotlib
```

```bash
cd py
pip3 install -r requirements.txt
```

The repo also provides lightweight defaults for the Python-side configs (`py/sinedon/sinedon.cfg` and `py/pyami/pyami.cfg`) so you can execute `tests/run_pyflakes.sh` and `tests/check.sh` without a real database. Feel free to replace those config stubs with your own credentials if you want to point at an actual MariaDB or instrument configuration.

> **Note:** Rendering is now handled by pure Python tooling (NumPy/SciPy/scikit-image/matplotlib); Chimera and EMAN are no longer bundled or required.

Useful build arguments:
- `VOSSVOLVOX_REF` (default `master`) and `VOSSVOLVOX_REPO` to check out a specific vossvolvox branch/tag/fork.
`tests/check.sh` and `tests/run_pyflakes.sh` automatically write temporary copies of `py/sinedon/sinedon.cfg`, `py/pyami/pyami.cfg`, and `py/pymysql.py` before running, then delete them when the script ends, so you do not need to commit those files to the repo.
