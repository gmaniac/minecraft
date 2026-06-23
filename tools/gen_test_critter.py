#!/usr/bin/env python3
"""Generate the M0 test-critter model + texture, proving the geometry/texture libs
drive the real pack pipeline. A small quadruped: body, head, 4 legs, tail."""
import os
from mclib.geometry import Geometry
from mclib.texture import Tex, hex_rgba, shade

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RP = os.path.join(ROOT, "MotorCraft_RP")
TW, TH = 64, 64


def build_geo():
    g = Geometry("geometry.motor_test_critter", TW, TH)
    root = g.bone("root", (0, 0, 0))
    body = g.bone("body", (0, 8, 0), parent="root")
    body.cube([-4, 6, -6], [8, 6, 12], [0, 20])
    head = g.bone("head", (0, 10, -6), parent="body")
    head.cube([-3, 7, -12], [6, 6, 6], [0, 0])
    head.cube([-1, 8, -14], [2, 2, 2], [24, 0])  # snout
    # legs
    for nm, (x, z), uv in (
        ("leg_fl", (-3, -5), [40, 20]), ("leg_fr", (3, -5), [40, 32]),
        ("leg_bl", (-3, 4), [48, 20]), ("leg_br", (3, 4), [48, 32]),
    ):
        b = g.bone(nm, (x, 6, z), parent="body")
        b.cube([x - 1.5, 0, z - 1.5], [3, 6, 3], uv)
    tail = g.bone("tail", (0, 9, 6), parent="body")
    tail.cube([-1.5, 8, 6], [3, 3, 6], [28, 20])
    g.bounds = [1.6, 1.4, 1.6]
    g.bounds_offset = [0, 0.7, 0]
    os.makedirs(os.path.join(RP, "models", "entity"), exist_ok=True)
    g.save(os.path.join(RP, "models", "entity", "motor_test_critter.geo.json"))


def build_tex():
    t = Tex(TW, TH)
    base = hex_rgba("#9b7653")
    belly = shade(base, 1.3)
    dark = shade(base, 0.8)
    t.box(0, 20, 8, 6, 12, base, top=dark, belly=belly)          # body
    t.box(0, 0, 6, 6, 6, base, top=shade(base, 1.1))             # head
    t.box(24, 0, 2, 2, 2, shade(base, 1.15))                     # snout
    for uv in ([40, 20], [40, 32], [48, 20], [48, 32]):
        t.box(uv[0], uv[1], 3, 6, 3, dark)                       # legs
    t.box(28, 20, 3, 3, 6, base)                                 # tail
    # eyes
    t.rect(2, 2, 1, 1, (20, 20, 20, 255))
    t.rect(8, 2, 1, 1, (20, 20, 20, 255))
    os.makedirs(os.path.join(RP, "textures", "entity"), exist_ok=True)
    t.save(os.path.join(RP, "textures", "entity", "motor_test_critter.png"))


if __name__ == "__main__":
    build_geo()
    build_tex()
    print("test critter model + texture generated")
