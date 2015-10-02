import json
from copy import copy

from lxml import etree, html
import requests

from sgc.cache import CacheManager


ROOT_URL = "http://api.steampowered.com"
DEFAULT_KEY = None


class CachedAPI(object):
    def get_data(self, *args):
        key = self._get_cache_key(*args)

        data = CacheManager.load(key)
        if data is None:
            data = self._get_data(*args)
            CacheManager.save(key, data)

        return data

    def _get_cache_key(self, *args):
        return "{}-{}".format(
            self.__class__.__name__,
            "_".join([
                str(a) for a in args
            ])
        )

    def _get_data(self, *args):
        raise NotImplementedError("{} does not implement _get_data()".format(
            self.__class__.__name__
        ))


class SteamAPI(CachedAPI):
    BASE_URL = None

    def __init__(self, key=None):
        if key:
            self.key = key
        elif DEFAULT_KEY:
            self.key = DEFAULT_KEY
        else:
            raise AttributeError(
                "No key given to {} and no default key set".format(
                    self.__class__.__name__
                )
            )

    @staticmethod
    def set_default_key(key):
        global DEFAULT_KEY
        DEFAULT_KEY = key

    def _fetch(self, params):
        if not self.BASE_URL:
            raise AttributeError("{} does not have a BASE_URL".format(
                self.__class__.__name__
            ))

        payload = copy(params)
        payload["key"] = self.key

        if not "format" in payload:
            payload["format"] = "json"

        req = requests.get(self.get_url(), params=payload)

        print("Fetched {} info for {} from API".format(
            self.__class__.__name__, " / ".join([
                str(params[k]) for k in params
            ])
        ))

        return req.text.encode('utf-8')

    def get_url(self):
        return "{}{}".format(ROOT_URL, self.BASE_URL)


class GetOwnedGames(SteamAPI):
    BASE_URL = "/IPlayerService/GetOwnedGames/v0001/"

    def _get_data(self, steam_id):
        data = self._fetch({
            "steamid": steam_id,
            "include_appinfo": 1,
        })

        return json.loads(data)


class GetSteamID64(CachedAPI):
    URL = "http://steamcommunity.com/id/{name}/?xml=1"

    def _get_data(self, name):
        data = self._fetch(name)
        tree = etree.fromstring(data)
        ids = tree.xpath('//steamID64//text()')

        return "".join(ids)

    def _get_cache_key(self, name):
        return "{}-{}".format(
            self.__class__.__name__,
            name.encode("hex")
        )

    def _fetch(self, name):
        req = requests.get(self.get_url(name))

        if req.status_code == requests.codes.ok:
            response = req.text.encode("utf-8")

            return response
        else:
            req.raise_for_status()

    def get_url(self, name):
        return self.URL.format(name=name)


class GetAppData(CachedAPI):
    URL = "http://store.steampowered.com/app/{appid}/"

    def _get_data(self, app_id):
        data = self._fetch(app_id)
        print("Fetched {} info for app {} from API".format(
            self.__class__.__name__, app_id
        ))

        tree = html.fromstring(data)
        reviews = tree.xpath(
            '//span[contains(@class, "game_review_summary")]/text()'
        )

        return "".join(reviews)

    def _fetch(self, app_id):
        req = requests.get(self.get_url(app_id))

        if req.status_code == requests.codes.ok:
            response = req.text.encode("utf-8")

            return response
        else:
            req.raise_for_status()

    def get_url(self, app_id):
        return self.URL.format(appid=app_id)
