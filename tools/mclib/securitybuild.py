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
    b.cube([-1, 0, -1], [2, 2, 2], [0, 0], region="dark")        # wall mount
    b.cube([-3, 2, -3], [6, 5, 4], [0, 0], region="body")        # housing
    b.cube([-3.2, 3, -3.2], [6.4, 1, 1.2], [0, 0], region="trim")  # vent band
    b.cube([-2.2, 3.2, -4], [4.4, 2.6, 1], [0, 0], region="glass")  # lens
    b.cube([2, 6, -3], [0.8, 1, 0.8], [0, 0], region="accent")   # status LED


def _tripwire(g):
    b = g.bone("body", (0, 0, 0), parent="root")
    b.cube([-2.5, 0, -2.5], [5, 1, 5], [0, 0], region="dark")    # base plate
    b.cube([-1.5, 1, -1.5], [3, 9, 3], [0, 0], region="body")    # post
    b.cube([-2, 9, -2], [4, 3.5, 4], [0, 0], region="trim")      # emitter head
    b.cube([-2.2, 10, -2.6], [4.4, 1.5, 1], [0, 0], region="accent")  # emitter eye
    b.cube([-0.6, 12.4, -0.6], [1.2, 1, 1.2], [0, 0], region="dark")  # cap


def _turret(g):
    base = g.bone("body", (0, 2, 0), parent="root")
    base.cube([-4.5, 0, -4.5], [9, 2, 9], [0, 0], region="dark")     # base plate
    base.cube([-3.5, 0, -3.5], [7, 1, 7], [0, 0], region="trim")     # base ring
    base.cube([-3, 2, -3], [6, 4, 6], [0, 0], region="body")         # housing
    base.cube([-3.2, 3, -3.2], [6.4, 1, 6.4], [0, 0], region="trim")  # housing band
    base.cube([2.5, 4, -1], [2, 3, 4], [0, 0], region="dark")        # ammo drum
    base.cube([-0.5, 7, -1], [1, 1.5, 1], [0, 0], region="accent")   # status light
    barrel = g.bone("barrel", (0, 5, -2), parent="body")            # script-rotated
    barrel.cube([-2, 4, -9], [4, 3, 8], [0, 0], region="trim")       # barrel housing
    for bx in (-1.1, 0.3):                                          # twin barrels
        barrel.cube([bx, 4.4, -11], [0.8, 0.8, 3], [0, 0], region="dark")
    barrel.cube([-1.6, 3.8, -9.6], [3.2, 3.2, 1.2], [0, 0], region="accent")  # muzzle ring


def _laser(g):
    base = g.bone("body", (0, 2, 0), parent="root")
    base.cube([-4.5, 0, -4.5], [9, 2, 9], [0, 0], region="dark")     # base plate
    base.cube([-3.5, 0, -3.5], [7, 1, 7], [0, 0], region="trim")     # base ring
    base.cube([-3, 2, -3], [6, 5, 6], [0, 0], region="body")         # housing
    base.cube([-3.2, 4, -3.2], [6.4, 1, 6.4], [0, 0], region="trim")  # trim band
    emit = g.bone("barrel", (0, 6, -3), parent="body")             # script-rotated
    emit.cube([-2.5, 5, -7], [5, 5, 5], [0, 0], region="trim")       # emitter housing
    emit.cube([-2, 5.4, -7.7], [4, 4, 1], [0, 0], region="dark")     # housing face
    emit.cube([-1.4, 5.6, -8.3], [2.8, 2.8, 1.2], [0, 0], region="accent")  # glowing lens
    emit.cube([-0.6, 5.8, -8.7], [1.2, 1.2, 0.6], [0, 0], region="glass")   # lens core


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
    b.cube([-1, 9, 5], [2, 2, 3], [0, 0], region="dark")        # wall plate
    b.cube([-0.6, 8, 1], [1.2, 1.2, 4], [0, 0], region="trim")  # swivel arm
    b.cube([-3, 6, -4], [6, 5, 8], [0, 0], region="body")       # body
    b.cube([-3.2, 6.5, -4.5], [6.4, 4, 1], [0, 0], region="dark")  # lens hood
    b.cube([-2, 7, -5], [4, 3, 1], [0, 0], region="glass")      # lens
    b.cube([-0.5, 11.2, -1], [1, 1.5, 1], [0, 0], region="accent")  # status LED


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
    b.cube([-7.2, 3, 6], [14.4, 1, 2], [0, 0], region="trim")   # console base trim
    b.cube([-6, 4.5, 5.5], [7, 6, 0.5], [0, 0], region="glass")  # main screen
    b.cube([1.5, 4.5, 5.5], [4, 6, 0.5], [0, 0], region="accent")  # status panel
    b.cube([-6, 0, -2], [12, 1, 4], [0, 0], region="trim")      # keyboard shelf
    for c in range(5):                                          # keypad buttons
        b.cube([-5 + c * 2.2, 1, -1.5], [1.4, 0.6, 1.4], [0, 0], region="accent")
