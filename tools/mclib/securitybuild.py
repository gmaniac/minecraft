"""Security device + block model builder. Reuses the vehicle region map for colors.

Entity devices (build_device): small gadgets; the turret has a rotatable "barrel" bone.
Block devices (build_block): camera/monitor/door/keypad/siren/hub in block space.
"""
from __future__ import annotations
from .geometry import Geometry


# ---------------- active entity devices ----------------
def build_device(kind):
    g = Geometry(f"geometry.wf_{kind}_dev", 1, 1)
    g.bone("root", (0, 0, 0))
    {"sensor": _sensor, "tripwire": _tripwire, "turret": _turret, "laser": _laser}[kind](g)
    g.tex_w = g.tex_h = 64
    g.autobounds(pad=2)
    return g


def _sensor(g):
    b = g.bone("body", (0, 4, 0), parent="root")
    b.cube([-3, 2, -3], [6, 5, 4], [0, 0], region="body")       # housing
    b.cube([-1, 0, -1], [2, 2, 2], [0, 0], region="dark")       # mount
    b.cube([-2, 3.5, -4], [4, 2.5, 1], [0, 0], region="glass")  # lens


def _tripwire(g):
    b = g.bone("body", (0, 0, 0), parent="root")
    b.cube([-1.5, 0, -1.5], [3, 10, 3], [0, 0], region="body")  # post
    b.cube([-2, 9, -2], [4, 3, 4], [0, 0], region="dark")
    b.cube([-1, 10, -2.5], [2, 1.5, 1], [0, 0], region="accent")  # emitter eye


def _turret(g):
    base = g.bone("body", (0, 2, 0), parent="root")
    base.cube([-4, 0, -4], [8, 3, 8], [0, 0], region="dark")    # base
    base.cube([-3, 3, -3], [6, 4, 6], [0, 0], region="body")    # dome
    barrel = g.bone("barrel", (0, 5, -2), parent="body")        # rotates in script-driven anim
    barrel.cube([-1.2, 4, -8], [2.4, 2.4, 7], [0, 0], region="trim")
    barrel.cube([-1.6, 3.6, -8.5], [3.2, 3.2, 1.5], [0, 0], region="accent")  # muzzle


def _laser(g):
    base = g.bone("body", (0, 2, 0), parent="root")
    base.cube([-4, 0, -4], [8, 3, 8], [0, 0], region="dark")
    base.cube([-3, 3, -3], [6, 5, 6], [0, 0], region="body")
    emit = g.bone("barrel", (0, 6, -3), parent="body")
    emit.cube([-2, 5, -6], [4, 4, 4], [0, 0], region="trim")
    emit.cube([-1.4, 5.6, -7], [2.8, 2.8, 1.5], [0, 0], region="accent")  # lens (glowing)


# ---------------- interact blocks (block space -8..8 / 0..16) ----------------
def build_block(geo_kind):
    g = Geometry(f"geometry.wf_secblk_{geo_kind}", 1, 1)
    b = g.bone("block", (0, 0, 0))
    {"camera": _b_camera, "monitor": _b_monitor, "door": _b_door, "door_open": _b_door_open,
     "keypad": _b_keypad, "siren": _b_siren, "hub": _b_hub}[geo_kind](b)
    g.tex_w = g.tex_h = 64
    g.bounds = [2, 2]
    g.bounds_offset = [0, 8, 0]
    return g


def _b_camera(b):
    b.cube([-2, 8, 4], [4, 4, 4], [0, 0], region="dark")        # mount on back wall
    b.cube([-3, 6, -4], [6, 5, 8], [0, 0], region="body")       # body
    b.cube([-2, 7, -5], [4, 3, 1], [0, 0], region="glass")      # lens
    b.cube([-0.5, 11, -1], [1, 2, 1], [0, 0], region="accent")  # status LED


def _b_monitor(b):
    b.cube([-7, 1, 5], [14, 12, 2], [0, 0], region="body")      # bezel on wall
    b.cube([-6, 2, 4.6], [12, 10, 0.5], [0, 0], region="glass")  # screen
    b.cube([-7, 0, 5], [14, 1, 3], [0, 0], region="dark")       # base shelf


def _b_door(b):
    # default (closed) geometry — full panel; open permutation hides it via thin slab
    b.cube([-8, 0, -1.5], [16, 16, 3], [0, 0], region="body")
    b.cube([-7, 1, -2], [14, 14, 0.5], [0, 0], region="trim")   # inset
    b.cube([4, 7, -2.2], [1, 3, 0.6], [0, 0], region="accent")  # handle/light


def _b_door_open(b):
    # door swung to the side — passable; small post + thin panel against one edge
    b.cube([6, 0, -2], [2, 16, 3], [0, 0], region="body")
    b.cube([6, 1, -2.2], [1.5, 14, 0.5], [0, 0], region="trim")


def _b_keypad(b):
    b.cube([-3, 4, 6], [6, 8, 2], [0, 0], region="body")        # panel on wall
    for r in range(3):
        for c in range(3):
            b.cube([-2.2 + c * 1.8, 5 + r * 2, 5.6], [1.2, 1.2, 0.4], [0, 0], region="accent")
    b.cube([-2.5, 10.5, 5.6], [5, 1, 0.4], [0, 0], region="glass")  # display


def _b_siren(b):
    b.cube([-2, 0, -2], [4, 2, 4], [0, 0], region="dark")
    b.cube([-3, 2, -3], [6, 6, 6], [0, 0], region="body")       # body
    b.cube([-2.5, 8, -2.5], [5, 4, 5], [0, 0], region="glass")  # light dome


def _b_hub(b):
    b.cube([-7, 0, 2], [14, 3, 6], [0, 0], region="dark")       # desk
    b.cube([-7, 3, 6], [14, 9, 2], [0, 0], region="body")       # console back
    b.cube([-6, 4, 5.6], [12, 7, 0.5], [0, 0], region="glass")  # screen
    b.cube([-6, 0, -2], [12, 1, 4], [0, 0], region="trim")      # keyboard shelf
