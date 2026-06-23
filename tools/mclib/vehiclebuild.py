"""Parametric vehicle model builder. build(v) -> Geometry.

Moving parts use consistent bone names (wheel_fl/fr/bl/br, wheel_f/b, prop, rotor,
rotor_t) so the shared vehicle animation spins them. Reuses the dragon texture packer.
"""
from __future__ import annotations
from .geometry import Geometry


def build(v):
    g = Geometry(f"geometry.wf_{v['id']}", 1, 1)
    g.bone("root", (0, 0, 0))
    {"car": _car, "bus": _bus, "bike": _bike, "plane": _plane, "jet": _jet, "heli": _heli,
     "glider": _glider, "balloon": _balloon, "boat": _boat, "jetski": _jetski, "sub": _sub,
     "pontoon": _pontoon}[v["plan"]](g, v)
    g.tex_w = g.tex_h = 128
    return g


def _wheel(g, name, x, z, r=2.5, wide=1.6, y=0):
    b = g.bone(name, (x, r, z), parent="body")
    b.cube([x - wide / 2, 0, z - r], [wide, r * 2, r * 2], [0, 0], region="wheel")
    b.cube([x - wide / 2 - 0.2, r - 0.8, z - 0.8], [wide + 0.4, 1.6, 1.6], [0, 0], region="metal")
    return b


def _seatmark(g, x, y, z):
    b = g.bone(f"seat_{round(x,1)}_{round(z,1)}", (x, y, z), parent="body")
    b.cube([x - 1.5, y, z - 1.5], [3, 1, 3], [0, 0], region="seat")


def _car(g, v):
    big = v["plan"] == "car" and v["scale"] >= 1.3
    bl, bw = 18, 8
    ride = 4 if v["id"] != "monster_truck" else 7
    body = g.bone("body", (0, ride, 0), parent="root")
    body.cube([-bw / 2, ride, -bl / 2], [bw, 4, bl], [0, 0], region="body")  # chassis
    # cabin / windscreen
    body.cube([-bw / 2 + 0.5, ride + 4, -bl / 6], [bw - 1, 4, bl / 2], [0, 0], region="glass")
    body.cube([-bw / 2 + 0.4, ride + 3.5, -bl / 6 + 0.4], [bw - 0.8, 1, bl / 2 - 0.8], [0, 0],
              region="body")
    # headlights / taillights
    body.cube([-bw / 2 + 0.5, ride + 1, -bl / 2 - 0.3], [1.5, 1.5, 0.4], [0, 0], region="light")
    body.cube([bw / 2 - 2, ride + 1, -bl / 2 - 0.3], [1.5, 1.5, 0.4], [0, 0], region="light")
    body.cube([-bw / 2 + 0.5, ride + 1, bl / 2 - 0.1], [1.5, 1.5, 0.4], [0, 0], region="accent")
    r = 3.4 if v["id"] == "monster_truck" else 2.4
    _wheel(g, "wheel_fl", -bw / 2, -bl / 2 + 4, r); _wheel(g, "wheel_fr", bw / 2, -bl / 2 + 4, r)
    _wheel(g, "wheel_bl", -bw / 2, bl / 2 - 4, r); _wheel(g, "wheel_br", bw / 2, bl / 2 - 4, r)
    for s in range(v["seats"]):
        _seatmark(g, 0, ride + 4, -bl / 6 + s * 3)
    g.bounds = [bl / 2 + 3, ride + 9]
    g.bounds_offset = [0, ride + 3, 0]


def _bus(g, v):
    bl, bw = 26, 9
    ride = 4
    body = g.bone("body", (0, ride, 0), parent="root")
    body.cube([-bw / 2, ride, -bl / 2], [bw, 9, bl], [0, 0], region="body")
    for z in range(int(-bl / 2 + 2), int(bl / 2 - 1), 4):  # windows
        body.cube([-bw / 2 - 0.2, ride + 5, z], [bw + 0.4, 3, 2.5], [0, 0], region="glass")
    body.cube([-bw / 2 + 0.5, ride + 1, -bl / 2 - 0.3], [2, 2, 0.4], [0, 0], region="light")
    body.cube([bw / 2 - 2.5, ride + 1, -bl / 2 - 0.3], [2, 2, 0.4], [0, 0], region="light")
    for z in (-bl / 2 + 5, bl / 2 - 5):
        _wheel(g, f"wheel_l{round(z)}", -bw / 2, z); _wheel(g, f"wheel_r{round(z)}", bw / 2, z)
    for s in range(v["seats"]):
        _seatmark(g, 0, ride + 9, -bl / 4 + s * 4)
    g.bounds = [bl / 2 + 3, ride + 12]
    g.bounds_offset = [0, ride + 5, 0]


def _bike(g, v):
    quad = v["id"] == "atv"
    bl, bw = 12, (6 if quad else 2.4)
    ride = 3
    body = g.bone("body", (0, ride, 0), parent="root")
    body.cube([-bw / 2, ride, -bl / 2], [bw, 3, bl], [0, 0], region="body")
    body.cube([-1, ride + 3, 1], [2, 2, 4], [0, 0], region="seat")            # seat
    body.cube([-2.5, ride + 4, -bl / 2 + 1], [5, 1, 1], [0, 0], region="metal")  # handlebars
    body.cube([-1, ride + 2, -bl / 2 - 0.3], [2, 2, 0.4], [0, 0], region="light")
    if quad:
        _wheel(g, "wheel_fl", -bw / 2, -bl / 2 + 3, 2.4, 2.2)
        _wheel(g, "wheel_fr", bw / 2, -bl / 2 + 3, 2.4, 2.2)
        _wheel(g, "wheel_bl", -bw / 2, bl / 2 - 3, 2.4, 2.2)
        _wheel(g, "wheel_br", bw / 2, bl / 2 - 3, 2.4, 2.2)
    else:
        _wheel(g, "wheel_f", 0, -bl / 2 + 2, 3, 1.2)
        _wheel(g, "wheel_b", 0, bl / 2 - 2, 3, 1.2)
    _seatmark(g, 0, ride + 3, 1)
    g.bounds = [bl / 2 + 3, ride + 7]
    g.bounds_offset = [0, ride + 2, 0]


def _plane(g, v):
    bl, bw = 22, 5
    y = 6
    body = g.bone("body", (0, y, 0), parent="root")
    body.cube([-bw / 2, y, -bl / 2], [bw, 5, bl], [0, 0], region="body")          # fuselage
    body.cube([-bw / 2 + 0.5, y + 4, -4], [bw - 1, 3, 7], [0, 0], region="glass")  # cockpit
    body.cube([-18, y + 1, -1], [36, 1.2, 7], [0, 0], region="body")               # main wing
    body.cube([-7, y + 4, bl / 2 - 3], [14, 1, 5], [0, 0], region="trim")          # h-stab
    body.cube([-0.5, y + 4, bl / 2 - 3], [1, 5, 5], [0, 0], region="trim")         # v-stab
    prop = g.bone("prop", (0, y + 2.5, -bl / 2), parent="body")
    prop.cube([-0.6, y - 4, -bl / 2 - 1], [1.2, 13, 1], [0, 0], region="dark")     # blades
    prop.cube([-4, y + 2, -bl / 2 - 1], [9, 1.2, 1], [0, 0], region="dark")
    _wheel(g, "wheel_f", 0, -bl / 2 + 4, 1.6, 1.0); _wheel(g, "wheel_bl", -3, bl / 2 - 6, 1.6, 1.0)
    _wheel(g, "wheel_br", 3, bl / 2 - 6, 1.6, 1.0)
    for s in range(v["seats"]):
        _seatmark(g, 0, y + 4, -3 + s * 3)
    g.bounds = [20, y + 8]
    g.bounds_offset = [0, y + 2, 0]


def _jet(g, v):
    bl, bw = 26, 4
    y = 6
    body = g.bone("body", (0, y, 0), parent="root")
    body.cube([-bw / 2, y, -bl / 2], [bw, 4, bl], [0, 0], region="body")
    body.cube([-1.2, y + 1, -bl / 2 - 3], [2.4, 2, 3], [0, 0], region="trim")     # nose
    body.cube([-bw / 2 + 0.4, y + 3.5, -6], [bw - 0.8, 2.5, 6], [0, 0], region="glass")
    body.cube([-14, y + 0.5, 3], [28, 1, 7], [0, 0], region="body")               # swept wing
    body.cube([-0.5, y + 4, bl / 2 - 4], [1, 5, 5], [0, 0], region="trim")        # tail fin
    body.cube([-bw / 2, y + 0.5, bl / 2 - 0.3], [bw, 3, 0.6], [0, 0], region="light")  # exhaust
    _seatmark(g, 0, y + 4, -3)
    g.bounds = [16, y + 9]
    g.bounds_offset = [0, y + 2, 0]


def _heli(g, v):
    bl, bw = 14, 6
    y = 5
    body = g.bone("body", (0, y, 0), parent="root")
    body.cube([-bw / 2, y, -bl / 2], [bw, 6, bl], [0, 0], region="body")
    body.cube([-bw / 2 + 0.4, y + 1, -bl / 2 - 0.3], [bw - 0.8, 4, 2], [0, 0], region="glass")
    body.cube([-1.5, y + 1, bl / 2], [3, 3, 12], [0, 0], region="trim")           # tail boom
    rotor = g.bone("rotor", (0, y + 7, 0), parent="body")
    rotor.cube([-18, y + 7, -0.6], [36, 0.6, 1.2], [0, 0], region="dark")
    rotor.cube([-0.6, y + 7, -18], [1.2, 0.6, 36], [0, 0], region="dark")
    rt = g.bone("rotor_t", (0, y + 3, bl / 2 + 11), parent="body")
    rt.cube([1.5, y + 1, bl / 2 + 10], [0.6, 6, 0.6], [0, 0], region="dark")
    body.cube([-bw / 2 + 1, y - 1, -bl / 2 + 2], [1, 1, bl - 4], [0, 0], region="metal")  # skids
    body.cube([bw / 2 - 2, y - 1, -bl / 2 + 2], [1, 1, bl - 4], [0, 0], region="metal")
    for s in range(v["seats"]):
        _seatmark(g, 0, y + 6, -2 + s * 3)
    g.bounds = [20, y + 9]
    g.bounds_offset = [0, y + 3, 0]


def _glider(g, v):
    y = 6
    body = g.bone("body", (0, y, 0), parent="root")
    body.cube([-2, y, -6], [4, 3, 14], [0, 0], region="body")
    body.cube([-22, y + 2, -2], [44, 1, 8], [0, 0], region="trim")               # big wing
    body.cube([-0.5, y + 2, 6], [1, 4, 4], [0, 0], region="trim")                # tail
    _seatmark(g, 0, y + 3, 0)
    g.bounds = [24, y + 6]
    g.bounds_offset = [0, y + 2, 0]


def _balloon(g, v):
    body = g.bone("body", (0, 4, 0), parent="root")
    # envelope (stacked rings)
    for i, (yy, r) in enumerate([(16, 7), (20, 9), (26, 9), (32, 7), (37, 4)]):
        body.cube([-r, yy, -r], [r * 2, 5, r * 2], [0, 0], region="body" if i % 2 else "trim")
    # basket
    body.cube([-3, 2, -3], [6, 4, 6], [0, 0], region="glass")
    for x in (-2.5, 2.5):                                                         # ropes
        body.cube([x, 6, -2.5], [0.4, 10, 0.4], [0, 0], region="dark")
        body.cube([x, 6, 2.1], [0.4, 10, 0.4], [0, 0], region="dark")
    for s in range(v["seats"]):
        _seatmark(g, -1 + s * 2, 3, 0)
    g.bounds = [10, 42]
    g.bounds_offset = [0, 20, 0]


def _boat(g, v):
    bl, bw = 20, 8
    body = g.bone("body", (0, 2, 0), parent="root")
    body.cube([-bw / 2, 2, -bl / 2], [bw, 3, bl], [0, 0], region="body")          # hull
    body.cube([-bw / 2 + 0.6, 1, -bl / 2 + 3], [bw - 1.2, 1.5, bl - 6], [0, 0], region="trim")
    body.cube([-bw / 2 + 1, 5, -2], [bw - 2, 2.5, 5], [0, 0], region="glass")     # windshield
    body.cube([-1, 5, 2], [2, 1, 1], [0, 0], region="metal")                      # wheel
    for s in range(v["seats"]):
        _seatmark(g, 0, 5, 1 + s * 3)
    g.bounds = [bl / 2 + 2, 8]
    g.bounds_offset = [0, 3, 0]


def _jetski(g, v):
    bl, bw = 12, 4
    body = g.bone("body", (0, 2, 0), parent="root")
    body.cube([-bw / 2, 2, -bl / 2], [bw, 3, bl], [0, 0], region="body")
    body.cube([-1.2, 5, 0], [2.4, 2, 4], [0, 0], region="seat")
    body.cube([-2.5, 6, -bl / 2 + 1], [5, 1, 1], [0, 0], region="metal")          # handlebars
    for s in range(v["seats"]):
        _seatmark(g, 0, 5, s * 3)
    g.bounds = [bl / 2 + 2, 8]
    g.bounds_offset = [0, 3, 0]


def _sub(g, v):
    bl, bw = 24, 7
    y = 4
    body = g.bone("body", (0, y, 0), parent="root")
    body.cube([-bw / 2, y, -bl / 2], [bw, bw, bl], [0, 0], region="body")
    body.cube([-2, y + bw, -3], [4, 4, 6], [0, 0], region="trim")                 # conning tower
    body.cube([-1.5, y + bw + 4, -2.5], [3, 2, 4], [0, 0], region="glass")        # viewport
    for z in (-4, 2, 6):                                                          # portholes
        body.cube([-bw / 2 - 0.3, y + 2, z], [0.4, 2, 2], [0, 0], region="glass")
        body.cube([bw / 2 - 0.1, y + 2, z], [0.4, 2, 2], [0, 0], region="glass")
    prop = g.bone("prop", (0, y + bw / 2, bl / 2), parent="body")
    prop.cube([-0.5, y + bw / 2 - 4, bl / 2], [1, 8, 1], [0, 0], region="dark")
    prop.cube([-4, y + bw / 2 - 0.5, bl / 2], [8, 1, 1], [0, 0], region="dark")
    for s in range(v["seats"]):
        _seatmark(g, 0, y + bw, -3 + s * 3)
    g.bounds = [bl / 2 + 2, y + bw + 6]
    g.bounds_offset = [0, y + bw / 2, 0]


def _pontoon(g, v):
    bl, bw = 22, 12
    body = g.bone("body", (0, 3, 0), parent="root")
    body.cube([-bw / 2, 1, -bl / 2], [3, 3, bl], [0, 0], region="trim")           # left pontoon
    body.cube([bw / 2 - 3, 1, -bl / 2], [3, 3, bl], [0, 0], region="trim")        # right pontoon
    body.cube([-bw / 2, 4, -bl / 2 + 1], [bw, 1, bl - 2], [0, 0], region="body")  # deck
    for x in (-bw / 2, bw / 2 - 0.6):                                             # railing
        body.cube([x, 5, -bl / 2 + 1], [0.6, 3, bl - 2], [0, 0], region="metal")
    body.cube([-3, 5, -bl / 2 + 2], [6, 3, 3], [0, 0], region="glass")            # console
    for s in range(v["seats"]):
        _seatmark(g, -2 + (s % 2) * 4, 5, -2 + (s // 2) * 5)
    g.bounds = [bl / 2 + 2, 9]
    g.bounds_offset = [0, 4, 0]
