class SGCError(Exception):
    def to_response(self):
        return {
            "type": "error",
            "cls": self.__class__.__name__,
            "message": self.MESSAGE
        }


class Wrapped(SGCError):
    def __init__(self, orig):
        self.orig = orig

    def to_response(self):
        return {
            "type": "error",
            "cls": self.orig.__class__.__name__,
            "message": str(self.orig)
        }

class UserNotFound(SGCError):
    MESSAGE = "User not found. Your username is e.g. on the Steam community URL https://steamcommunity.com/id/USERNAME"


class APIError(SGCError):
    MESSAGE = "Error communicating with Steam"
