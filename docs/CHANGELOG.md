# Changelog

## 2026-01-16
- Removed shebangs from non-executable Python modules flagged by lint.
- Removed additional invalid shebangs from Python modules flagged by lint.
- Removed remaining invalid shebangs flagged by lint in py/sinedon, py/tests, and related scripts.
- Restored valid shebangs for py/tests shell and Python smoke test scripts.
- Simplified README with a concise overview, doc map, and Podman quick start.
- Added docs/INSTALL.md and docs/USAGE.md for setup and basic usage guidance.
- Expanded docs/INSTALL.md and docs/USAGE.md with quick start, verification, and
  known gaps sections.
- Adjusted install and usage docs to include TODO-style gaps and command snippets.
- Added a macOS Podman note in docs/INSTALL.md and expanded docs/USAGE.md examples.
- Rewrote docs/CODE_ARCHITECTURE.md to match current repo structure.
- Clarified the PHP submission step wording in docs/CODE_ARCHITECTURE.md.
- Added docs/FILE_STRUCTURE.md and linked it from README.md.

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
- Removed mapman-based EZD->CCP4 conversion and updated FSVCalc to consume MRC output directly.
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
- Replaced macOS QEMU guidance with native Podman instructions and added a Homebrew Brewfile.
- Updated README quick run instructions and cleaned out the old env/QEMU sections.
- Added a dark mode backlog item.
- Added CSRF protection and stricter PDB upload validation.
- Refreshed the glossary and volume viewing guide layout/content.
- Added program summaries to the glossary with images and descriptions.
- Added ASA/SAS/SES background notes and references to the glossary (from Wikipedia).
- Expanded the glossary with guided tutorials, parameter intuition, and interpretation notes.
- Expanded the footer to a five-column layout with separate Resources and Social sections.
- Moved Font Awesome font assets into `php/assets/fonts/`.
- Replaced footer email with support + social links and added Font Awesome icons.
- Added a documentation index section to `README.md` linking all `docs/*.md` files.
