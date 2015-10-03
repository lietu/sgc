import pickle


class CacheManager(object):
    save_queue = {}

    @staticmethod
    def load(key):
        try:
            with open("cache/{}".format(key), 'rb') as f:
                return pickle.loads(f.read())
        except IOError:
            print("Cache miss: {}".format(key))
            return None

    @classmethod
    def save(cls, key, data):
        pickled = pickle.dumps(data)
        cls.save_queue[key] = pickled

    @classmethod
    def write_to_cache(cls):
        print("Have {} keys to cache".format(len(cls.save_queue.keys())))
        for key in cls.save_queue:
            pickled = cls.save_queue[key]
            print("Saving to cache: {}".format(key))

            with open("cache/{}".format(key), 'wb') as f:
                f.write(pickled)

        cls.save_queue = {}