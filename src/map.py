import utils


class Map(dict):
    def __init__(self, output_fn, input_fn=None):
        super().__init__()
        self.fn = output_fn
        if input_fn:
            for k, v in utils.read_map(input_fn).items():
                super().__setitem__(k, v)

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
