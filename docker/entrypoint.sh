#!/bin/bash
set -euo pipefail

APP_ROOT="/var/www/html/3vee"

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
cfg_path = os.path.join(app_root, 'sinedon', 'sinedon.cfg')

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
	if [[ "${THREEV_SKIP_DB_WAIT}" == "1" ]]; then
		return
	fi

	local attempt=0
	until mysql -h "${THREEV_DB_HOST}" -u "${THREEV_DB_USER}" -p"${THREEV_DB_PASSWORD}" -e "SELECT 1" >/dev/null 2>&1
	do
		((attempt++))
		echo "Waiting for MariaDB at ${THREEV_DB_HOST}…attempt ${attempt}"
		sleep 30
	done
}

bootstrap_db() {
	if [[ "${THREEV_SKIP_DB_INIT}" == "1" ]]; then
		return
	fi
	python3 "${APP_ROOT}/sinedon/maketables.py" threevdata || true
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
