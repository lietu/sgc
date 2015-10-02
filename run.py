from random import choice
import json
import sys
import os

from bottle import route, run, static_file

import settings
from sgc.steamapi import SteamAPI, CacheManager
from sgc.steamdata import User


@route('/')
@route('/<filename:re:.*\.(js|html|css)>')
def static(filename="index.html"):
    return static_file(filename, root='static')


@route('/pick/<name>/<reviews>/<hours_lt>')
def pick(name, reviews, hours_lt):
    user = User(name)

    if reviews == "null":
        reviews = None
    else:
        reviews = [
            int(i) for i in reviews.split(",")
        ]

    if hours_lt == "null":
        hours_lt = None
    else:
        hours_lt = int(hours_lt)

    filtered = user.filtered_games(
        reviews=reviews,
        hours_lt=hours_lt
    )

    game = choice(filtered)

    response = {
        "games": user.game_count,
        "matches": len(filtered),
        "name": name,
        "game": game.name,
        "review": game.review,
        "hours": game.hours,
        "logo": game.logo
    }

    user.save_to_cache()
    CacheManager.write_to_cache()

    return json.dumps(response)


if __name__ == "__main__":
    SteamAPI.set_default_key(settings.STEAM_API_KEY)

    if not os.path.exists("cache"):
        print("Cache directory does not exist. (mkdir -p cache)")
        sys.exit(1)

    run(host=settings.HOST, port=settings.PORT)
