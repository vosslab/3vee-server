# Install

Install for this repo means running the containerized web stack
(Apache/PHP, Python job runners, MariaDB, and vossvolvox tools).

## Requirements
- Docker Engine 24+ or Podman 4+ with compose support.
- About 2 GiB RAM and 5 GiB disk space for builds and the database.
- Internet access to download base images and packages.
- On macOS with Podman, a Podman VM is required (see [docs/MACOS_PODMAN.md](docs/MACOS_PODMAN.md)).

## Install steps
1. If you do not already have the repo, clone it:
   ```bash
   git clone https://github.com/vosslab/3vee-server.git
   cd 3vee-server
   ```
2. Create the output directory:
   ```bash
   mkdir -p output
   ```
3. Start the stack:
   ```bash
   podman compose up --build
   ```
   Use `docker compose up --build` if you are using Docker.

## Verify install
```bash
podman compose logs --tail 50 web
```

Look for the Apache startup line before loading http://localhost:8080/php/volumeCalc.php.

## Known gaps
- TODO: Confirm whether non-container local installs are supported and document
  required system packages if they are.

See [docs/CONTAINER.md](docs/CONTAINER.md) for full build and run details and
[docs/MACOS_PODMAN.md](docs/MACOS_PODMAN.md) for macOS Podman setup.
