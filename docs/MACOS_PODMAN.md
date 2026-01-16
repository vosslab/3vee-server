# macOS Podman setup (native arm64/amd64)

3vee-server builds and runs natively on Apple Silicon without emulation. Use Podman's VM and compose to run the stack on macOS.

## Prerequisites

- Homebrew (https://brew.sh)
- macOS 13+ with virtualization support

## Install Podman tooling

From the repo root:

```bash
brew bundle
```

This uses the `Brewfile` in the repo root to install `podman` and `podman-compose`.

## Create and start the Podman machine

```bash
podman machine init \
  --now \
  --user-mode-networking \
  --cpus 4 \
  --memory 8192 \
  --disk-size 40
```

Confirm the machine is running:

```bash
podman machine ls
```

## Build and run

```bash
./build_podman_image.sh
```

The UI will be available at `http://localhost:8080/php/volumeCalc.php` once Apache is up.
