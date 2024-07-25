
class Command(object):
    def __init__(self, names, func, help="No help text provided"):
        if isinstance(names, str):
            raise TypeError('Names should be a str list, not str!')

        self.names = names
        self.func = func
        self.help = help
