from sgc.cache import CacheManager
from sgc.steamapi import GetSteamID64, GetOwnedGames, GetAppData


def games_to_list(games):
    """
    Convert a list of Game objects to a list of objects for list API

    :param Game[] games:
    :return dict[]:
    """
    return [
        game.to_list_item()
        for game in games
    ]


class User(object):
    def __init__(self, name):
        self.name = name
        self._steam_id = None
        self._data = None
        self._games = None
        self.from_cache = self.load_from_cache()

    def save_to_cache(self):
        if self.from_cache:
            return False

        cache_data = {
            "_steam_id": self._steam_id,
            "_games": [
                game.cache_data
                for game in self._games
            ]
        }

        CacheManager.save(self.cache_key, cache_data)

        return True

    def load_from_cache(self):
        cache_data = CacheManager.load(self.cache_key)

        if cache_data is not None:
            print("Loading user info from cache")
            self._steam_id = cache_data["_steam_id"]
            self._games = [
                Game(**kwargs)
                for kwargs in cache_data["_games"]
            ]

            return True

        return False

    @property
    def cache_key(self):
        return "{}-{}".format(self.__class__.__name__, self.name.encode("hex"))

    @property
    def steam_id(self):
        if not self._steam_id:
            api = GetSteamID64()
            self._steam_id = api.get_data(self.name)
            print("{} -> {}".format(self.name, self._steam_id))

        return self._steam_id

    @property
    def data(self):
        if not self._data:
            api = GetOwnedGames()
            data = api.get_data(self.steam_id)
            self._data = data["response"]

        return self._data

    @property
    def game_count(self):
        return self.data["game_count"]

    @property
    def games(self):
        if not self._games:
            self._games = [
                Game(game_data)
                for game_data in self.data["games"]
            ]

        return self._games

    def filtered_games(self, reviews=None, hours_lt=None, hours_gt=None):
        if hours_gt and hours_lt and hours_gt > hours_lt:
            raise AttributeError(
                "Cannot fetch games with hours > {} and < {}".format(
                    hours_gt, hours_lt
                ))

        matches = []

        for game in self.games:
            if reviews and not game.review_number in reviews:
                continue

            if hours_lt and not game.hours < hours_lt:
                continue

            if hours_gt and not game.hours > hours_gt:
                continue

            matches.append(game)

        return matches


class Game(object):
    LOGO_URL = "http://media.steampowered.com/steamcommunity/public/images/apps/{appid}/{hash}.jpg"

    REVIEW_LEVELS = {
        '': -1,
        'Very Negative': 0,
        'Negative': 1,
        'Mostly Negative': 2,
        'Mixed': 3,
        'Mostly Positive': 4,
        'Positive': 5,
        'Very Positive': 6,
        'Overwhelmingly Positive': 7
    }

    def __init__(self, data, review=None):
        self._data = data
        self._review = review

    def to_list_item(self):
        return {
            "name": self.name,
            "logo": self.logo,
            "app_id": self.app_id,
            "hours": self.hours,
            "review": self.review,
        }

    @property
    def cache_data(self):
        return {
            "data": self._data,
            "review": self.review
        }

    @property
    def app_id(self):
        return self._data["appid"]

    @property
    def logo(self):
        return self.LOGO_URL.format(
            appid=self.app_id,
            hash=self._data["img_logo_url"]
        )

    @property
    def name(self):
        return self._data["name"].encode("utf-8")

    @property
    def hours(self):
        return self._data["playtime_forever"] / 60

    @property
    def review(self):
        if not self._review:
            api = GetAppData()
            self._review = api.get_data(self.app_id)

        return self._review

    @property
    def review_number(self):
        return self.REVIEW_LEVELS[self.review]
