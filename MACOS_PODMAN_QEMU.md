# Preparing an x86_64 Podman Machine on macOS with QEMU

Chimera and `threev-web`’s native binaries are amd64-only, so Apple Silicon hosts must run them inside an emulated x86_64 Podman VM. Podman on macOS uses QEMU under the hood; this document walks through the one-time preparation so that `podman build --arch amd64`, `./build_podman_image.sh`, and `podman compose up` all execute inside that emulated architecture.

## Prerequisites

- Homebrew (https://brew.sh) so you can install the Podman toolchain.
- Apple Silicon macOS 13+ with virtualization enabled (macOS shows “Virtualization” as a supported feature in `/Applications/Utilities/System Settings.app` under “About” → “System Report” → “Hardware”).

## 1. Install Podman + QEMU

```bash
brew install podman podman-compose qemu
podman version
podman compose version
```

`qemu` provides the user-space binaries that Podman uses to emulate x86_64, and `podman`/`podman-compose` are the runtimes for your containers. If you already have Podman, make sure it is at least v4 so the `podman machine` workflow supports Compose.

## 2. Create and configure the Podman machine

1. Initialize a machine with user-mode networking so host ports forward automatically:

```bash
podman machine init \
  --now \
  --user-mode-networking \
  --cpus 4 \
  --memory 8192 \
  --disk-size 40
```

The defaults work, but bumping memory/disk gives the VM enough headroom for compiling `vossvolvox` and storing Chimera assets. `--now` starts the VM immediately; omit it if you prefer to boot manually.

2. Confirm the machine is running:

```bash
podman machine ls
```

3. To inspect or tweak the VM, open a shell:

```bash
podman machine ssh
```

Inside the VM you can install additional tooling or verify that `/usr/local/bin/qemu-x86_64` exists.

4. Install QEMU user emulation inside the VM (one time):

```bash
podman machine ssh -- sudo rpm-ostree install qemu-user-static
podman machine stop podman-machine-default
podman machine start podman-machine-default
```

This adds the static QEMU binaries to the guest so binfmt registration can run for amd64 images. Restarting the machine applies the rpm-ostree change.

## 3. Verify x86_64 emulation

Run an amd64 container to ensure QEMU is registered with `binfmt_misc`:

```bash
podman run --rm --arch amd64 docker.io/library/alpine uname -m
```

It should print `x86_64`. Podman automatically handles the `binfmt` registration the first time you request a mismatched architecture, but rerun the command if you ever recreate the VM.

## 4. Build and run the stack

- Use `./build_podman_image.sh` (default `ARCH=amd64`) to build the web image via Podman. It sets `podman build --arch amd64`, ensuring the resulting image is compatible with the binaries you need.
- Start services with `podman compose up --build` after the machine is started. Keep the machine running while you interact with the UI or submit jobs.
- `podman machine stop`/`start` controls the VM lifecycle.

## Troubleshooting notes

- If building fails because qemu is missing, reinstall `qemu` or rerun `brew reinstall qemu`.
- Delete and recreate the machine when you want a clean slate: `podman machine stop podman-machine-default`, `podman machine rm podman-machine-default`, then `podman machine init ...`.
- If host ↔ VM networking breaks, reinitialize with `--user-mode-networking` so `localhost:8080` maps into the guest automatically.

With these steps completed, your macOS host can run the amd64-only components via Podman + QEMU while still interacting with them over `http://localhost:8080/php/volumeCalc.php`.
