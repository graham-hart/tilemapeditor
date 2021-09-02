import datetime

import utils


class Map(dict):
    def __init__(self, fn=None):
        super().__init__()
        if fn is None:
            self.fn = datetime.datetime.now()
        else:
            self.fn = fn
        for k, v in utils.read_map(fn).items():
            super().__setitem__(k, v)
        self.fn = fn

    @staticmethod
    def format_key(key: tuple):
        return f"{int(key[0])},{int(key[1])},{int(key[2])}"

    def __getitem__(self, key: tuple):
        return super().__getitem__(Map.format_key(key))

    def __setitem__(self, key: tuple, value: str):
        super().__setitem__(Map.format_key(key), value)

    def __delitem__(self, key: tuple):
        super().__delitem__(Map.format_key(key))

    def __contains__(self, key: tuple):
        return super().__contains__(Map.format_key(key))

    def __repr__(self):
        return f"Map[{super().__repr__()}]"

    def save(self):
        utils.write_map(self)
