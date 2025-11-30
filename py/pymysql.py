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


import sys
sys.modules.setdefault('pymysql.err', err)
