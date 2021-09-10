import math
import sys
from enum import Enum

import pygame as pg

import utils
from camera import Camera
from map import Map


# ----------------------------------------------------------- Constants etc
class DrawMode(Enum):
    PEN = "pen"
    ERASE = "erase"
    FILL = "fill"
    NONE = "none"


COLORS = {
    "TEAL": (74, 122, 150),
    "BLUE": (51, 63, 88),
    "BLACK": (41, 40, 49),
    "PINK": (238, 134, 149),
    "PEACH": (251, 187, 173)
}

SETTINGS = {
    "draw_mode": DrawMode.PEN,
    "selected_tile": "",
    "save_on_exit": False,
    "remove_tiles_not_in_palette": True,
    "move_speed": 0.1,
    "curr_layer": 0,
    "pen_size": 2,
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
    "layer_up": [pg.K_RIGHTBRACKET],
    "layer_down": [pg.K_LEFTBRACKET],
    "shrink_pen": [pg.K_COMMA],
    "scale_pen": [pg.K_PERIOD],
    "inflate": [pg.K_EQUALS],
    "deflate": [pg.K_MINUS]
}
SIZE = WIDTH, HEIGHT = 1200, 900
SIDEBAR_SURF_SIZE = SIDEBAR_WIDTH, SIDEBAR_HEIGHT = 300, HEIGHT
MAP_SURF_SIZE = MAP_WIDTH, MAP_HEIGHT = WIDTH - SIDEBAR_WIDTH, HEIGHT


# Run when exiting editor
def exit_pg(tilemap):
    if SETTINGS["save_on_exit"]:
        tilemap.save()
    sys.exit()


# Remove tiles with no image from map
def sanitize_map(tilemap, palette):
    for k, v in sorted(tilemap.items(), reverse=True):
        if v not in palette.keys():
            pos = utils.parse_map_key(k)
            if SETTINGS["remove_tiles_not_in_palette"]:
                del tilemap[pos]


# ----------------------------------------------------------- Controls-related funcs

def swap_image(key, palette):
    num = pg.key.name(key)
    if num.isdigit():
        num = int(num)
        if len(palette.keys()) >= num:
            SETTINGS["selected_tile"] = list(palette.keys())[num - 1]


def world_mouse_pos(camera, screen_x, screen_y):
    p = camera.unproject(screen_x - SIDEBAR_WIDTH, screen_y)
    return math.floor(p[0]), math.floor(p[1]), SETTINGS["curr_layer"]


def key_down(key, tilemap, palette, cam):
    if key in CONTROLS["exit"]:
        exit_pg(tilemap)
    elif key in CONTROLS["save"]:
        tilemap.save()
    elif key in CONTROLS["erase"]:
        SETTINGS["draw_mode"] = DrawMode.ERASE
    elif key in CONTROLS["pen"]:
        SETTINGS["draw_mode"] = DrawMode.PEN
    elif key in CONTROLS["no_draw"]:
        SETTINGS["draw_mode"] = DrawMode.NONE
    elif key in CONTROLS["layer_down"] and SETTINGS["curr_layer"] > 0:
        SETTINGS["curr_layer"] -= 1
    elif key in CONTROLS["layer_up"] and SETTINGS["curr_layer"] < 10:
        SETTINGS["curr_layer"] += 1
    elif key in CONTROLS["shrink_pen"] and SETTINGS["pen_size"] > 1:
        SETTINGS["pen_size"] -= 1
    elif key in CONTROLS["scale_pen"] and SETTINGS["pen_size"] < 4:
        SETTINGS["pen_size"] += 1
    elif key in CONTROLS["inflate"]:
        cam.inflate(1, 1)
    elif key in CONTROLS["deflate"]:
        cam.inflate(-1, -1)
    else:
        swap_image(key, palette)


def mouse_down(btn, pos, palette):
    if btn == pg.BUTTON_LEFT:
        x, y = pos
        if x <= SIDEBAR_WIDTH:
            for key, img in palette.items():
                if img[1].x <= x <= img[1].x + img[1].width and img[1].y <= y <= img[1].y + img[1].height:
                    SETTINGS["selected_tile"] = key
                    break


def key_pressed_in_list(lst):
    k = pg.key.get_pressed()
    for i in lst:
        if k[i]:
            return True
    return False


def move(cam):
    m = [0, 0]
    if key_pressed_in_list(CONTROLS["move_up"]):
        m[1] -= SETTINGS["move_speed"]
    if key_pressed_in_list(CONTROLS["move_down"]):
        m[1] += SETTINGS["move_speed"]
    if key_pressed_in_list(CONTROLS["move_left"]):
        m[0] -= SETTINGS["move_speed"]
    if key_pressed_in_list(CONTROLS["move_right"]):
        m[0] += SETTINGS["move_speed"]
    cam.translate(*m)


# ----------------------------------------------------------- Events
def handle_event(evt, palette, tilemap, cam):
    if evt.type == pg.QUIT:
        exit_pg(tilemap)
    elif evt.type == pg.KEYDOWN:
        key_down(evt.key, tilemap, palette, cam)
    elif evt.type == pg.MOUSEBUTTONDOWN:
        mouse_down(evt.button, evt.pos, palette)


# ----------------------------------------------------------- Rendering funcs
def draw_sidebar(palette, surf, font, wmx, wmy, fps):
    pg.draw.rect(surf, COLORS["TEAL"], ((0, 0), (SIDEBAR_WIDTH, SIDEBAR_HEIGHT / 2)))
    pg.draw.rect(surf, COLORS["BLUE"], ((0, SIDEBAR_HEIGHT / 2), (SIDEBAR_WIDTH, SIDEBAR_HEIGHT / 2)))
    for name, i in palette.items():
        surf.blit(pg.transform.scale(i[0], (20, 20)), i[1])
        if SETTINGS["selected_tile"] == name:
            pg.draw.rect(surf, COLORS["PEACH"], i[1].inflate(4, 4), width=4, border_radius=2)
    text_blit(surf, font,
              f"{wmx},{wmy}\nLayer: {SETTINGS['curr_layer']}\nMode: {SETTINGS['draw_mode'].value}\nPen size: {SETTINGS['pen_size']}\nFPS: {math.floor(fps)}",
              (20, HEIGHT - 120), COLORS["PINK"])


def draw_map(tilemap, surface, palette, cam):
    surface.fill(COLORS["BLACK"])
    top_left, bottom_right = cam.bounds()
    for x in range(math.floor(top_left.x), math.ceil(bottom_right.x)):
        for y in range(math.floor(top_left.y), math.ceil(bottom_right.y)):
            if utils.format_map_key((x, y)) in tilemap.dict:
                for z, t in sorted(sorted(tilemap.get_layer((x, y)).items(), key=lambda i: i[0]),
                                   key=lambda i: i[0] == SETTINGS["curr_layer"]):
                    r = pg.Rect(cam.project_rect((x, y, 1, 1)))
                    size_f = cam.project_dist(1,1)
                    size = math.ceil(size_f[0]),math.ceil(size_f[1])
                    # TODO: Make this better lol
                    img = pg.transform.scale(palette[t][0], size)
                    surface.blit(img, r)



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


# ----------------------------------------------------------- Map Editing
def pen_size_draw(mode, radius, loc, tilemap):
    wmx, wmy, wmz = loc
    if radius:
        for x in range(wmx - radius, wmx + radius):
            for y in range(wmy - radius, wmy + radius):
                if mode == DrawMode.PEN:
                    tilemap.set_item((x, y, wmz), SETTINGS["selected_tile"])
                elif mode == DrawMode.ERASE and (x, y, wmz) in tilemap:
                    tilemap.del_item((x, y, wmz))
    else:
        if mode == DrawMode.PEN:
            tilemap.set_item((wmx, wmy, wmz), SETTINGS["selected_tile"])
        elif mode == DrawMode.ERASE and (wmx, wmy, wmz) in tilemap:
            tilemap.del_item((wmx, wmy, wmz))


def paint(cam, tilemap):
    if pg.mouse.get_pressed(3)[pg.BUTTON_LEFT - 1]:
        if SETTINGS["draw_mode"] != DrawMode.NONE:
            pos = pg.mouse.get_pos()
            if pos[0] > SIDEBAR_WIDTH:
                loc = wmx, wmy, wmz = world_mouse_pos(cam, *pos)
                radius = math.floor(SETTINGS["pen_size"] / 2)
                if SETTINGS["draw_mode"] == DrawMode.PEN or SETTINGS["draw_mode"] == DrawMode.ERASE:
                    pen_size_draw(SETTINGS["draw_mode"], radius, loc, tilemap)


def main():
    # ----------------------------------------------------------- Basic Pygame Initialization
    pg.init()
    pg.mouse.set_visible(False)
    screen = pg.display.set_mode(SIZE)
    pg.display.set_caption("Tile Map Editor")
    font = pg.font.Font(pg.font.get_default_font(), 16)
    clock = pg.time.Clock()

    # ----------------------------------------------------------- Setup surfaces for rendering
    sidebar_surf = pg.Surface(SIDEBAR_SURF_SIZE)
    sidebar_surf_rect = sidebar_surf.get_rect()
    map_surf = pg.Surface(MAP_SURF_SIZE)
    map_surf_rect = map_surf.get_rect().move(SIDEBAR_WIDTH, 0)
    CAM = Camera(MAP_SURF_SIZE, (40, 40))
    # ----------------------------------------------------------- Palette setup
    PALETTE = {d[0]: (pg.transform.scale(d[1], (20, 20)), pg.Rect(WIDTH / 18, index * 24 + 32, 20, 20)) for index, d in
               enumerate(utils.load_image_dir("imgs").items())}
    SETTINGS["selected_tile"] = list(PALETTE.keys())[0]
    # ----------------------------------------------------------- Map & Translation
    TILEMAP = Map("map.json")
    while True:
        # ----------------------------------------------------------- Events
        for evt in pg.event.get():
            handle_event(evt, PALETTE, TILEMAP, CAM)
        pg.event.clear()
        paint(CAM, TILEMAP)  # Paint on map if left mb pressed
        move(CAM)  # Change translation based on input (if any)

        # ----------------------------------------------------------- Draw onto screen
        mouse_pos = mx, my = pg.mouse.get_pos()
        world_pos = wmx, wmy, wmz = world_mouse_pos(CAM, *mouse_pos)
        draw_map(TILEMAP, map_surf, PALETTE, CAM)
        draw_sidebar(PALETTE, sidebar_surf, font, wmx, wmy, clock.get_fps())
        screen.blit(map_surf, map_surf_rect)
        screen.blit(sidebar_surf, sidebar_surf_rect)
        draw_cursor(screen, *mouse_pos)
        pg.display.flip()
        clock.tick()


if __name__ == "__main__":
    main()
