# 3V Server Technical Architecture

This document explains how the 3V (Voss Volume Voxelator) server works end-to-end. The stack combines PHP for the web UI, Python for orchestration, MariaDB for metadata, compiled C++ programs from the vossvolvox toolkit for the heavy computation, and a set of utilities (`appionlib`, `pyami`, `sinedon`) that glue these parts together.

## High-Level Flow
1. **User submits a job** through one of the PHP forms (e.g., `php/volumeCalc.php`). Form helpers defined in `php/inc/processing.inc` normalize inputs, render documentation popovers, and show presets.
2. **PHP assembles a CLI command** (see `php/volumeCalc.php:149-161` and friends) that points at one of the `run*.py` scripts, supplies the sanitized parameters, and then calls `launchJob()` (also in `processing.inc`). The helper spawns the Python process, usually redirecting stdout/stderr to `output/<jobdir>/shell-<jobid>.log` and storing the job id in MariaDB.
3. **Python runner (`runVolume.py`, `runChannelFinder.py`, …)** inherits from `ThreeVScript.ThreeVScript`. The base class parses CLI options, sets up the job directory, writes a running log (`runlog-<jobid>.html`), persists metadata via `threevdata` (MariaDB), and fetches any required PDB file.
4. **`ThreeVLib` performs the heavy lifting**: it converts PDB → XYZR, invokes the appropriate vossvolvox executable (`bin/Volume.exe`, `bin/AllChannel.exe`, etc.), post-processes the binary output, and generates downloadable artifacts plus preview images.
5. **Python emits result fragments** (HTML in `results-<jobid>.html`) and streaming logs referenced by the PHP status pages.
6. **PHP delivers status/results** via `php/viewResults.php`. It polls the HTML logs, colors terminal output, and, once the job finishes, wraps the generated result page with the global chrome.

## Repository Layout
- `php/` – Web entry points for each tool (`volumeCalc.php`, `channelFinder.php`, `viewResults.php`, etc.) plus supporting assets referenced through `processing.inc`.
- `run*.py` – Python jobs invoked directly from PHP. Each maps to one UI page (volume calculation, channel extraction, tunnel finder, etc.).
- `ThreeVScript.py` – Shared runner that handles CLI parsing, filesystem setup, metadata upload, and PDB preparation.
- `ThreeVLib.py` – Library of domain-specific helpers responsible for calling the C++ binaries, converting file formats, imaging, and logging.
- `threevdata.py` – Sinedon ORM definitions for MariaDB tables (`ProgramRun`, `ParamValue`, etc.).
- `appionlib/`, `pyami/` – External dependencies that provide utilities for logging (`apDisplay`), parameter handling (`apParam`), Chimera rendering, MRC IO, etc.
- `sinedon/` – Lightweight ORM and DB connection helpers plus `sinedon.cfg` for the MariaDB DSN.
- Utility scripts (`mrcTrim.py`, `mrcBisect.py`, etc.) – invoked by `ThreeVLib` for optional post-processing.

All binaries and static assets live under `/var/www/html/3vee` at runtime (`ThreeVLib.procdir`). That directory is expected to contain `bin/` (vossvolvox executables), `dat/` (lookup tables such as `atmtypenumbers.dat`), `sh/` (wrappers like `pdb_to_xyzr.sh`), `output/` (job data), and `py/` (the checked-in Python scripts).

## PHP Front End
### Common infrastructure
`php/inc/processing.inc` (not tracked here) defines shared helpers used by every page: `writeTop()/writeBottom()` for layout, `writeJavaPopupFunctions()` for inline documentation, `firstColumn()` for the set of common inputs (job id, grid resolution, PDB upload, hetero flags), `docpop()` for hoverable tooltips, `showRecentRuns()` for listing job history, and `launchJob()` for spawning Python.

`$PROCDIR` is exported from the same include and points at the server-side checkout (usually `/var/www/html/3vee/`). PHP uses it whenever it needs to read/write job artifacts.

### Submission pages
Each page follows the pattern shown in `php/volumeCalc.php` and `php/channelFinder.php`:
- Render the shared column of general parameters via `firstColumn()`.
- Add tool-specific fields (probe radii, filters, coordinate inputs) with inline documentation and optional presets implemented in JavaScript.
- On `POST`, read back the submitted values, build a CLI string, and call `launchJob($command, $progname)`.
- `launchJob` is expected to resolve/ration the `jobid`, create `output/<jobdir>` if needed, drop users onto the `viewResults.php?jobid=<jobid>` status page, and return an error string if submission failed.

Whenever PHP needs to surface progress, it calls into `php/viewResults.php`. That script:
- Pulls core job metadata via `inc/threevdata.inc` (a PHP bridge to the same MariaDB tables used by Python).
- Streams or tails `runlog-<jobid>.html` and `shell-<jobid>.log`, translating ANSI color codes with `convertToColors()`.
- Includes the generated `results-<jobid>.html` when available to avoid duplicating presentation logic that is already emitted by Python.

## Python Job Layer
### Runner scripts (`run*.py`)
Every Python entry point subclasses `ThreeVScript.ThreeVScript`, overrides `setupParserOptions()` to declare tool-specific CLI flags, optionally implements `checkConflicts()` to validate parameter combinations, and defines `start()` with the actual workflow. Examples:
- `runVolume.py` gathers a single probe radius and generates one surface.
- `runChannelFinder.py` enforces that at least one channel filter is set, then loops over the MRC files returned by `ThreeVLib.runChannelFinder()` and appends sections to the result HTML.
- `runVolumeRange.py` iterates through a range of probe radii, generating and documenting the result for each probe.

Because the runners inherit from `ThreeVScript`, they already support the shared CLI flags (`--jobid`, `--gridres`, `--pdbid/--pdbfile`, `--biounit`, `--hetero`, `--pymol`, `--waterpdb`, etc.) and use a consistent filesystem + logging convention.

### `ThreeVScript`
`ThreeVScript` (see `ThreeVScript.py`) is the backbone of every job:
- **Argument parsing** – wraps `optparse` and exposes helper methods to reconstruct command-line usage strings for DB logging.
- **Job directory setup** – converts job ids like `08jun04b.cc` into `output/08jun04b/cc` subdirectories, ensures they exist, and `chdir`s into them.
- **Metadata upload** – `uploadScriptData()` builds `threevdata.Path`, `ProgramRun`, `ParamName`, `ParamValue`, and `HostName` records, then inserts them through Sinedon so both PHP and Python can query run history.
- **PDB preparation** – downloads structures from RCSB (including the `?pdb1` biological unit variant when requested), decompresses them, optionally copies a user-uploaded file, and passes the result to `ThreeVLib.convertPDBtoXYZR()`.
- **Lifecycle hooks** – `onInit()` / `onClose()` allow job-specific code to tack logic before/after the core scaffold executes.
- **Logging** – creates `runlog-<jobid>.html` and writes command-line invocation metadata via `apParam.writeFunctionLog()`.

### `ThreeVLib`
`ThreeVLib` (see `ThreeVLib.py`) encapsulates the cluster-facing work:
- **Environment management** – sets `umask`, enforces one job directory per job (`/var/www/html/3vee/output/<jobdir>`), monitors system load before launching CPU-intensive steps (`checkSystemLoad()`), and wraps shell commands through `runCommand()` (optionally sourcing `/etc/bashrc`).
- **Geometry preparation** – extracts atoms from the PDB into `.atoms`, overlays `dat/atmtypenumbers.dat`, and uses `sh/pdb_to_xyzr.sh` to generate the XYZR file consumed by vossvolvox.
- **C++ invocation** – exposes a method per binary (`runVolume`, `runVolumeNoCav`, `runChannel`, `runChannelFinder`, `runTunnel`, `runSolvent`, `runCavity`, `runFsvCalc`). Each validates inputs, builds the command string in `/var/www/html/3vee/bin/`, and logs the action.
- **Post-processing** – converts EZD → CCP4 → MRC (`convertEZDtoCCP4`, `convertCCP4toMRC`), trims/bisects volumes (`trimMrcFile`, `bisectMrcFile` via helper scripts), decimates mesh outputs through Meshlab (`meshlabDecimateConvert`), and smooths the volumes before imaging (`filterVolume`).
- **Visualization + artifacts** – renders static PNGs/X3D/OBJ outputs via UCSF Chimera (`makeImages`), optionally tars files, gzips data for download, and writes reusable HTML fragments (`webImageSection`, `webMrcStats`, `webMrcSection`, `webJmolSection`, `webStlSection`). Runner scripts merely open `results-<jobid>.html` and call these writers in whatever order suits the workflow.
- **Logging and monitoring** – every meaningful action writes a `<li>` entry into `runlog-<jobid>.html` with a severity icon (`Check`, `Star`, `Cross`). These are the lines `viewResults.php` streams back to users during execution.

## Database Layer & Sinedon
Python defines the schema used to persist job metadata in `threevdata.py`. Classes inherit from `sinedon.data.Data`, so each maps 1:1 to MariaDB tables. When `ThreeVScript.uploadScriptData()` runs it creates:
- `ProgramRun` rows keyed by `jobid` plus host/user info.
- `ParamName`/`ParamValue` rows capturing the exact CLI as submitted (including usage strings for reproducibility).
- `Path`, `ProgramName`, `UserName`, and `HostName` rows used by the PHP layer when it augments the results page.

DB connectivity is configured via `sinedon/sinedon.cfg`. PHP uses a parallel include (`inc/threevdata.inc`) to read the same tables, which is why both layers see identical job metadata without hitting the filesystem.

## Output, Logs, and Static Files
Given a job id `YYmmddx.zz`, both PHP and Python agree on the following conventions:
- `output/YYmmddx/zz/` – job directory containing everything.
- `runlog-<jobid>.html` – human-readable log consumed in `viewResults.php` running mode.
- `shell-<jobid>.log` – raw stdout/stderr from the spawned Python process (tailed for debugging in `viewResults.php`).
- `results-<jobid>.html` – fully formatted result sections (images, download links). PHP simply wraps this file inside the site chrome.
- Data products (MRC, CCP4, EZD, PNG, OBJ, X3D, STL) are written in the same folder and linked using the relative `output/<jobdir>/` URL that Python computes via `self.website`.

Because Python writes HTML fragments directly, there is no duplication of presentation logic: changes in `ThreeVLib.web*` helpers are immediately reflected across all job types.

## Extending the System
To add a new tool:
1. **Create a Python runner** following one of the existing `run*.py` scripts. Subclass `ThreeVScript`, add parser options for your parameters, and orchestrate the call(s) into `ThreeVLib` inside `start()`.
2. **Expose the workflow via PHP**: copy an existing `php/*Calc.php`, wire up custom inputs, and point `runThreeVProgram()` at the new runner script. Ensure you add any documentation popovers needed for the new inputs.
3. **Update the UI** to link to the new page (navigation, README, etc.) and, if necessary, add support to `viewResults.php` for new download types.
4. **Deploy supporting binaries/scripts** into `/var/www/html/3vee/bin` or `py/` as needed so `ThreeVLib` can reach them.

Because job metadata is abstracted through Sinedon, new parameters will automatically show up in the “Run Information” table as soon as the runner sends them through `uploadScriptData()`.

## Key Dependencies and Assumptions
- UCSF Chimera, EMAN’s `proc3d`, Meshlab, and ImageMagick must be installed on the host for imaging and 3D conversion steps.
- MariaDB credentials are stored in `sinedon/sinedon.cfg`; both PHP and Python components expect this file to be configured.
- The filesystem layout referenced by `$PROCDIR`/`ThreeVLib.procdir` must match the production deployment (`/var/www/html/3vee`).
- Some PHP includes (`inc/processing.inc`, `inc/threevdata.inc`) are not part of this repo; they are required for the site to run.

This overview should give new contributors enough context to trace a job from the browser, through the Python orchestrators, down to the native executables, and back to the rendered output.
