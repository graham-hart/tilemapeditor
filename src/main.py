import math
import sys
from enum import Enum

import pygame as pg

import utils
from map import Map
import argparse


class DrawMode(Enum):
    PEN = 0
    ERASE = 1
    FILL = 2
    NONE = 3


COLORS = {
    "TEAL": "#4a7a96",
    "BLUE": "#333f58",
    "BLACK": "#292831",
    "PINK": "#ee8695",
    "PEACH": "#fbbbad"
}

CONFIG = {
    "draw_mode": DrawMode.PEN,
    "selected_img": "",
    "save_on_exit": True,
    "remove_tiles_not_in_palette": True,
    "move_speed": 3,
    "scale": 16,
}

CONTROLS = {
    "exit": [pg.K_ESCAPE],
    "erase": [pg.K_e],
    "pen": [pg.K_p],
    "move_up": [pg.K_w, pg.K_UP],
    "move_down": [pg.K_s, pg.K_DOWN],
    "move_left": [pg.K_a, pg.K_LEFT],
    "move_right": [pg.K_d, pg.K_RIGHT],
    "save": [pg.K_g],
    "no_draw": [pg.K_n],
    "zoom_in": [pg.K_EQUALS],
    "zoom_out": [pg.K_MINUS]
}
SIZE = WIDTH, HEIGHT = 1600, 900
SIDEBAR_SIZE = SIDEBAR_WIDTH, SIDEBAR_HEIGHT = WIDTH / 4, HEIGHT


def exit(tilemap):
    if CONFIG["save_on_exit"]:
        tilemap.save()
    sys.exit()


def world_mouse_pos(translation, screen_x, screen_y):
    return math.floor((screen_x - SIDEBAR_WIDTH - translation[0]) / CONFIG["scale"]), math.floor(
        (screen_y - translation[1]) / CONFIG["scale"])


def draw_sidebar(palette, screen):
    pg.draw.rect(screen, COLORS["TEAL"], ((0, 0), (SIDEBAR_WIDTH, SIDEBAR_HEIGHT / 2)))
    pg.draw.rect(screen, COLORS["BLUE"], ((0, SIDEBAR_HEIGHT / 2), (SIDEBAR_WIDTH, SIDEBAR_HEIGHT / 2)))
    for name, i in palette.items():
        screen.blit(pg.transform.scale(i[0], (20, 20)), i[1])
        if CONFIG["selected_img"] == name:
            pg.draw.rect(screen, COLORS["PEACH"], i[1].inflate(4, 4), width=4, border_radius=2)


def swap_image(key, palette):
    num = pg.key.name(key)
    if num.isdigit():
        num = int(num)
        if len(palette.keys()) >= num:
            CONFIG["selected_img"] = list(palette.keys())[num - 1]


def key_down(key, tilemap, movement, palette):
    if key in CONTROLS["exit"]:
        exit(tilemap)
    elif key in CONTROLS["save"]:
        tilemap.save()
    elif key in CONTROLS["erase"]:
        CONFIG["draw_mode"] = DrawMode.ERASE
    elif key in CONTROLS["pen"]:
        CONFIG["draw_mode"] = DrawMode.PEN
    elif key in CONTROLS["no_draw"]:
        CONFIG["draw_mode"] = DrawMode.NONE
    elif key in CONTROLS["move_up"]:
        movement[1] = CONFIG["move_speed"]
    elif key in CONTROLS["move_down"]:
        movement[1] = -CONFIG["move_speed"]
    elif key in CONTROLS["move_left"]:
        movement[0] = -CONFIG["move_speed"]
    elif key in CONTROLS["move_right"]:
        movement[0] = CONFIG["move_speed"]
    elif key in CONTROLS["zoom_in"] and CONFIG["scale"] <= 62:
        CONFIG["scale"] += 2
    elif key in CONTROLS["zoom_out"] and CONFIG["scale"] > 2:
        CONFIG["scale"] -= 2
    else:
        swap_image(key, palette)


def key_up(key, movement):
    if key in CONTROLS["move_up"] or key in CONTROLS["move_down"]:
        movement[1] = 0
    elif key in CONTROLS["move_left"] or key in CONTROLS["move_right"]:
        movement[0] = 0


def mouse_down(btn, pos, palette, tilemap, translation):
    if btn == pg.BUTTON_LEFT:
        x, y = pos
        if x <= SIDEBAR_WIDTH:
            for key, img in palette.items():
                if img[1].x <= x <= img[1].x + img[1].width and img[1].y <= y <= img[1].y + img[1].height:
                    CONFIG["selected_img"] = key
                    break
        elif CONFIG["draw_mode"] != DrawMode.NONE:
            loc = world_mouse_pos(translation, *pos)
            if CONFIG["draw_mode"] == DrawMode.PEN:
                tilemap[loc] = CONFIG["selected_img"]
            elif CONFIG["draw_mode"] == DrawMode.ERASE and loc in tilemap:
                del tilemap[loc]


def handle_event(evt, palette, tilemap, translation, movement):
    if evt.type == pg.QUIT:
        exit(tilemap)
    elif evt.type == pg.KEYDOWN:
        key_down(evt.key, tilemap, movement, palette)
    elif evt.type == pg.KEYUP:
        key_up(evt.key, movement)
    elif evt.type == pg.MOUSEBUTTONDOWN:
        mouse_down(evt.button, evt.pos, palette, tilemap, translation)


def draw_map(tilemap, screen, palette, translation):
    for k, v in sorted(tilemap.items(), reverse=True):
        pos = utils.parse_map_key(k)
        rect = pg.Rect(int(pos[0]) * CONFIG["scale"] + SIDEBAR_WIDTH, int(pos[1]) * CONFIG["scale"],
                       CONFIG["scale"], CONFIG["scale"])
        img = palette[v][0]
        if CONFIG["scale"] != 1:
            img = pg.transform.scale(img, (CONFIG["scale"], CONFIG["scale"]))
        rect.move_ip(translation)
        rect.inflate(CONFIG["scale"], CONFIG["scale"])
        if v in palette.keys():
            if SIDEBAR_WIDTH - rect.width <= rect.x <= WIDTH and -rect.height <= rect.y <= HEIGHT:
                screen.blit(img, rect)
        else:
            print(f"Image '{v}' not found in palette.")
            if CONFIG["remove_tiles_not_in_palette"]:
                del tilemap[pos]


def draw_cursor(sc, x, y):
    length = 10
    width = 3
    gap = 5
    color = COLORS["PINK"]
    pg.draw.line(sc, color, (x - length, y), (x - gap, y), width=width)
    pg.draw.line(sc, color, (x + length, y), (x + gap, y), width=width)
    pg.draw.line(sc, color, (x, y - length), (x, y - gap), width=width)
    pg.draw.line(sc, color, (x, y + length), (x, y + gap), width=width)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=str, help="Output file for the map")
    parser.add_argument("-i", type=str, help="Input file for the map (optional)", metavar="input")
    args = parser.parse_args()
    pg.init()
    pg.mouse.set_visible(False)
    sc = pg.display.set_mode(SIZE)
    pg.display.set_caption("Tile Map Editor")
    PALETTE = {d[0]: (pg.transform.scale(d[1], (20, 20)), pg.Rect(WIDTH / 18, index * 24 + 32, 20, 20)) for index, d in
               enumerate(utils.load_image_dir("imgs").items())}
    CONFIG["selected_img"] = list(PALETTE.keys())[0]
    MAP = Map(args.output, args.i)
    translation = [0, 0]
    movement = [0, 0]
    while True:
        for evt in pg.event.get():
            handle_event(evt, PALETTE, MAP, translation, movement)
        translation[0] -= movement[0]
        translation[1] += movement[1]
        sc.fill(COLORS["BLACK"])
        draw_map(MAP, sc, PALETTE, translation)
        draw_sidebar(PALETTE, sc)
        draw_cursor(sc, *pg.mouse.get_pos())
        pg.display.flip()


if __name__ == "__main__":
    main()
