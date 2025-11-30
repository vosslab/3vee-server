#!/usr/bin/env bash
set -euo pipefail

prepare_local_env() {
    local pyroot=${1:-$(cd "$(dirname "$0")/.." && pwd)}
    local sinedon_cfg="$pyroot/sinedon/sinedon.cfg"
    local pyami_cfg="$pyroot/pyami/pyami.cfg"
    local pymysql_stub="$pyroot/pymysql.py"
    local stub_files=(), file
    stub_files+=("$sinedon_cfg" "$pyami_cfg" "$pymysql_stub")

    cleanup_stubs() {
        for file in "${stub_files[@]}"; do
            rm -f "$file"
        done
    }

    trap cleanup_stubs EXIT

    cat <<'EOF' >"$sinedon_cfg"
[global]
host=localhost
user=appion
passwd=
db=appiondata

[leginondata]
db=leginondata

[leginonconfig]
db=leginondata
EOF

    cat <<'EOF' >"$pyami_cfg"
[global]
host=localhost
user=pyami
passwd=
db=pyami
EOF

    cat <<'EOF' >"$pymysql_stub"
import sys

class DummyCursor:
    def fetchone(self):
        return None

    def fetchall(self):
        return []

    def fetchmany(self, *args, **kwargs):
        return []

    def close(self):
        pass


class DummyConnection:
    def cursor(self, *args, **kwargs):
        return DummyCursor()

    def close(self):
        pass

    def commit(self):
        pass

    def ping(self, reconnect=False):
        pass

    def autocommit(self, flag=True):
        pass

    def insert_id(self):
        return 0

    def __getattr__(self, item):
        return lambda *args, **kwargs: None


class converters:
    @staticmethod
    def escape_string(val):
        return val


class cursors:
    class DictCursor:
        pass


def connect(**kwargs):
    return DummyConnection()


def install_as_MySQLdb():
    pass


class Error(Exception):
    pass


class OperationalError(Error):
    pass


class ProgrammingError(Error):
    pass


class InternalError(Error):
    pass


class err:
    Error = Error
    OperationalError = OperationalError
    ProgrammingError = ProgrammingError
    InternalError = InternalError


sys.modules.setdefault('pymysql.err', err)
EOF
}
