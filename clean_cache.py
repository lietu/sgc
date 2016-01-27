"""
Clean SGC caches periodically.

Suggested usage is to put this in crontab, once per day, with the following
settings:

--users=2 --apps=5
"""

import os
import inspect
from argparse import ArgumentParser
from glob import glob
from random import sample

CURRENT_DIR = os.path.dirname(
    os.path.abspath(inspect.getfile(inspect.currentframe()))
)
CACHE_BASE = os.path.join(CURRENT_DIR, "cache")

USER_PATTERNS = [
    "GetOwnedGames-*",
    "User-*"
]

APP_PATTERNS = [
    "GetAppData-*",
]


def get_args():
    ap = ArgumentParser()
    ap.add_argument("--users", type=int, required=True,
                    help="Number of user cache entries to clear")
    ap.add_argument("--apps", type=int, required=True,
                    help="Number of app cache entries to clear")

    return ap.parse_args()


def clean_caches(filename_patterns, count):
    for pattern in filename_patterns:
        matches = glob(os.path.join(CACHE_BASE, pattern))

        picks = min(len(matches), count)
        if picks == 0:
            continue

        deletions = sample(matches, picks)

        for entry in deletions:
            print("Deleting " + entry)
            os.remove(entry)


def clean_all_caches(users, apps):
    print("Deleting {} users and {} apps from cache".format(users, apps))
    clean_caches(USER_PATTERNS, users)
    clean_caches(APP_PATTERNS, apps)


if __name__ == "__main__":
    args = get_args()
    clean_all_caches(args.users, args.apps)
