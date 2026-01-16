# File structure

## Top-level layout
- [AGENTS.md](AGENTS.md): agent instructions for this repo.
- [README.md](README.md): project overview and quick start.
- [Dockerfile](Dockerfile): container image build for the web stack.
- [docker-compose.yml](docker-compose.yml): web and MariaDB services.
- [build_podman_image.sh](build_podman_image.sh): Podman build and run helper.
- [Brewfile](Brewfile): macOS Homebrew packages for Podman workflows.
- [SQLITE_MIGRATION_PLAN.md](SQLITE_MIGRATION_PLAN.md): notes on a staged SQLite plan.
- [LICENSE](LICENSE): licensing terms.
- [docs/](docs/): documentation set.
- [docker/](docker/): container entrypoint and helper scripts.
- [php/](php/): web UI entry points and static assets.
- [py/](py/): Python job runners and shared libraries.
- [tests/](tests/): repo-level lint and compliance scripts.
- [devel/](devel/): developer utilities.
- [leginon/](leginon/): bundled Leginon and related tooling.
- [output/](output/): runtime job artifacts (bind-mounted, gitignored).
- [logs/](logs/): local log output directory used by build scripts.

## Key subtrees
- [php/inc/](php/inc/): shared PHP helpers and database accessors.
- [php/tests/](php/tests/): PHP lint and smoke scripts.
- [php/css/](php/css/), [php/js/](php/js/), [php/img/](php/img/): UI assets.
- [php/jmol/](php/jmol/): Jmol viewer assets.
- [py/tests/](py/tests/): Python smoke scripts and sample data.
- [py/appionlib/](py/appionlib/), [py/pyami/](py/pyami/), [py/sinedon/](py/sinedon/):
  bundled libraries used by the Python job layer.

## Generated artifacts
- [output/](output/): job artifacts and logs (ignored in [.gitignore](.gitignore)).
- [docker/chimera.bin](docker/chimera.bin) and
  [docker/eman-linux-x86_64-cluster-1.9.tar.gz](docker/eman-linux-x86_64-cluster-1.9.tar.gz):
  downloaded assets (ignored in [.gitignore](.gitignore)).

## Documentation map
- [docs/INSTALL.md](docs/INSTALL.md): setup instructions.
- [docs/USAGE.md](docs/USAGE.md): running the UI and finding outputs.
- [docs/CONTAINER.md](docs/CONTAINER.md): container build and runtime details.
- [docs/MACOS_PODMAN.md](docs/MACOS_PODMAN.md): macOS Podman setup notes.
- [docs/CODE_ARCHITECTURE.md](docs/CODE_ARCHITECTURE.md): system overview and data flow.
- [docs/FILE_STRUCTURE.md](docs/FILE_STRUCTURE.md): directory map (this document).
- [docs/CHANGELOG.md](docs/CHANGELOG.md): dated change log.
- [docs/REPO_STYLE.md](docs/REPO_STYLE.md): repo conventions.
- [docs/MARKDOWN_STYLE.md](docs/MARKDOWN_STYLE.md): Markdown rules.
- [docs/PYTHON_STYLE.md](docs/PYTHON_STYLE.md): Python conventions.

## Where to add new work
- PHP pages and UI changes go in [php/](php/) and shared helpers in [php/inc/](php/inc/).
- Python job logic goes in [py/](py/) and shared helpers in [py/appionlib/](py/appionlib/).
- Container changes go in [Dockerfile](Dockerfile), [docker/](docker/),
  and [docker-compose.yml](docker-compose.yml).
- Documentation updates go in [docs/](docs/).
- Lint or smoke scripts go in [tests/](tests/), [py/tests/](py/tests/),
  or [php/tests/](php/tests/).
