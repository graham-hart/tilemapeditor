import json
import os

import pygame as pg


def load_image_dir(directory):
    imgs = {}
    d = os.fsencode(directory)
    for i, file in enumerate(os.listdir(d)):
        fn = os.fsdecode(file)
        imgs[os.path.splitext(fn)[0]] = pg.image.load(f"./{directory}/{fn}").convert()
    return imgs


def parse_map_key(key: str):
    return tuple(key.split(","))


def read_map(fn: str):
    path = f"./{fn}.json"
    if os.path.exists(path):
        with open(path, "r+") as file:
            data = file.read()
            return json.loads(data) if data != "" else {}
    else:
        f = open(path, "x")
        f.close()
        return {}


def write_map(tilemap):
    with open(f"./{tilemap.fn}.json", "w") as file:
        file.write(json.dumps(tilemap))
