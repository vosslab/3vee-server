# Code architecture

## Overview
3vee-server provides a PHP web UI that launches Python runner scripts to compute
volume results, writes job artifacts under [output/](output/), and can persist
run metadata in MariaDB when the container stack is used.

## Major components
- Web UI entry points live in [php/](php/) with shared helpers in
  [php/inc/](php/inc/) and static assets in [php/css/](php/css/),
  [php/js/](php/js/), [php/img/](php/img/), and [php/jmol/](php/jmol/).
- Python runners live in [py/](py/) as `run*.py` scripts and share core logic in
  [py/ThreeVScript.py](py/ThreeVScript.py) and [py/ThreeVLib.py](py/ThreeVLib.py).
- Rendering and legacy helpers are bundled under [py/appionlib/](py/appionlib/),
  [py/pyami/](py/pyami/), and [py/sinedon/](py/sinedon/).
- Database metadata schema lives in [py/threevdata.py](py/threevdata.py) and is
  paired with PHP accessors in [php/inc/threevdata.inc](php/inc/threevdata.inc).
- Container build and runtime are defined by [Dockerfile](Dockerfile),
  [docker-compose.yml](docker-compose.yml), and [docker/entrypoint.sh](docker/entrypoint.sh).
  The Dockerfile clones and builds vossvolvox and installs binaries under
  `/var/www/html/3vee/bin` inside the image.

## Data flow
1. A user submits a form in a page under [php/](php/).
2. Shared PHP helpers in [php/inc/processing.inc](php/inc/processing.inc) assemble
   inputs and invoke a Python runner in [py/](py/) (`run*.py`).
3. The Python runner uses [py/ThreeVScript.py](py/ThreeVScript.py) and
   [py/ThreeVLib.py](py/ThreeVLib.py) to prepare inputs, call vossvolvox binaries,
   and render outputs via [py/appionlib/](py/appionlib/).
4. Job artifacts are written under [output/](output/) including
   `results-<jobid>.html`, `runlog-<jobid>.html`, and `shell-<jobid>.log`.
5. [php/viewResults.php](php/viewResults.php) reads those files and presents
   status and results back to the user.

## Testing and verification
- Repo-level scripts live in [tests/](tests/) including
  [tests/run_pyflakes.sh](tests/run_pyflakes.sh),
  [tests/run_ascii_compliance.py](tests/run_ascii_compliance.py), and
  [tests/check_ascii_compliance.py](tests/check_ascii_compliance.py).
- Smoke scripts and lint helpers live under [py/tests/](py/tests/) and
  [php/tests/](php/tests/).

## Extension points
- Add a new UI page under [php/](php/) and wire it to
  [php/inc/processing.inc](php/inc/processing.inc).
- Add a new runner under [py/](py/) and reuse
  [py/ThreeVScript.py](py/ThreeVScript.py) and
  [py/ThreeVLib.py](py/ThreeVLib.py).
- Update container behavior in [Dockerfile](Dockerfile),
  [docker/entrypoint.sh](docker/entrypoint.sh), or
  [docker-compose.yml](docker-compose.yml).

## Known gaps
- None noted.
