"""16x16 material textures for HomeBuilding full-cube blocks.

Deterministic patterns (no RNG, so regeneration is stable) per category.
"""
from __future__ import annotations
from .texture import Tex, shade, hex_rgba


def _noise(i, j):
    return ((i * 73 + j * 151) % 7) - 3   # small deterministic dither in [-3, 3]


def build(mat) -> Tex:
    t = Tex(16, 16)
    c = hex_rgba(mat["c"])
    c2 = hex_rgba(mat["c2"])
    cat = mat["cat"]
    a = 150 if mat.get("glass") else 255
    base = (c[0], c[1], c[2], a)
    fn = PATTERNS.get(cat, _flat)
    fn(t, base, c2)
    return t


def _flat(t, c, c2):
    for j in range(16):
        for i in range(16):
            n = _noise(i, j)
            t.px[i, j] = (max(0, min(255, c[0] + n)), max(0, min(255, c[1] + n)),
                          max(0, min(255, c[2] + n)), c[3])


def _planks(t, c, c2):
    _flat(t, c, c2)
    for j in (0, 5, 10, 15):                      # plank seams (horizontal)
        for i in range(16):
            t.px[i, j] = c2
    for x in (3, 11):                             # nail/joint offsets
        t.px[x, 2] = c2
        t.px[(x + 5) % 16, 12] = c2


def _beam(t, c, c2):
    _flat(t, c, c2)
    for i in (0, 5, 10, 15):                      # vertical grain
        for j in range(16):
            t.px[i, j] = c2


def _brick(t, c, c2):
    for j in range(16):
        for i in range(16):
            t.px[i, j] = c
    for j in (0, 4, 8, 12):                       # mortar rows
        for i in range(16):
            t.px[i, j] = c2
    for j in range(16):                            # offset vertical mortar
        row = j // 4
        off = 0 if row % 2 == 0 else 4
        for i in range(off, 16, 8):
            t.px[i % 16, j] = c2


def _shingle(t, c, c2):
    for j in range(16):
        for i in range(16):
            t.px[i, j] = shade(c, 1.0 + 0.06 * ((j // 4) % 2))
    for j in (3, 7, 11, 15):                       # overlapping rows
        for i in range(16):
            t.px[i, j] = c2
    for j in range(16):                            # scallop offsets
        row = j // 4
        off = 0 if row % 2 == 0 else 4
        for i in range(off, 16, 8):
            t.px[i % 16, j] = c2


def _siding(t, c, c2):
    _flat(t, c, c2)
    for i in (0, 4, 8, 12):                        # vertical boards
        for j in range(16):
            t.px[i, j] = c2


def _tile(t, c, c2):
    _flat(t, c, c2)
    for k in (0, 8):                               # grid
        for n in range(16):
            t.px[k, n] = c2
            t.px[n, k] = c2


def _trim(t, c, c2):
    _flat(t, c, c2)
    for n in range(16):                            # border
        for k in (0, 15):
            t.px[k, n] = c2
            t.px[n, k] = c2


def _glass(t, c, c2):
    for j in range(16):
        for i in range(16):
            t.px[i, j] = c
    for n in range(16):                            # frame
        for k in (0, 15):
            t.px[k, n] = c2
            t.px[n, k] = c2
    t.px[4, 4] = shade(c, 1.4)                     # highlight
    t.px[5, 5] = shade(c, 1.4)


PATTERNS = {"planks": _planks, "beam": _beam, "brick": _brick, "shingle": _shingle,
            "siding": _siding, "tile": _tile, "trim": _trim, "glass": _glass,
            "stone": _flat, "plaster": _flat, "floor": _planks}
