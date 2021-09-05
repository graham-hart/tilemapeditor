import argparse
import math
import sys
from enum import Enum

import pygame as pg

import utils
from map import Map


# ----------------------------------------------------------- Constants etc
class DrawMode(Enum):
    PEN = "pen"
    ERASE = "erase"
    FILL = "fill"
    NONE = "none"


COLORS = {
    "TEAL": (74,122,150),
    "BLUE": (51,63,88),
    "BLACK": (41,40,49),
    "PINK": (238,134,149),
    "PEACH": (251,187,173)
}

CONFIG = {
    "draw_mode": DrawMode.PEN,
    "selected_img": "",
    "save_on_exit": False,
    "remove_tiles_not_in_palette": True,
    "move_speed": 3,
    "scale": 16,
    "curr_layer": 0,
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
    "zoom_out": [pg.K_MINUS],
    "layer_up": [pg.K_RIGHTBRACKET],
    "layer_down": [pg.K_LEFTBRACKET],
}
SIZE = WIDTH, HEIGHT = 1600, 900
SIDEBAR_SIZE = SIDEBAR_WIDTH, SIDEBAR_HEIGHT = WIDTH / 4, HEIGHT
MAP_SIZE = MAP_WIDTH, MAP_HEIGHT = WIDTH - SIDEBAR_WIDTH, HEIGHT


# Run when exiting editor
def exit_pg(tilemap):
    if CONFIG["save_on_exit"]:
        tilemap.save()
    sys.exit()


# Remove tiles with no image from map
def sanitize_map(tilemap, palette):
    for k, v in sorted(tilemap.items(), reverse=True):
        if v not in palette.keys():
            pos = utils.parse_map_key(k)
            if CONFIG["remove_tiles_not_in_palette"]:
                del tilemap[pos]


# ----------------------------------------------------------- Controls-related funcs

def swap_image(key, palette):
    num = pg.key.name(key)
    if num.isdigit():
        num = int(num)
        if len(palette.keys()) >= num:
            CONFIG["selected_img"] = list(palette.keys())[num - 1]


def world_mouse_pos(translation, screen_x, screen_y):
    return math.floor((max(screen_x - SIDEBAR_WIDTH, 0) - translation[0]) / CONFIG["scale"]), math.floor(
        (screen_y - translation[1]) / CONFIG["scale"]), CONFIG["curr_layer"]


def key_down(key, tilemap, palette):
    if key in CONTROLS["exit"]:
        exit_pg(tilemap)
    elif key in CONTROLS["save"]:
        tilemap.save()
    elif key in CONTROLS["erase"]:
        CONFIG["draw_mode"] = DrawMode.ERASE
    elif key in CONTROLS["pen"]:
        CONFIG["draw_mode"] = DrawMode.PEN
    elif key in CONTROLS["no_draw"]:
        CONFIG["draw_mode"] = DrawMode.NONE
    elif key in CONTROLS["zoom_in"] and CONFIG["scale"] <= 62:
        CONFIG["scale"] += 2
    elif key in CONTROLS["zoom_out"] and CONFIG["scale"] > 2:
        CONFIG["scale"] -= 2
    elif key in CONTROLS["layer_down"] and CONFIG["curr_layer"] > 0:
        CONFIG["curr_layer"] -= 1
    elif key in CONTROLS["layer_up"] and CONFIG["curr_layer"] < 10:
        CONFIG["curr_layer"] += 1
    else:
        swap_image(key, palette)


def mouse_down(btn, pos, palette):
    if btn == pg.BUTTON_LEFT:
        x, y = pos
        if x <= SIDEBAR_WIDTH:
            for key, img in palette.items():
                if img[1].x <= x <= img[1].x + img[1].width and img[1].y <= y <= img[1].y + img[1].height:
                    CONFIG["selected_img"] = key
                    break


def key_pressed_in_list(lst):
    k = pg.key.get_pressed()
    for i in lst:
        if k[i]:
            return True
    return False


def move(translation):
    if key_pressed_in_list(CONTROLS["move_up"]):
        translation[1] += CONFIG["move_speed"]
    if key_pressed_in_list(CONTROLS["move_down"]):
        translation[1] -= CONFIG["move_speed"]
    if key_pressed_in_list(CONTROLS["move_left"]):
        translation[0] += CONFIG["move_speed"]
    if key_pressed_in_list(CONTROLS["move_right"]):
        translation[0] -= CONFIG["move_speed"]


# ----------------------------------------------------------- Events
def handle_event(evt, palette, tilemap):
    if evt.type == pg.QUIT:
        exit_pg(tilemap)
    elif evt.type == pg.KEYDOWN:
        key_down(evt.key, tilemap, palette)
    elif evt.type == pg.MOUSEBUTTONDOWN:
        mouse_down(evt.button, evt.pos, palette)


# ----------------------------------------------------------- Rendering funcs
def draw_sidebar(palette, surf, font, wmx, wmy):
    pg.draw.rect(surf, COLORS["TEAL"], ((0, 0), (SIDEBAR_WIDTH, SIDEBAR_HEIGHT / 2)))
    pg.draw.rect(surf, COLORS["BLUE"], ((0, SIDEBAR_HEIGHT / 2), (SIDEBAR_WIDTH, SIDEBAR_HEIGHT / 2)))
    for name, i in palette.items():
        surf.blit(pg.transform.scale(i[0], (20, 20)), i[1])
        if CONFIG["selected_img"] == name:
            pg.draw.rect(surf, COLORS["PEACH"], i[1].inflate(4, 4), width=4, border_radius=2)
    text_blit(surf, font, f"{wmx},{wmy}\nLayer: {CONFIG['curr_layer']}\nMode: {CONFIG['draw_mode'].value}",
              (20, HEIGHT - 50), COLORS["PINK"])


def draw_map(tilemap, surface, palette, translation):
    surface.fill(COLORS["BLACK"])
    lst = sorted(sorted(tilemap.items(), key=lambda i: utils.parse_map_key(i[0])[2], reverse=True),
                 key=lambda j: utils.parse_map_key(j[0])[2] == CONFIG["curr_layer"])
    for k, v in lst:
        loc = utils.parse_map_key(k)
        rect = pg.Rect(int(loc[0]) * CONFIG["scale"], int(loc[1]) * CONFIG["scale"],
                       CONFIG["scale"], CONFIG["scale"])
        img = palette[v][0]
        if CONFIG["scale"] != 1:
            img = pg.transform.scale(img, (CONFIG["scale"], CONFIG["scale"]))
        rect.move_ip(translation)
        rect.inflate(CONFIG["scale"], CONFIG["scale"])
        if v in palette.keys():
            if -rect.width <= rect.x <= MAP_WIDTH and -rect.height <= rect.y <= MAP_HEIGHT:
                # TODO: MAKE THIS ACTUALLY EFFICIENT
                if loc[2] == CONFIG["curr_layer"]:
                    img.set_alpha(255)
                else:
                    img.set_alpha(128)
                    if surface.get_at((rect.x, rect.y)) != COLORS["BLACK"]:
                        pg.draw.rect(surface, COLORS["BLACK"], rect)
                surface.blit(img, rect)


def draw_cursor(sc, x, y):
    length = 10
    width = 3
    gap = 5
    color = COLORS["PINK"]
    pg.draw.line(sc, color, (x - length, y), (x - gap, y), width=width)
    pg.draw.line(sc, color, (x + length, y), (x + gap, y), width=width)
    pg.draw.line(sc, color, (x, y - length), (x, y - gap), width=width)
    pg.draw.line(sc, color, (x, y + length), (x, y + gap), width=width)


def text_blit(surface, font, text, pos, color):
    lines = text.split("\n")
    px, py = pos
    for ln in lines:
        s = font.render(ln, True, color)
        surface.blit(s, (px, py, *s.get_size()))
        py += s.get_size()[1]


def main():
    # ----------------------------------------------------------- Parse CLI args for file IO
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=str, help="Output file for the map")
    parser.add_argument("-i", type=str, help="Input file for the map (optional)", metavar="input")
    args = parser.parse_args()

    # ----------------------------------------------------------- Basic Pygame Initialization
    pg.init()
    pg.mouse.set_visible(False)
    screen = pg.display.set_mode(SIZE)
    pg.display.set_caption("Tile Map Editor")
    font = pg.font.Font(pg.font.get_default_font(), 12)

    # ----------------------------------------------------------- Setup surfaces for rendering
    sidebar_surf = pg.Surface(SIDEBAR_SIZE)
    sidebar_surf_rect = sidebar_surf.get_rect()
    map_surf = pg.Surface(MAP_SIZE)
    map_surf_rect = map_surf.get_rect().move(SIDEBAR_WIDTH, 0)

    # ----------------------------------------------------------- Palette setup
    PALETTE = {d[0]: (pg.transform.scale(d[1], (20, 20)), pg.Rect(WIDTH / 18, index * 24 + 32, 20, 20)) for index, d in
               enumerate(utils.load_image_dir("imgs").items())}
    CONFIG["selected_img"] = list(PALETTE.keys())[0]

    # ----------------------------------------------------------- Map & Translation
    TILEMAP = Map(args.output, args.i)
    translation = [0, 0]
    while True:
        # ----------------------------------------------------------- Events
        for evt in pg.event.get():
            handle_event(evt, PALETTE, TILEMAP)

        # ----------------------------------------------------------- Paint on map
        if pg.mouse.get_pressed(3)[pg.BUTTON_LEFT - 1]:
            if CONFIG["draw_mode"] != DrawMode.NONE:
                pos = pg.mouse.get_pos()
                if pos[0] > SIDEBAR_WIDTH:
                    loc = world_mouse_pos(translation, *pos)
                    if CONFIG["draw_mode"] == DrawMode.PEN:
                        TILEMAP[loc] = CONFIG["selected_img"]
                    elif CONFIG["draw_mode"] == DrawMode.ERASE and loc in TILEMAP:
                        del TILEMAP[loc]

        move(translation)  # Change translation based on input (if any)

        # ----------------------------------------------------------- Draw onto screen
        mouse_pos = mx, my = pg.mouse.get_pos()
        world_pos = wmx, wmy, wmz = world_mouse_pos(translation, *mouse_pos)
        draw_map(TILEMAP, map_surf, PALETTE, translation)
        draw_sidebar(PALETTE, sidebar_surf, font, wmx, wmy)
        screen.blit(map_surf, map_surf_rect)
        screen.blit(sidebar_surf, sidebar_surf_rect)
        draw_cursor(screen, *mouse_pos)
        pg.display.flip()


if __name__ == "__main__":
    main()
