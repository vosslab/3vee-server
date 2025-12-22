# Repository Guidelines

## Codebase Overview
- **Entry points:** Users interact through PHP pages in `php/` (e.g., `volumeCalc.php`, `viewResults.php`). Shared helpers live in `php/inc/*.inc`, and diagnostics/scripts sit in `php/tests/`.
- **Job orchestration:** Form submissions run `py/run*.py`, which bootstrap `ThreeVScript.py`/`ThreeVLib.py`. Those modules coordinate volume calculations, smoothing (pure Python low-pass filtering), and rendering via the headless Python renderer in `py/appionlib`, plus legacy `vossvolvox` binaries.
- **Supporting libraries:** `py/appionlib`, `py/pyami`, and `py/sinedon` are mostly vendor drops—touch only as needed for bug fixes or Python 3 work.
- **Visualization assets:** `jmol/`, `jmol-*/`, `php/css/`, `php/img/`, and `php/js/` provide the static UI and viewer resources packaged with the repo.
- **Container/build plumbing:** `Dockerfile`, `docker-compose.yml`, `docker/`, and `build_podman_image.sh` define the web + MariaDB stack. Images are pre-built via `podman build --arch <ARCH>` (default `amd64`) before `podman compose up`.
- **Data & artifacts:** `output/` is bind-mounted at runtime to hold submitted jobs, logs, and generated meshes. Keep it out of version control.

## Project Structure & Module Organization
- `php/`: Web UI entry points and result viewers (with `php/tests/` for ad hoc diagnostics).
- `py/`: Python job runners (`run*.py`, `ThreeVLib.py`, `ThreeVScript.py`, `threevdata.py`), shared libraries (`appionlib`, `pyami`, `sinedon`), and smoke scripts under `py/tests/`.
- `vossvolvox/`: C++ tools built into `bin/*.exe` inside the image.
- `docker/`, `Dockerfile`, `docker-compose.yml`: Container build and orchestration.
- `output/`: Job artifacts/logs (bind-mounted in containers; kept out of Git).

## Build, Test, and Development Commands
- Build & run with Podman/Docker: `podman compose up --build` (or `docker compose up --build`). Opens UI at `http://localhost:8080/php/volumeCalc.php`.
- Start the Podman VM (macOS) before `compose up`: `podman machine start podman-machine-default` (see `CONTAINER.md` for the full Podman workflow and port-forwarding tips).
- Exec into web container: `podman compose exec web bash`.
- Lint compile Python locally: `(cd py && python3 -m py_compile *.py run*.py ThreeV*.py)`.
- Build vossvolvox natively (if needed): `make -C vossvolvox/src all`.

## Coding Style & Naming Conventions
- Python 3, 4-space indentation, UTF-8, prefer f-strings and pathlib when adding new code.
- PHP follows existing style (plain echo templates, minimal HTML helpers).
- File naming: snake_case for Python, lowerCamel for PHP functions, keep historical `*.exe` binary names.
- Keep shebangs `#!/usr/bin/env python3` for scripts.

## Testing Guidelines
- No formal test suite here; basic sanity: `python3 -m py_compile ...` and run a sample job via the web UI.
- For C++ tools, use `make test` in `vossvolvox` if adding new binaries.
- Prefer adding small smoke scripts over heavy frameworks until an official test harness exists.

## Commit & Pull Request Guidelines
- Commits: concise present-tense messages (e.g., “Add Python3 port for runVolume”), group related changes.
- PRs: include summary, validation steps (e.g., “podman compose up --build; submitted volumeCalc”), note any platform caveats (amd64 vs arm64 Chimera).
- Keep unrelated formatting churn out of functional changes; avoid rewriting vendorized libs unless required.

## Security & Configuration Tips
- Database config is templated via `py/sinedon/sinedon.cfg` at container start; override with `THREEV_DB_*`.
- Chimera installer only runs on amd64; arm64 builds skip it by design.
- User input flows into shell commands in PHP → Python; sanitize and escape if introducing new parameters.
- The MariaDB wait loop now retries every 20 s (6 attempts total), forces `mysql` to use `--skip-ssl --ssl-verify-server-cert=0`, and logs each probe; follow status via `podman compose logs --tail 50 web` (or `db` if you temporarily remove `logging.driver: "none"`) and wait for Apache’s startup line before loading the UI at `http://localhost:8080/php/volumeCalc.php`.
See Python coding style in docs/PYTHON_STYLE.md.
See Markdown style in docs/MARKDOWN_STYLE.md.
When making edits, document them in docs/CHANGELOG.md.
See repo style in docs/REPO_STYLE.md.
