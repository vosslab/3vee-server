# Changelog

## 2025-12-22
- Moved documentation into `docs/` and renamed files to match repo conventions.
- Updated references in `README.md` and `AGENTS.md`.
- Added ChimeraX (flatpak) install flow in the Dockerfile and made rendering prefer ChimeraX with Python fallback.
- Documented the need for privileged builds during ChimeraX flatpak installation.
- Added `SQLITE_MIGRATION_PLAN.md` outlining a staged SQLite migration plan.
- Added a Docker build-time ChimeraX smoke test script (`py/tests/chimerax_smoke.py`) guarded by `CHIMERAX_TEST`.
- Removed unsupported `--no-sandbox` flag from the ChimeraX flatpak wrapper.
- Added CLI flags (including `--privileged-build` and `--chimerax-test`) to `build_podman_image.sh` for ChimeraX builds.
- Removed env-based renderer toggles so ChimeraX is always attempted before Python fallbacks.
- Dropped the legacy `mapman_linux.exe` copy step from the Docker image build.
- Removed mapman-based EZD→CCP4 conversion and updated FSVCalc to consume MRC output directly.
- Set the web service to privileged in `docker-compose.yml` to allow ChimeraX (flatpak) at runtime.
- Passed `QTWEBENGINE_CHROMIUM_FLAGS=--no-sandbox` into the ChimeraX flatpak wrapper to allow root execution.
- Moved the ChimeraX smoke test to container startup (entrypoint) and dropped the Dockerfile build-time test.
- Disabled ChimeraX integration (flatpak install, wrapper, smoke test) and reverted rendering to the Python-only path.
- Sanitized PHP inputs used in shell commands and removed shell_exec usage in log tails.
- Added OBJ export in the headless renderer so Jmol links can work, and added Jmol links to channel/FSV result pages.
- Tightened fixed-format input validation (finite floats, strict jobid format) and aligned step-one jobid generation.
- Updated the source code page to point at GitHub repos and removed Subversion references.
- Added a top navigation bar and simplified footer across PHP pages.
- Restyled the header/footer with a slimmer menu and improved layout/typography.
