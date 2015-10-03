import csv

try:
    import fcntl
except ImportError:
    print("No fcntl support, cannot guarantee file consistency.")

    class fcntl(object):
        LOCK_EX = 0
        LOCK_UN = 1

        @staticmethod
        def flock(*args):
            pass


class FileLock(object):
    def __init__(self, file):
        self.file = file

    def __enter__(self):
        fcntl.flock(self.file, fcntl.LOCK_EX)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        fcntl.flock(self.file, fcntl.LOCK_UN)


class AnalyticsManager(object):
    ANALYTICS_PATH = "analytics/{key}.csv"

    @classmethod
    def write(cls, key, *args):
        path = cls.ANALYTICS_PATH.format(key=key)
        with open(path, 'a') as f:
            with FileLock(f):
                writer = csv.writer(f)
                writer.writerow(args)