"""Parametric pet model builder. build(p) -> Geometry for a pet param block.

Consistent bone names (body, head, leg_fl/fr/bl/br, tail, wing_l/r, ear_l/r) so a
single shared pet animation drives every species. Reuses the dragon texture packer.
"""
from __future__ import annotations
import math
from .geometry import Geometry


def build(p):
    plan = p["plan"]
    g = Geometry(f"geometry.wf_{p['id']}", 1, 1)
    g.bone("root", (0, 0, 0))
    {"quad": _quad, "bird": _bird, "reptile": _reptile, "turtle": _turtle,
     "blob": _blob, "sprite": _sprite}[plan](g, p)
    g.autobounds(pad=3)
    return g


def _eyes(b, hx, hy, hz, w):
    b.cube([-hx - 0.05, hy, hz - 0.6], [0.4, 0.8, 0.8], [0, 0], region="eye")
    b.cube([hx - 0.35, hy, hz - 0.6], [0.4, 0.8, 0.8], [0, 0], region="eye")


def _ears(g, p, hx, hy, hz):
    t = p["features"].get("ears")
    if not t:
        return
    el = g.bone("ear_l", (-hx + 0.5, hy, hz), parent="head")
    er = g.bone("ear_r", (hx - 0.5, hy, hz), parent="head")
    if t == "pointy":
        el.cube([-hx, hy, hz - 0.5], [1, 2, 1], [0, 0], region="ear")
        er.cube([hx - 1, hy, hz - 0.5], [1, 2, 1], [0, 0], region="ear")
    elif t == "tall":
        el.cube([-hx, hy, hz], [1, 4, 0.8], [0, 0], region="ear")
        er.cube([hx - 1, hy, hz], [1, 4, 0.8], [0, 0], region="ear")
    elif t == "floppy":
        el.cube([-hx - 0.5, hy - 2.5, hz], [1.2, 3, 0.6], [0, 0], region="ear")
        er.cube([hx - 0.7, hy - 2.5, hz], [1.2, 3, 0.6], [0, 0], region="ear")
    else:  # round
        el.cube([-hx, hy, hz], [1.4, 1.4, 0.8], [0, 0], region="ear")
        er.cube([hx - 1.4, hy, hz], [1.4, 1.4, 0.8], [0, 0], region="ear")


def _tail(g, p, bx, by, bz):
    t = p["features"].get("tail", "stub")
    if t == "none":
        return
    tb = g.bone("tail", (0, by, bz), parent="body", rotation=[-35, 0, 0])
    if t in ("bushy", "fluffy", "puff", "hair"):
        tb.cube([-1.2, by - 1, bz], [2.4, 2.4, 4], [0, 0], region="body")
    elif t == "long":
        tb.cube([-0.6, by - 0.6, bz], [1.2, 1.2, 5], [0, 0], region="body")
    elif t == "crystal":
        tb.cube([-0.8, by - 0.8, bz], [1.6, 1.6, 3], [0, 0], region="accent")
        tb.cube([-0.5, by - 0.5, bz + 3], [1, 2, 2], [0, 0], region="spot")
    else:  # stub
        tb.cube([-0.8, by - 0.8, bz], [1.6, 1.6, 1.6], [0, 0], region="body")


def _quad(g, p, lh=5, bl=9, bw=5, bh=5):
    f = p["features"]
    if p["id"] == "rabbit":
        lh, bl, bh = 4, 6, 5
    by = lh
    body = g.bone("body", (0, by + bh / 2, 0), parent="root")
    body.cube([-bw / 2, by, -bl / 2], [bw, bh, bl], [0, 0], region="body")
    body.cube([-bw / 2 + 0.5, by - 0.3, -bl / 2 + 1], [bw - 1, 1.5, bl - 2], [0, 0], region="belly")
    if f.get("mane"):
        body.cube([-bw / 2 - 0.2, by + bh - 1, -bl / 2 - 0.5], [bw + 0.4, 3, 3], [0, 0], region="spot")
    if f.get("cap"):
        body.cube([-bw / 2 - 0.6, by + bh, -1.5], [bw + 1.2, 1.5, 4], [0, 0], region="spot")
    if f.get("crystals"):
        for z in (-2, 1):
            body.cube([-0.5, by + bh, z], [1, 2, 1], [0, 0], region="spot")
    # head
    hz = -bl / 2
    head = g.bone("head", (0, by + bh, hz), parent="body")
    hs = 4 if p["id"] != "rabbit" else 3
    head.cube([-hs / 2, by + bh - 1, hz - hs], [hs, hs, hs], [0, 0], region="head")
    head.cube([-1.2, by + bh - 1.5, hz - hs - 1.5], [2.4, 2, 2], [0, 0], region="head")  # snout
    _eyes(head, hs / 2 - 0.5, by + bh + 0.5, hz - hs + 0.4, hs)
    _ears(g, p, hs / 2, by + bh, hz - hs + 1)
    # legs
    w = 1.6 if p["size"] != "large" else 2.0
    for nm, (x, z) in (("leg_fl", (-bw / 2 + 1, -bl / 2 + 2)), ("leg_fr", (bw / 2 - 1, -bl / 2 + 2)),
                       ("leg_bl", (-bw / 2 + 1, bl / 2 - 2)), ("leg_br", (bw / 2 - 1, bl / 2 - 2))):
        b = g.bone(nm, (x, lh, z), parent="body")
        b.cube([x - w / 2, 0, z - w / 2], [w, lh, w], [0, 0], region="leg")
    _tail(g, p, 0, by + bh / 2, bl / 2)
    g.tex_w = g.tex_h = 64
    g.bounds = [max(4, bl / 2 + 3), lh + bh + 3]
    g.bounds_offset = [0, (lh + bh) / 2, 0]


def _bird(g, p):
    by, bl, bw, bh = 5, 5, 3.5, 4
    body = g.bone("body", (0, by + bh / 2, 0), parent="root", rotation=[20, 0, 0])
    body.cube([-bw / 2, by, -bl / 2], [bw, bh, bl], [0, 0], region="body")
    body.cube([-bw / 2 + 0.4, by + 0.4, -bl / 2 + 0.4], [bw - 0.8, bh - 1, 1], [0, 0], region="belly")
    head = g.bone("head", (0, by + bh, -bl / 2), parent="body")
    head.cube([-1.5, by + bh - 0.5, -bl / 2 - 2.5], [3, 3, 3], [0, 0], region="head")
    head.cube([-0.6, by + bh, -bl / 2 - 4], [1.2, 1, 1.5], [0, 0], region="accent")  # beak
    _eyes(head, 1.0, by + bh + 1, -bl / 2 - 1.6, 3)
    if p["features"].get("crest"):
        head.cube([-0.4, by + bh + 2.5, -bl / 2 - 1], [0.8, 2, 1.5], [0, 0], region="accent")
    for nm, s in (("wing_l", -1), ("wing_r", 1)):
        w = g.bone(nm, (s * bw / 2, by + bh - 1, 0), parent="body", rotation=[0, 0, -s * 8])
        w.cube([min(s * bw / 2, s * (bw / 2 + 5)), by + 1, -bl / 2], [5, 0.6, bl], [0, 0],
               region="accent")
    for nm, x in (("leg_bl", -1), ("leg_br", 1)):
        b = g.bone(nm, (x, by, 1), parent="body")
        b.cube([x - 0.4, 0, 0.6], [0.8, by, 0.8], [0, 0], region="accent")
    t = g.bone("tail", (0, by + 1, bl / 2), parent="body")
    t.cube([-1.5, by, bl / 2], [3, 0.6, 4], [0, 0], region="accent")
    g.tex_w = g.tex_h = 64
    g.bounds = [6, 10]
    g.bounds_offset = [0, 5, 0]


def _reptile(g, p):
    big = p["features"].get("big_legs")
    lh = 3 if not big else 4
    bl, bw, bh = (10, 4, 3) if not big else (13, 6, 5)
    by = lh
    body = g.bone("body", (0, by + bh / 2, 0), parent="root")
    body.cube([-bw / 2, by, -bl / 2], [bw, bh, bl], [0, 0], region="body")
    body.cube([-bw / 2 + 0.4, by - 0.2, -bl / 2 + 1], [bw - 0.8, 1, bl - 2], [0, 0], region="belly")
    if p["features"].get("crest"):
        ridge = g.bone("ridge", (0, by + bh, 0), parent="body")
        n = 8
        for i in range(n):
            z = -bl / 2 + 1 + (bl - 2) * i / (n - 1)
            ridge.cube([-0.4, by + bh, z], [0.8, 1.2, 0.8], [0, 0], region="accent")
    head = g.bone("head", (0, by + bh / 2, -bl / 2), parent="body")
    head.cube([-bw / 2 + 0.5, by, -bl / 2 - 3.5], [bw - 1, bh - 0.5, 3.5], [0, 0], region="head")
    _eyes(head, bw / 2 - 1, by + bh - 1, -bl / 2 - 2, bw)
    # splayed legs
    w = 1.4 if not big else 2.2
    for nm, (x, z, sx) in (("leg_fl", (-bw / 2, -bl / 2 + 2, -1)), ("leg_fr", (bw / 2, -bl / 2 + 2, 1)),
                           ("leg_bl", (-bw / 2, bl / 2 - 2, -1)), ("leg_br", (bw / 2, bl / 2 - 2, 1))):
        b = g.bone(nm, (x, by, z), parent="body", rotation=[0, 0, sx * 30])
        b.cube([x - w / 2 + (sx * 0.5), 0, z - w / 2], [w, lh + 1, w], [0, 0], region="leg")
    tb = g.bone("tail", (0, by + bh / 2, bl / 2), parent="body")
    seg = bw
    for i in range(4):
        tb.cube([-seg / 2, by, bl / 2 + i * 3], [seg, max(1, seg - 1), 3.2], [0, 0], region="tail")
        seg = max(1.2, seg - 1.0)
    g.tex_w = g.tex_h = 64 if not big else 128
    g.bounds = [bl / 2 + 3, lh + bh + 3]
    g.bounds_offset = [0, (lh + bh) / 2, 0]


def _turtle(g, p):
    lh, bl, bw = 3, 8, 7
    by = lh
    body = g.bone("body", (0, by, 0), parent="root")
    body.cube([-bw / 2 + 1, by - 1, -bl / 2 + 1], [bw - 2, 2, bl - 2], [0, 0], region="belly")
    # shell dome
    shell = g.bone("shell", (0, by, 0), parent="body")
    shell.cube([-bw / 2, by + 0.5, -bl / 2], [bw, 3, bl], [0, 0], region="body")
    shell.cube([-bw / 2 + 1.5, by + 3, -bl / 2 + 1.5], [bw - 3, 2, bl - 3], [0, 0], region="accent")
    head = g.bone("head", (0, by, -bl / 2), parent="body")
    head.cube([-1.5, by, -bl / 2 - 3], [3, 3, 3], [0, 0], region="head")
    _eyes(head, 1.0, by + 1.5, -bl / 2 - 1.6, 3)
    for nm, (x, z) in (("leg_fl", (-bw / 2 + 1, -bl / 2 + 2)), ("leg_fr", (bw / 2 - 1, -bl / 2 + 2)),
                       ("leg_bl", (-bw / 2 + 1, bl / 2 - 2)), ("leg_br", (bw / 2 - 1, bl / 2 - 2))):
        b = g.bone(nm, (x, by, z), parent="body")
        b.cube([x - 1, 0, z - 1], [2, lh, 2], [0, 0], region="leg")
    g.tex_w = g.tex_h = 64
    g.bounds = [bl / 2 + 2, lh + 6]
    g.bounds_offset = [0, 3, 0]


def _blob(g, p):
    s = 6
    body = g.bone("body", (0, s / 2, 0), parent="root")
    body.cube([-s / 2, 0, -s / 2], [s, s, s], [0, 0], region="body")
    body.cube([-s / 2 + 1, 0.5, -s / 2 + 1], [s - 2, s - 2, s - 2], [0, 0], region="belly")
    # inner core / face on the front
    head = g.bone("head", (0, s / 2, -s / 2), parent="body")
    head.cube([-1.5, s / 2 - 0.5, -s / 2 - 0.05], [1, 1, 0.4], [0, 0], region="eye")
    head.cube([0.5, s / 2 - 0.5, -s / 2 - 0.05], [1, 1, 0.4], [0, 0], region="eye")
    g.tex_w = g.tex_h = 64
    g.bounds = [s, s + 2]
    g.bounds_offset = [0, s / 2, 0]


def _sprite(g, p):
    s = 4
    by = 4
    body = g.bone("body", (0, by + s / 2, 0), parent="root")
    body.cube([-s / 2, by, -s / 2], [s, s, s], [0, 0], region="body")
    head = g.bone("head", (0, by + s / 2, -s / 2), parent="body")
    head.cube([-1.2, by + s / 2, -s / 2 - 0.05], [0.8, 0.8, 0.4], [0, 0], region="eye")
    head.cube([0.4, by + s / 2, -s / 2 - 0.05], [0.8, 0.8, 0.4], [0, 0], region="eye")
    # flame / aura crown
    for i in range(6):
        ang = i / 6 * math.tau
        body.cube([math.cos(ang) * 2.4 - 0.4, by + s - 0.5, math.sin(ang) * 2.4 - 0.4],
                  [0.8, 2, 0.8], [0, 0], region="accent")
    # tiny wings
    for nm, sx in (("wing_l", -1), ("wing_r", 1)):
        w = g.bone(nm, (sx * s / 2, by + s / 2, 0), parent="body")
        w.cube([min(sx * s / 2, sx * (s / 2 + 3)), by + 1, -1], [3, 0.4, 3], [0, 0], region="spot")
    g.tex_w = g.tex_h = 64
    g.bounds = [6, 10]
    g.bounds_offset = [0, by + s / 2, 0]
