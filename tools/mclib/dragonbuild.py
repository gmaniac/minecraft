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

    g.autobounds(pad=4)        # enclose wings/tail so the dragon never frustum-culls
    return g


def _build_quad(g, d):
    arch = d["archetype"]
    f = d["features"]
    heads = f.get("heads", 1)
    legs4 = arch in ("western", "drake", "four_winged", "multi_head")
    if arch == "multi_head" and not f.get("legs4") and "fin" in f.get("wing_style", ""):
        legs4 = True  # tiamat still gets 4 limbs

    bulk = 1.35 if arch == "drake" else (0.85 if d["id"] == "fae" else 1.0)
    bw = round(10 * bulk)         # body width
    bh = round(9 * bulk)          # body height
    bl = 22 if arch != "drake" else 18   # body length
    leg_h = 11 if arch != "drake" else 8
    body_y = leg_h

    body = g.bone("body", (0, body_y + bh / 2, 0), parent="root")
    # tapered torso: broad chest/shoulders -> core -> raised haunches
    body.cube([-bw / 2, body_y, -bl / 2], [bw, bh, bl], [0, 0], region="body")          # core
    body.cube([-(bw + 2) / 2, body_y - 0.5, -bl / 2 - 0.5], [bw + 2, bh + 2, bl * 0.34],
              [0, 0], region="body")                                                    # chest/shoulders
    body.cube([-(bw + 1.4) / 2, body_y + 1.5, -bl / 5], [bw + 1.4, bh * 0.55, bl * 0.5],
              [0, 0], region="body")                                                    # upper flank/back muscle
    body.cube([-(bw + 1) / 2, body_y + 1, bl / 2 - bl * 0.3], [bw + 1, bh - 1, bl * 0.3],
              [0, 0], region="body")                                                    # haunches (raised)
    # stacked belly scutes (the armored underside look)
    z = -bl / 2 + 2
    while z < bl / 2 - 2:
        body.cube([-(bw - 1) / 2, body_y - 0.8, z], [bw - 1, 1.6, 2.0], [0, 0], region="belly")
        z += 2.6
    # overlapping back plates along the spine (armor)
    z = -bl / 2 + 3
    while z < bl / 2 - 2:
        body.cube([-1.6, body_y + bh - 0.3, z], [3.2, 1.2, 2.2], [0, 0], region="spine")
        z += 2.4

    # ---- necks + heads ----
    front_z = -bl / 2
    nlen, nrise, nbw = bl * 0.7, bh * 0.9, bw * 0.7
    if heads > 1:
        spread = [-bw * 0.55, 0, bw * 0.55]
        names = ["head", "head2", "head3"]
        for i in range(heads):
            _neck_curved(g, d, "body", (spread[i], body_y + bh - 1, front_z + 1), names[i],
                          yaw=(-20 if i == 0 else (20 if i == 2 else 0)),
                          length=nlen, rise=nrise, base_w=nbw, head_w=5)
    else:
        _neck_curved(g, d, "body", (0, body_y + bh - 1, front_z + 1), "head",
                      yaw=0, length=nlen, rise=nrise, base_w=nbw, head_w=5)

    # ---- tail ----
    _tail_curved(g, d, "body", (0, body_y + bh / 2, bl / 2), base_w=bw * 0.55,
                 length=bl * 0.95)

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


def _neck_curved(g, d, parent, base, head_name, yaw, length, rise, base_w, head_w):
    # a smooth curved neck built from many small tapered boxes positioned along an
    # arc (positions only -> reads identically in-game and in preview, no pitch lock)
    bx, by, bz = base
    nb = (head_name + "_neck") if head_name != "head" else "neck"
    neck = g.bone(nb, (bx, by, bz), parent=parent)
    yawr = math.radians(yaw)
    segs = 10
    last = (bx, by, bz)
    for i in range(segs):
        t = (i + 0.5) / segs
        z = bz - t * length
        y = by + math.sin(min(1.0, t * 1.15) * math.pi * 0.5) * rise
        x = bx + math.sin(yawr) * t * length * 0.35
        w = base_w + (head_w - base_w) * t
        neck.cube([x - w / 2, y - w / 2, z - 2.4], [w, w, 2.8], [0, 0], region="body")
        # underside throat scutes
        if i % 2 == 0:
            neck.cube([x - (w - 1) / 2, y - w / 2 - 0.3, z - 2.2], [w - 1, 1.0, 2.2], [0, 0],
                      region="belly")
        last = (x, y, z)
    _head(g, d, parent=nb, pivot=(last[0], last[1] + 1, last[2] - 1), name=head_name)


def _head(g, d, parent, pivot, name):
    f = d["features"]
    px, py, pz = pivot
    hb = g.bone(name, (px, py, pz), parent=parent, rotation=[0, 0, 0])
    hb.cube([px - 3, py - 2, pz - 7], [6, 6, 7], [0, 0], region="head")          # skull
    hb.cube([px - 3.3, py - 1, pz - 5], [6.6, 4, 4], [0, 0], region="head")      # cheeks (wider)
    # tapered snout (two segments)
    hb.cube([px - 2.5, py - 1.5, pz - 11], [5, 4, 4], [0, 0], region="head")
    hb.cube([px - 2, py - 1.2, pz - 13.5], [4, 3, 3], [0, 0], region="head")
    hb.cube([px - 0.9, py + 1.2, pz - 13.6], [0.9, 0.8, 1], [0, 0], region="head")  # nostril ridge L
    hb.cube([px, py + 1.2, pz - 13.6], [0.9, 0.8, 1], [0, 0], region="head")        # nostril ridge R
    # angled brow ridges over each eye
    br = g.bone(f"{name}_browL", (px - 2, py + 3.5, pz - 5), parent=name, rotation=[0, 0, 18])
    br.cube([px - 3.4, py + 3, pz - 6.5], [3, 1.4, 4.5], [0, 0], region="head")
    br2 = g.bone(f"{name}_browR", (px + 2, py + 3.5, pz - 5), parent=name, rotation=[0, 0, -18])
    br2.cube([px + 0.4, py + 3, pz - 6.5], [3, 1.4, 4.5], [0, 0], region="head")
    # eyes (glow), set into sockets
    hb.cube([px - 3.3, py + 1.4, pz - 6.6], [0.5, 1.6, 1.8], [0, 0], region="eye")
    hb.cube([px + 2.8, py + 1.4, pz - 6.6], [0.5, 1.6, 1.8], [0, 0], region="eye")
    # lower jaw (animatable) + chin
    jaw = g.bone(f"{name}_jaw", (px, py - 2, pz - 5), parent=name, rotation=[0, 0, 0])
    jaw.cube([px - 2.5, py - 4, pz - 12], [5, 2.2, 11], [0, 0], region="head")
    jaw.cube([px - 1.5, py - 4, pz - 5], [3, 2, 3], [0, 0], region="head")       # jaw hinge
    # upper + lower teeth
    for tx in (-2.2, -0.8, 0.8, 2.2):
        hb.cube([px + tx, py - 2.4, pz - 12], [0.7, 1.5, 0.7], [0, 0], region="teeth")
        jaw.cube([px + tx, py - 2.2, pz - 11.5], [0.7, 1.4, 0.7], [0, 0], region="teeth")
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


def _tail_curved(g, d, parent, base, base_w, length):
    # long tapered tail as many small boxes along a gentle droop-then-lift arc,
    # split across two animatable bones (tail1/tail2) so it can sway
    bx, by, bz = base
    t1 = g.bone("tail1", (bx, by, bz), parent=parent)
    t2 = g.bone("tail2", (bx, by, bz), parent="tail1")
    segs = 12
    last = (bx, by, bz)
    for i in range(segs):
        t = (i + 0.5) / segs
        z = bz + t * length
        y = by - math.sin(t * math.pi * 0.5) * (by * 0.4) + max(0.0, t - 0.82) * 7
        w = max(1.4, base_w * (1 - t * 0.82))
        bone = t1 if t < 0.5 else t2
        bone.cube([bx - w / 2, y - w / 2, z - 2.2], [w, w, 2.6], [0, 0], region="tail")
        last = (bx, y, z)
    _tail_tip(g, d, "tail2", last)


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
    # haunch/thigh muscle (wider at top), tapering to the knee
    thigh.cube([px - (w + 1.4) / 2, py - leg_h * 0.5, pz - (w + 1.4) / 2],
               [w + 1.4, leg_h * 0.5 + 1, w + 1.4], [0, 0], region="leg")
    shin = g.bone(f"{name}_shin", (px, py - leg_h * 0.45, pz), parent=name)
    shin.cube([px - w / 2 + 0.3, py - leg_h, pz - w / 2 + 0.3], [w - 0.6, leg_h * 0.5, w - 0.6],
              [0, 0], region="leg")
    shin.cube([px - w / 2, py - leg_h * 0.5, pz - w / 2], [w, 1.6, w], [0, 0], region="leg")  # knee
    foot = g.bone(f"{name}_foot", (px, py - leg_h, pz), parent=f"{name}_shin")
    foot.cube([px - w / 2, py - leg_h, pz - w / 2 - 1], [w, 1.8, w], [0, 0], region="leg")     # ankle
    # three splayed toes, each tipped with a claw
    for cx in (-1.4, 0, 1.4):
        foot.cube([px + cx - 0.7, py - leg_h, pz - w / 2 - 3.5], [1.4, 1.6, 4], [0, 0], region="leg")
        foot.cube([px + cx - 0.45, py - leg_h, pz - w / 2 - 4.8], [0.9, 1, 1.6], [0, 0], region="claw")


def _wing(g, d, name, pivot, side, second=False):
    style = d["features"].get("wing_style", "membrane")
    px, py, pz = pivot
    s = side
    span = 24 if not second else 17
    raise_deg = (-42 if not second else -28) * s
    wing = g.bone(name, (px, py, pz), parent="body", rotation=[0, 0, raise_deg])
    shoulder, elbow, tip = px, px + s * 9, px + s * span

    def xc(bone, xa, xb, y, dy, z, dz, region):
        bone.cube([min(xa, xb), y, z], [max(0.4, abs(xb - xa)), dy, dz], [0, 0], region=region)

    # humerus + forearm (the wing "arm")
    xc(wing, shoulder, elbow, py - 1.4, 3, pz - 1.6, 3.2, "wingbone")
    fore = g.bone(f"{name}_fore", (elbow, py, pz), parent=name, rotation=[0, -24 * s, 0])
    xc(fore, elbow, tip, py - 1, 2.2, pz - 1.3, 2.6, "wingbone")

    if style == "skeletal":                          # bones only, no web
        for i in range(5):
            fb = g.bone(f"{name}_f{i}", (tip, py, pz), parent=f"{name}_fore")
            xc(fb, tip, tip - s * (10 - i), py - 0.5, 1, pz - 3 + i * 4.5, 1, "wingbone")
        return

    back = 20 if style == "butterfly" else 15        # max trailing-edge depth (at the tip)
    mem = g.bone(f"{name}_mem", (px, py, pz), parent=f"{name}_fore")
    # membrane built as strips that DEEPEN toward the wingtip -> a real wing silhouette
    strips = 6
    x_in = shoulder + s * 3
    for i in range(strips):
        xa = x_in + (tip - x_in) * (i / strips)
        xb = x_in + (tip - x_in) * ((i + 1) / strips)
        depth = back * (0.35 + 0.65 * ((i + 1) / strips))
        xc(mem, xa, xb, py - 0.2, 0.5, pz - 2, depth, "membrane")
        if style == "crystalline":                   # crystal ribs along each strip
            xc(mem, xb, xb + s * 0.6, py - 0.4, 4.5, pz - 1, depth, "membrane")
    if style == "tattered":                          # torn notches in the trailing edge
        for i in (1, 3):
            xc(mem, x_in + (tip - x_in) * (i / strips), x_in + (tip - x_in) * ((i + 0.6) / strips),
               py - 0.25, 0.6, pz - 2 + back * 0.7, back * 0.5, "belly")
    # finger struts fanning from the wrist to the scalloped trailing edge
    for i in range(5):
        a = i / 4.0
        flen = (span - 9) * (0.5 + 0.12 * i)
        fb = g.bone(f"{name}_f{i}", (tip, py, pz), parent=f"{name}_fore")
        xc(fb, tip, tip - s * flen, py + 0.1, 0.9, pz - 2 + back * a, 0.9, "wingbone")


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
    _neck_curved(g, d, parent="root", base=(0, body_y + 2, pivot[2]), head_name="head",
                 yaw=0, length=10, rise=3, base_w=6, head_w=5)
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
def pack_and_paint(geo: Geometry, palette: dict, style: str = "plain") -> Tex:
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
                t.box_detailed(c.uv[0], c.uv[1], abs(c.size[0]), abs(c.size[1]), abs(c.size[2]),
                               col, c.region or "body", style)
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
