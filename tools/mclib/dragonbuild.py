"""Parametric dragon model + texture builder.

build(d) -> Geometry for a dragon param block (see tools/dragons_data.py).
pack_and_paint(geo, palette) -> Tex with auto box-UV packing + region shading.

Bone naming is kept consistent across every archetype (body, head, neck*, wing_l/r,
leg_fl/fr/bl/br, tail*) so a single shared animation file drives all 21 dragons.
"""
from __future__ import annotations
import math
from .geometry import Geometry
from .texture import Tex, shade, hex_rgba

# region -> (shade factor on base color, palette key)
REGION = {
    "body": ("body", 1.0), "belly": ("belly", 1.0), "head": ("body", 1.06),
    "horn": ("horn", 1.0), "spine": ("accent", 1.0), "wingbone": ("horn", 0.9),
    "membrane": ("membrane", 1.0), "leg": ("body", 0.92), "claw": ("horn", 1.05),
    "tail": ("body", 0.98), "tip": ("accent", 1.0), "eye": ("eye", 1.0),
    "teeth": ("horn", 1.15), "extra": ("accent", 1.0),
    "accent": ("accent", 1.0), "spot": ("extra", 1.0), "ear": ("body", 0.95),
    # vehicle regions
    "glass": ("glass", 1.0), "trim": ("trim", 1.0), "dark": ("dark", 1.0),
    "wheel": ("dark", 0.7), "metal": ("trim", 0.9), "light": ("accent", 1.25),
    "seat": ("dark", 1.1),
    # furniture regions (own palette keys to avoid collisions)
    "fwood": ("wood", 1.0), "ftrim": ("trim", 1.0), "faccent": ("accent", 1.0),
    "fmetal": ("metal", 1.0), "ffabric": ("fabric", 1.0), "fdark": ("dark", 1.0),
    "fglass": ("glass", 1.0), "flight": ("light", 1.0), "fleg": ("wood", 0.85),
    "ftop": ("wood", 1.08),
}


def _col(palette, region):
    key, fac = REGION.get(region, ("body", 1.0))
    return shade(hex_rgba(palette[key]), fac)


# --------------------------------------------------------------------------- #
# Geometry
# --------------------------------------------------------------------------- #
def build(d) -> Geometry:
    arch = d["archetype"]
    f = d["features"]
    pal = d["palette"]
    g = Geometry(f"geometry.wf_{d['id']}", 1, 1)  # tex size set after packing
    root = g.bone("root", (0, 0, 0))  # noqa: F841

    if arch == "serpentine":
        _build_serpent(g, d)
    else:
        _build_quad(g, d)

    return g


def _build_quad(g, d):
    arch = d["archetype"]
    f = d["features"]
    heads = f.get("heads", 1)
    legs4 = arch in ("western", "drake", "four_winged", "multi_head")
    if arch == "multi_head" and not f.get("legs4") and "fin" in f.get("wing_style", ""):
        legs4 = True  # tiamat still gets 4 limbs

    bulk = 1.25 if arch == "drake" else (0.9 if d["id"] == "fae" else 1.0)
    bw = int(8 * bulk)            # body width
    bh = int(8 * bulk)            # body height
    bl = 16 if arch != "drake" else 14   # body length
    leg_h = 9 if arch != "drake" else 7
    body_y = leg_h

    body = g.bone("body", (0, body_y + bh / 2, 0), parent="root")
    body.cube([-bw / 2, body_y, -bl / 2], [bw, bh, bl], [0, 0], region="body")
    body.cube([-bw / 2 + 0.5, body_y - 0.4, -bl / 2 + 1], [bw - 1, 2, bl - 2], [0, 0],
              region="belly")  # belly plate

    # ---- necks + heads ----
    neck_n = f.get("neck", 3)
    front_z = -bl / 2
    if heads > 1:
        spread = [-bw * 0.6, 0, bw * 0.6]
        names = ["head", "head2", "head3"]
        for i in range(heads):
            _neck_and_head(g, d, parent="body", base=(spread[i], body_y + bh, front_z),
                            neck_n=neck_n, head_name=names[i],
                            yaw=(-22 if i == 0 else (22 if i == 2 else 0)))
    else:
        _neck_and_head(g, d, parent="body", base=(0, body_y + bh, front_z),
                        neck_n=neck_n, head_name="head", yaw=0)

    # ---- tail ----
    _tail(g, d, parent="body", base=(0, body_y + bh / 2, bl / 2), bw=bw)

    # ---- legs ----
    if arch == "wyvern":
        _leg(g, d, "leg_bl", (-bw / 2 + 1, leg_h, bl / 2 - 3), leg_h, big=True)
        _leg(g, d, "leg_br", (bw / 2 - 1, leg_h, bl / 2 - 3), leg_h, big=True)
    else:
        _leg(g, d, "leg_fl", (-bw / 2 + 1, leg_h, -bl / 2 + 3), leg_h)
        _leg(g, d, "leg_fr", (bw / 2 - 1, leg_h, -bl / 2 + 3), leg_h)
        if legs4:
            _leg(g, d, "leg_bl", (-bw / 2 + 1, leg_h, bl / 2 - 3), leg_h, big=True)
            _leg(g, d, "leg_br", (bw / 2 - 1, leg_h, bl / 2 - 3), leg_h, big=True)

    # ---- wings ----
    style = f.get("wing_style", "membrane")
    shoulder_y = body_y + bh - 1
    if style not in ("none",):
        _wing(g, d, "wing_l", (-bw / 2, shoulder_y, -bl / 4), -1)
        _wing(g, d, "wing_r", (bw / 2, shoulder_y, -bl / 4), 1)
        if style in ("four", "butterfly"):
            _wing(g, d, "wing_l2", (-bw / 2, shoulder_y - 1, bl / 6), -1, second=True)
            _wing(g, d, "wing_r2", (bw / 2, shoulder_y - 1, bl / 6), 1, second=True)

    # ---- dorsal spines ----
    _spines(g, d, top_y=body_y + bh, z0=front_z + 2, z1=bl / 2 - 1, x=0)

    # ---- element extras ----
    _extras(g, d, body_y, bh, bl, bw)

    # visible bounds
    g.tex_w = g.tex_h = 128  # provisional; packer may bump
    g.bounds = [max(8, bl / 2 + 6), max(8, leg_h + bh + 6)]
    g.bounds_offset = [0, (leg_h + bh) / 2, 0]


def _neck_and_head(g, d, parent, base, neck_n, head_name, yaw):
    f = d["features"]
    x0, y0, z0 = base
    seg_len = 3.2
    seg = 6
    prev = parent
    pivot = list(base)
    for i in range(neck_n):
        nm = f"{head_name}_neck{i+1}" if head_name != "head" else f"neck{i+1}"
        # No baked pitch — the stepped pivots form a forward arch; rotations are
        # left to the animations so the dragon never sits locked staring upward.
        b = g.bone(nm, tuple(pivot), parent=prev,
                   rotation=[0, yaw if i == 0 else 0, 0])
        b.cube([pivot[0] - seg / 2, pivot[1] - seg / 2, pivot[2] - seg_len], [seg, seg, seg_len],
               [0, 0], region="body")
        prev = nm
        pivot = [pivot[0] + math.sin(math.radians(yaw)) * 0.5,
                 pivot[1] + 1.4, pivot[2] - seg_len + 0.4]
        seg = max(4, seg - 0.5)
    _head(g, d, parent=prev, pivot=tuple(pivot), name=head_name)


def _head(g, d, parent, pivot, name):
    f = d["features"]
    px, py, pz = pivot
    hb = g.bone(name, (px, py, pz), parent=parent, rotation=[0, 0, 0])
    hb.cube([px - 3, py - 2, pz - 7], [6, 6, 7], [0, 0], region="head")
    # snout
    hb.cube([px - 2, py - 1.5, pz - 11], [4, 3.5, 4], [0, 0], region="head")
    # brow
    hb.cube([px - 3, py + 3.5, pz - 6], [6, 1, 4], [0, 0], region="head")
    # eyes (glow)
    hb.cube([px - 3.2, py + 1.5, pz - 6.5], [0.4, 1.4, 1.6], [0, 0], region="eye")
    hb.cube([px + 2.8, py + 1.5, pz - 6.5], [0.4, 1.4, 1.6], [0, 0], region="eye")
    # jaw (animatable)
    jaw = g.bone(f"{name}_jaw", (px, py - 2, pz - 5), parent=name, rotation=[0, 0, 0])
    jaw.cube([px - 2.5, py - 4, pz - 10], [5, 2, 9], [0, 0], region="head")
    # teeth
    for tx in (-2, 0, 2):
        hb.cube([px + tx, py - 2.2, pz - 10], [0.8, 1.4, 0.8], [0, 0], region="teeth")
    _horns(g, d, name, px, py, pz)


def _horns(g, d, parent, px, py, pz):
    t = d["features"].get("horns", "swept")
    if t == "none":
        return

    def horn(x, length, rot, sz=1.4):
        b = g.bone(f"{parent}_horn_{round(x,1)}", (px + x, py + 4, pz - 2),
                   parent=parent, rotation=rot)
        b.cube([px + x - sz / 2, py + 4, pz - 2 - sz / 2], [sz, length, sz], [0, 0], region="horn")
    if t == "swept":
        horn(-2.4, 7, [-40, -10, -14]); horn(2.4, 7, [-40, 10, 14])
    elif t == "crown":
        for x in (-3, -1, 1, 3):
            horn(x, 5 + abs(x), [-18, 0, x * 4])
    elif t == "single":
        horn(0, 9, [-70, 0, 0], sz=1.8)
    elif t == "antler":
        for x in (-2.6, 2.6):
            horn(x, 6, [-30, 0, x * 5])
            b = g.bone(f"{parent}_ant_{round(x,1)}", (px + x * 1.6, py + 8, pz - 2),
                       parent=parent, rotation=[-20, 0, x * 9])
            b.cube([px + x * 1.6, py + 8, pz - 3], [1, 4, 1], [0, 0], region="horn")
    elif t == "crest":
        for x in (-2, 0, 2):
            horn(x, 4, [-10, 0, 0], sz=1.0)
    elif t == "frill":
        b = g.bone(f"{parent}_frill", (px, py + 2, pz), parent=parent)
        b.cube([px - 6, py - 1, pz - 1], [12, 7, 0], [0, 0], region="membrane")
    elif t == "fin":
        b = g.bone(f"{parent}_fin", (px, py + 3, pz), parent=parent)
        b.cube([px - 0.2, py + 1, pz - 4], [0.4, 6, 7], [0, 0], region="membrane")
    elif t == "ram":
        horn(-2.6, 4, [10, -30, -60], sz=1.8); horn(2.6, 4, [10, 30, 60], sz=1.8)


def _tail(g, d, parent, base, bw):
    f = d["features"]
    n = f.get("long_tail", 4)
    x0, y0, z0 = base
    prev = parent
    pivot = list(base)
    w = bw * 0.55
    for i in range(n):
        nm = f"tail{i+1}"
        b = g.bone(nm, tuple(pivot), parent=prev, rotation=[6, 0, 0])
        b.cube([pivot[0] - w / 2, pivot[1] - w / 2, pivot[2]], [w, w, 4.5], [0, 0], region="tail")
        prev = nm
        pivot = [pivot[0], pivot[1] - 0.4, pivot[2] + 4.0]
        w = max(2, w - 1.0)
    _tail_tip(g, d, prev, pivot)


def _tail_tip(g, d, parent, pivot):
    tip = d["features"].get("tail_tip", "spike")
    px, py, pz = pivot
    b = g.bone("tail_tip", (px, py, pz), parent=parent)
    if tip == "spike":
        b.cube([px - 0.7, py - 0.7, pz], [1.4, 1.4, 5], [0, 0], region="tip")
    elif tip == "club":
        b.cube([px - 2.5, py - 2.5, pz], [5, 5, 5], [0, 0], region="tip")
    elif tip in ("fin", "fluke"):
        b.cube([px - 0.2, py - 4, pz], [0.4, 8, 6], [0, 0], region="membrane")
    elif tip == "spade":
        b.cube([px - 3, py - 0.2, pz], [6, 0.4, 5], [0, 0], region="membrane")
    elif tip == "stinger":
        b.cube([px - 0.6, py - 0.6, pz], [1.2, 1.2, 6], [0, 0], region="tip")


def _leg(g, d, name, pivot, leg_h, big=False):
    px, py, pz = pivot
    w = 3.2 if not big else 3.6
    thigh = g.bone(name, (px, py, pz), parent="body", rotation=[0, 0, 0])
    thigh.cube([px - w / 2, py - leg_h * 0.5, pz - w / 2], [w, leg_h * 0.5 + 1, w], [0, 0], region="leg")
    shin = g.bone(f"{name}_shin", (px, py - leg_h * 0.45, pz), parent=name)
    shin.cube([px - w / 2 + 0.3, py - leg_h, pz - w / 2 + 0.3], [w - 0.6, leg_h * 0.5, w - 0.6],
              [0, 0], region="leg")
    foot = g.bone(f"{name}_foot", (px, py - leg_h, pz), parent=f"{name}_shin")
    foot.cube([px - w / 2, py - leg_h, pz - w / 2 - 2], [w, 2, w + 2], [0, 0], region="leg")
    for cx in (-1, 0, 1):
        foot.cube([px + cx - 0.4, py - leg_h, pz - w / 2 - 3], [0.8, 1, 1.5], [0, 0], region="claw")


def _wing(g, d, name, pivot, side, second=False):
    f = d["features"]
    style = f.get("wing_style", "membrane")
    px, py, pz = pivot
    span = 16 if not second else 12
    s = side
    wing = g.bone(name, (px, py, pz), parent="body",
                  rotation=[0, 0, -18 * s if not second else -10 * s])
    # humerus
    wing.cube([min(px, px + s * 6), py - 1, pz - 1], [6, 2, 2], [0, 0], region="wingbone")
    fore = g.bone(f"{name}_fore", (px + s * 6, py, pz), parent=name, rotation=[0, -20 * s, 0])
    fore.cube([min(px + s * 6, px + s * span), py - 1, pz - 1], [span - 6, 1.6, 1.6], [0, 0],
              region="wingbone")
    tipx = px + s * span
    # finger struts + membrane
    fingers = 4 if style != "skeletal" else 5
    for i in range(fingers):
        fz = pz - 2 + i * (10 / max(1, fingers - 1))
        fb = g.bone(f"{name}_f{i}", (tipx, py, pz), parent=f"{name}_fore",
                    rotation=[0, 0, 0])
        fb.cube([min(tipx, tipx + s * 1), py - 1, fz], [1, 1, 1], [0, 0], region="wingbone")
        # strut backwards
        fb.cube([min(tipx - s * 6, tipx), py - 0.6, fz], [6, 1, 1], [0, 0], region="wingbone")
    if style not in ("skeletal",):
        mcol = "membrane"
        # membrane sheet between forearm tip and body, behind the struts
        x_in = px + s * 5
        mwidth = abs(tipx - x_in)
        mx = min(tipx, x_in)
        if style == "crystalline":
            for i in range(3):
                cb = g.bone(f"{name}_cry{i}", (mx, py, pz + i * 3), parent=f"{name}_fore")
                cb.cube([mx + i * (mwidth / 3), py - 1, pz - 1 + i * 3], [mwidth / 3, 5, 0.4],
                        [0, 0], region=mcol)
        else:
            depth = 11 if style != "butterfly" else 14
            mem = g.bone(f"{name}_mem", (mx, py, pz), parent=f"{name}_fore")
            mem.cube([mx, py - 0.2, pz - 2], [mwidth, 0.4, depth], [0, 0], region=mcol)
            if style == "tattered":
                # notch out the trailing edge with a belly-colored gap cube (visual tear)
                mem.cube([mx + mwidth * 0.4, py - 0.2, pz + depth - 4], [mwidth * 0.5, 0.5, 4],
                         [0, 0], region="belly")


def _spines(g, d, top_y, z0, z1, x):
    sp = d["features"].get("spines", {"n": 10, "style": "spike", "sz": 1.0})
    n = sp.get("n", 10)
    style = sp.get("style", "spike")
    sz = sp.get("sz", 1.0)
    if style == "none" or n <= 0:
        return
    b = g.bone("ridge", (0, top_y, 0), parent="body")
    for i in range(n):
        z = z0 + (z1 - z0) * (i / max(1, n - 1))
        h = sz * (2 + 1.5 * math.sin(math.pi * i / max(1, n - 1)))
        if style == "sail":
            b.cube([x - 0.2, top_y, z], [0.4, h + 2, 2.4], [0, 0], region="membrane")
        elif style == "crystal":
            b.cube([x - 0.6, top_y, z], [1.2, h + 1, 1.2], [0, 0], region="tip")
        else:  # spike
            b.cube([x - 0.5, top_y, z], [1, h, 1], [0, 0], region="spine")


def _extras(g, d, body_y, bh, bl, bw):
    extras = d["features"].get("extras", [])
    if not extras:
        return
    b = g.bone("extras", (0, body_y + bh, 0), parent="body")
    top = body_y + bh
    # element-flavoured decorations along the back/shoulders
    if "vines" in extras or "leaves" in extras:
        for i, z in enumerate(range(int(-bl / 2 + 3), int(bl / 2 - 1), 4)):
            b.cube([(-1) ** i * (bw / 2), top - 2, z], [2, 2, 2], [0, 0], region="extra")
    if "flowers" in extras:
        b.cube([-bw / 2 - 1, top, -bl / 4], [2, 2, 2], [0, 0], region="extra")
        b.cube([bw / 2 - 1, top, bl / 6], [2, 2, 2], [0, 0], region="extra")
    if "ribs" in extras or "bones" in extras:
        for z in range(int(-bl / 2 + 3), int(bl / 2 - 1), 3):
            b.cube([-bw / 2 - 0.4, body_y + 1, z], [bw + 0.8, 1, 0.6], [0, 0], region="claw")
    if "gas_sacs" in extras:
        b.cube([-bw / 2 - 1.5, top - 3, 0], [2, 2, 4], [0, 0], region="extra")
        b.cube([bw / 2 - 0.5, top - 3, 0], [2, 2, 4], [0, 0], region="extra")
    if "coral" in extras or "fins" in extras:
        b.cube([-bw / 2, top - 2, -bl / 6], [0.4, 4, 3], [0, 0], region="membrane")
        b.cube([bw / 2 - 0.4, top - 2, -bl / 6], [0.4, 4, 3], [0, 0], region="membrane")
    if "stone_plates" in extras or "sand_plates" in extras or "magma_cracks" in extras:
        b.cube([-bw / 2 - 0.3, top - 1, -bl / 3], [bw + 0.6, 1.5, bl * 0.5], [0, 0], region="extra")
    if "radiant_crown" in extras:
        for i in range(6):
            ang = i / 6 * math.tau
            b.cube([math.cos(ang) * 4 - 0.5, top + 2, math.sin(ang) * 4 - 0.5 - bl / 3],
                   [1, 3, 1], [0, 0], region="tip")


def _build_serpent(g, d):
    f = d["features"]
    n = f.get("body_segments", 10)
    body_y = 6
    prev = "root"
    pivot = [0, body_y, -n * 2]
    w = 6
    # head first (front)
    _neck_and_head(g, d, parent="root", base=(0, body_y + 2, pivot[2]),
                    neck_n=2, head_name="head", yaw=0)
    # undulating segmented body
    for i in range(n):
        nm = f"seg{i+1}" if i else "body"
        b = g.bone(nm, tuple(pivot), parent=prev, rotation=[0, 8 * math.sin(i), 0])
        b.cube([pivot[0] - w / 2, pivot[1] - w / 2, pivot[2]], [w, w, 4.5], [0, 0],
               region="body")
        b.cube([pivot[0] - w / 2 + 0.5, pivot[1] - w / 2 - 0.3, pivot[2] + 0.5],
               [w - 1, 1.5, 3.5], [0, 0], region="belly")
        prev = nm
        pivot = [pivot[0], pivot[1], pivot[2] + 4.0]
        w = max(2.5, w - 0.3) if i > n / 2 else w
    g.tex_w = g.tex_h = 128
    g.bounds = [10, 10]
    g.bounds_offset = [0, body_y, 0]


# --------------------------------------------------------------------------- #
# Texture: auto box-UV packing + region painting
# --------------------------------------------------------------------------- #
def pack_and_paint(geo: Geometry, palette: dict) -> Tex:
    cubes = list(geo.all_cubes())

    def net(c):
        sx, sy, sz = (abs(c.size[0]), abs(c.size[1]), abs(c.size[2]))
        w = max(1, math.ceil(2 * sz + 2 * sx))
        h = max(1, math.ceil(sz + sy))
        return w, h

    for size in (128, 256, 512):
        placed = _shelf_pack(cubes, size, size, net)
        if placed:
            geo.tex_w = geo.tex_h = size
            t = Tex(size, size)
            for c in cubes:
                col = _col(palette, c.region or "body")
                top = shade(col, 0.85)
                belly = shade(col, 1.18)
                t.box(c.uv[0], c.uv[1], abs(c.size[0]), abs(c.size[1]), abs(c.size[2]),
                      col, top=top, belly=belly)
            return t
    raise RuntimeError("could not pack UVs even at 512x512")


def _shelf_pack(cubes, W, H, net):
    x = y = shelf_h = 0
    for c in cubes:
        w, h = net(c)
        if w > W:
            return False
        if x + w > W:
            x = 0
            y += shelf_h + 1
            shelf_h = 0
        if y + h > H:
            return False
        c.uv = [x, y]
        x += w + 1
        shelf_h = max(shelf_h, h)
    return True
