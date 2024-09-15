from enum import Enum

class Command(object):
    def __init__(self, names, func, help="No help text provided"):
        if isinstance(names, str):
            raise TypeError('Names should be a str list, not str!')

        self.names = sorted(names, key=lambda x: len(x), reverse=True)
        self.func = func
        self.help = help

class Event(Enum):
    USER_JOINED_VC = 0
    USER_LEFT_VC = 1
