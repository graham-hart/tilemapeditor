import utils


class Map:
    def __init__(self, fn):
        self.dict = utils.read_map(fn)
        self.fn = fn

    def get_item(self, loc: tuple[int, int, int]):
        if utils.type_all(loc, int) and len(loc) == 3:
            x, y, z = loc
            k = utils.format_map_key((x, y))
            return self.dict[k][z]
        else:
            raise TypeError("Argument must be a tuple of ints with len 3")

    def set_item(self, loc: tuple[int, int, int], v):
        if utils.type_all(loc, int) and len(loc) == 3:
            x, y, z = loc
            k = utils.format_map_key((x, y))
            if k not in self.dict:
                self.dict[k] = {}
            self.dict[k][str(z)] = v
        else:
            raise TypeError("Argument must be a tuple of ints with len 3")

    def get_layer(self, loc: tuple[int, int]):
        if utils.type_all(loc, int) and len(loc) == 2:
            return self.dict[utils.format_map_key(loc)]
        else:
            raise TypeError("Argument must be a tuple of ints with len 2")

    def del_item(self, loc: tuple[int, int, int]):
        if utils.type_all(loc, int) and len(loc) == 3:
            x, y, z = loc
            k = utils.format_map_key((x, y))
            if len(self.dict[k]) == 1:
                del self.dict[k]
            else:
                del self.dict[k][z]
        else:
            raise TypeError("Argument must be a tuple of ints with len 3")

    def __contains__(self, loc):
        if utils.type_all(loc, int) and len(loc) == 3:
            x, y, z = loc
            k = utils.format_map_key((x, y))
            return k in self.dict and z in self.dict[k]
        else:
            raise TypeError("Argument must be a tuple of ints with len 3")

    def __iter__(self):
        return self.dict.__iter__()

    def __next__(self):
        return self.dict.__next__()

    def save(self):
        utils.write_map(self.dict, self.fn)

    def items(self):
        return self.dict.items()

    def keys(self):
        return self.dict.keys()

    def values(self):
        return self.dict.values()
