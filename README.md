# 3vee-server
3vee-server is the web UI and containerized stack for 3V (voss volume voxelator), providing a PHP front end that runs Python job scripts and vossvolvox tools for volume calculations.

## Documentation

### Getting started
- [docs/INSTALL.md](docs/INSTALL.md): prerequisites and setup for the container stack.
- [docs/USAGE.md](docs/USAGE.md): run the UI and find job outputs.
- [docs/CONTAINER.md](docs/CONTAINER.md): detailed Docker and Podman build and run guide.
- [docs/MACOS_PODMAN.md](docs/MACOS_PODMAN.md): Podman VM setup for macOS.

### Architecture and project info
- [docs/CODE_ARCHITECTURE.md](docs/CODE_ARCHITECTURE.md): system components and data flow.
- [docs/FILE_STRUCTURE.md](docs/FILE_STRUCTURE.md): directory map and file placement.
- [docs/CHANGELOG.md](docs/CHANGELOG.md): dated changes.
- [docs/TODO.md](docs/TODO.md): backlog items.

### Standards and attribution
- [docs/REPO_STYLE.md](docs/REPO_STYLE.md): repo conventions.
- [docs/MARKDOWN_STYLE.md](docs/MARKDOWN_STYLE.md): Markdown rules.
- [docs/PYTHON_STYLE.md](docs/PYTHON_STYLE.md): Python conventions.
- [docs/AUTHORS.md](docs/AUTHORS.md): maintainers and contributors.

## Quick start (Podman)
```bash
mkdir -p output
podman compose up --build
```

Open http://localhost:8080/php/volumeCalc.php once the containers start. Job results are written to [output/](output/) on the host; see [docs/CONTAINER.md](docs/CONTAINER.md) and [docs/USAGE.md](docs/USAGE.md) for details.
