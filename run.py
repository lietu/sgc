from random import choice
import json
import sys
import os

from bottle import run, static_file, Bottle

import settings
from sgc.errors import SGCError, Wrapped
from sgc.steamapi import SteamAPI, CacheManager
from sgc.steamdata import User


app = application = Bottle()


@app.route('/')
@app.route('/<filename:re:.*\.(js|html|css)>')
def static(filename="index.html"):
    return static_file(filename, root='static')


@app.route('/pick/<name>/<reviews>/<hours_lt>')
def pick(name, reviews, hours_lt):
    try:
        SteamAPI.set_default_key(settings.STEAM_API_KEY)

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
            "type": "success",
            "appid": game.app_id,
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

    except SGCError as e:
        response = e.to_response()

    # except Exception as e:
    #     wrapped = Wrapped(e)
    #     response = wrapped.to_response()

    return json.dumps(response)


if __name__ == "__main__":
    if not os.path.exists("cache"):
        print("Cache directory does not exist. (mkdir -p cache)")
        sys.exit(1)

    run(app=app, host=settings.HOST, port=settings.PORT)
