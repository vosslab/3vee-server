#!/bin/bash
set -euo pipefail

APP_ROOT="/var/www/html/3vee"
PY_ROOT="${APP_ROOT}/py"

THREEV_DB_HOST="${THREEV_DB_HOST:-db}"
THREEV_DB_USER="${THREEV_DB_USER:-vossman}"
THREEV_DB_PASSWORD="${THREEV_DB_PASSWORD:-vossman}"
THREEV_DB_NAME="${THREEV_DB_NAME:-threevdata}"
THREEV_SKIP_DB_WAIT="${THREEV_SKIP_DB_WAIT:-0}"
THREEV_SKIP_DB_INIT="${THREEV_SKIP_DB_INIT:-0}"

update_sinedon_config() {
	python3 <<'PYCODE'
import os
import configparser

app_root = os.environ.get('APP_ROOT', '/var/www/html/3vee')
cfg_path = os.path.join(app_root, 'py', 'sinedon', 'sinedon.cfg')

db_host = os.environ.get('THREEV_DB_HOST', 'db')
db_user = os.environ.get('THREEV_DB_USER', 'vossman')
db_pass = os.environ.get('THREEV_DB_PASSWORD', 'vossman')
db_name = os.environ.get('THREEV_DB_NAME', 'threevdata')

config = configparser.RawConfigParser()
config.read(cfg_path)

if not config.has_section('global'):
	config.add_section('global')
config.set('global', 'host', db_host)

section = 'threevdata'
if not config.has_section(section):
	config.add_section(section)
config.set(section, 'db', db_name)
config.set(section, 'user', db_user)
config.set(section, 'passwd', db_pass)

with open(cfg_path, 'w') as cfg_file:
	config.write(cfg_file)
PYCODE
}

wait_for_db() {
  if [[ "${THREEV_SKIP_DB_WAIT:-0}" == "1" ]]; then
    echo "THREEV_SKIP_DB_WAIT=1, skipping DB wait"
    return 0
  fi

  local host="${THREEV_DB_HOST:-db}"
  local user="${THREEV_DB_USER:-vossman}"
  local pass="${THREEV_DB_PASSWORD:-vossman}"
  local max_attempts=6
  local attempt=0

  echo "Waiting for MariaDB at ${host} as ${user}..."

  # Use a loop so failures do not trigger set -e
  while ! mysql --skip-ssl --ssl-verify-server-cert=0 \
                -h "${host}" -u "${user}" -p"${pass}" \
                -e "SELECT 1" >/dev/null 2>&1; do
    attempt=$((attempt + 1))
    if (( attempt >= max_attempts )); then
      echo "ERROR: MariaDB still not ready after ${max_attempts} attempts" >&2
      return 1
    fi
    echo "  attempt ${attempt} failed, sleeping 20s..."
    sleep 20
  done

  echo "MariaDB is ready."
}

bootstrap_db() {
	if [[ "${THREEV_SKIP_DB_INIT}" == "1" ]]; then
		return
	fi
	python3 "${PY_ROOT}/sinedon/maketables.py" threevdata || true
}

prepare_fs() {
	mkdir -p "${APP_ROOT}/output"
	chown -R www-data:www-data "${APP_ROOT}/output"
	mkdir -p /run/apache2
}

export APP_ROOT
update_sinedon_config
wait_for_db
bootstrap_db
prepare_fs

exec /usr/sbin/apache2ctl -D FOREGROUND
