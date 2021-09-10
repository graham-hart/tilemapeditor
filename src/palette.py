import math

import pygame as pg


class Palette:
    def __init__(self):
        self.dict = {}
        self.current = ""

    def add_img(self, name, img):
        n = len(self.dict) + 1
        self.dict[name] = {"palette_img": pg.transform.scale(img, (20, 20)),
                           "palette_rect": img.get_rect().move(50, 50 + n * 32), "map_img": img}
        self.current = name

    def get_img(self, name):
        return self.dict[name]

    def __contains__(self, key):
        return key in self.dict

    def keys(self):
        return self.dict.keys()

    def values(self):
        return self.dict.values()

    def items(self):
        return self.dict.items()

    def scale_imgs(self, cam):
        size = cam.project_dist(1, 1)
        for i in self.dict.values():
            size_f = cam.project_dist(1, 1)
            size = math.ceil(size_f[0]), math.ceil(size_f[1])
            i["map_img"] = pg.transform.scale(i["map_img"], size)
