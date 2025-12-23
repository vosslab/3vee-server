# 3vee-server
Web server for 3v: voss volume voxelator

For a deep technical walkthrough of the stack (PHP UI, Python job layer, vossvolvox binaries, and MariaDB logging) see [docs/CODE_ARCHITECTURE.md](docs/CODE_ARCHITECTURE.md).

## Containerized Web Server

You can spin up the full stack (Apache + PHP UI, Python 3 job runners, MariaDB, headless Python rendering, and the freshly built `vossvolvox` binaries) with Docker or Podman. The container builds on Debian 13 “trixie”, installs Python 3.11 from the distro, and pulls the required scientific/DB bindings from the Debian packages (`python3-numpy`, `python3-scipy`, `python3-mysqldb`, `python3-pil`, etc.).

### Prerequisites
- Docker Engine 24+ **or** Podman 4+ with Compose support.
- Enough RAM/disk to compile `vossvolvox` and run MariaDB (2 GiB free is plenty).

### Quick run (Podman)
```bash
# from the repo root
mkdir -p output
./build_podman_image.sh
```

`build_podman_image.sh` tears down any existing containers, starts MariaDB in the background, and builds/runs the `web` container while streaming logs to `logs/podman-compose-<timestamp>.log`. See [docs/CONTAINER.md](docs/CONTAINER.md) for the full Podman workflow and port-forwarding tips.

### Build & Run (docker compose)
```bash
# from the repo root
mkdir -p output                      # persist job artifacts on the host
docker compose up --build
```

The compose file exposes Apache on port `8080`, so the UI is available at `http://localhost:8080/php/volumeCalc.php` (and the other PHP entry points under `/php`). Jobs write into `output/` which is bind-mounted so logs/results survive container rebuilds.

### What the containers do
- `web`: built from the included `Dockerfile`. It installs Apache + PHP, Python 3 with `numpy/scipy/MySQLdb`, builds the bundled `vossvolvox` sources, installs the helper scripts/data expected by `ThreeVLib`, rewrites `py/sinedon/sinedon.cfg` based on `THREEV_DB_*` variables, boots Apache, and automatically runs `py/sinedon/maketables.py threevdata` against the DB on startup.
- `db`: vanilla `mariadb:10.6` with credentials defined in `docker-compose.yml`. Data lives in the named volume `db-data`.

Use `podman compose` instead of `docker compose` if you prefer Podman—the files are compatible. The stack is pure Python for rendering and builds natively on arm64 or amd64.

The `web` container’s entrypoint probes MariaDB with `mysql --skip-ssl --ssl-verify-server-cert=0`, sleeping ~20 s between attempts (six tries total). Keep an eye on `podman compose logs web` to ensure the DB is ready before Apache starts serving traffic.

## macOS Podman

For a concise macOS setup (no emulation required), see [docs/MACOS_PODMAN.md](docs/MACOS_PODMAN.md). A Homebrew `Brewfile` is included at the repo root for installing Podman tooling.

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
Pillow
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
