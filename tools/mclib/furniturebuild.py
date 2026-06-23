"""Parametric furniture block builder. build(type_key) -> Geometry in block space.

Block space: x,z in [-8, 8], y in [0, 16] (one 16^3 cell). Geometry is static (no
animation), one bone "block". Styling comes from the per-style palette at paint time,
so each type's geometry is authored once and recoloured for all three styles.
"""
from __future__ import annotations
from .geometry import Geometry

ID = "geometry.wf_furn"


def build(key):
    g = Geometry(f"{ID}_{key}", 1, 1)
    b = g.bone("block", (0, 0, 0))
    BUILDERS[key](b)
    g.tex_w = g.tex_h = 64
    g.bounds = [2, 2]
    g.bounds_offset = [0, 8, 0]
    return g


def legs(b, h, inset=6, region="fleg", w=2):
    for x in (-inset, inset - w):
        for z in (-inset, inset - w):
            b.cube([x, 0, z], [w, h, w], [0, 0], region=region)


def _chair(b):
    legs(b, 7)
    b.cube([-6, 7, -6], [12, 2, 12], [0, 0], region="ffabric")        # seat
    b.cube([-6, 9, 4], [12, 7, 2], [0, 0], region="fwood")            # backrest


def _stool(b):
    legs(b, 7, inset=5)
    b.cube([-5, 7, -5], [10, 2, 10], [0, 0], region="ffabric")


def _sofa(b):
    b.cube([-8, 0, -6], [16, 6, 12], [0, 0], region="fwood")          # base
    b.cube([-8, 6, -6], [16, 3, 12], [0, 0], region="ffabric")        # cushion
    b.cube([-8, 9, 4], [16, 6, 2], [0, 0], region="ffabric")          # back
    b.cube([-8, 6, -6], [2, 6, 12], [0, 0], region="ffabric")         # arms
    b.cube([6, 6, -6], [2, 6, 12], [0, 0], region="ffabric")


def _armchair(b):
    b.cube([-7, 0, -6], [14, 6, 12], [0, 0], region="fwood")
    b.cube([-6, 6, -6], [12, 3, 11], [0, 0], region="ffabric")
    b.cube([-6, 9, 4], [12, 6, 2], [0, 0], region="ffabric")
    b.cube([-7, 6, -6], [2, 6, 11], [0, 0], region="ffabric")
    b.cube([5, 6, -6], [2, 6, 11], [0, 0], region="ffabric")


def _dining_table(b):
    legs(b, 12, inset=6)
    b.cube([-8, 12, -8], [16, 2, 16], [0, 0], region="ftop")


def _coffee_table(b):
    legs(b, 6, inset=6)
    b.cube([-8, 6, -8], [16, 2, 16], [0, 0], region="ftop")


def _desk(b):
    b.cube([-8, 0, 4], [16, 13, 4], [0, 0], region="fwood")           # back panel/drawers
    b.cube([6, 0, -8], [2, 13, 12], [0, 0], region="fleg")            # side
    b.cube([-8, 12, -8], [16, 2, 16], [0, 0], region="ftop")          # top
    b.cube([-8, 0, -8], [2, 13, 2], [0, 0], region="fleg")            # front leg
    b.cube([-6, 5, 4.0], [10, 4, 0.4], [0, 0], region="fmetal")       # drawer face


def _box_frame(b, h=16):
    b.cube([-8, 0, -8], [16, h, 16], [0, 0], region="fwood")
    b.cube([-7, 1, -8.2], [14, h - 2, 0.4], [0, 0], region="fdark")   # recessed front


def _bookshelf(b):
    _box_frame(b)
    for y in (4, 8, 12):
        b.cube([-7, y, -7], [14, 1, 7], [0, 0], region="fdark")       # shelves
        b.cube([-6, y + 1, -7], [12, 3, 3], [0, 0], region="faccent")  # books


def _drawer(b):
    b.cube([-8, 0, -8], [16, 12, 16], [0, 0], region="fwood")
    for y in (1, 5, 9):
        b.cube([-7, y, -8.3], [14, 3, 0.4], [0, 0], region="ftrim")   # drawer face
        b.cube([-1, y + 1, -8.6], [2, 1, 0.4], [0, 0], region="fmetal")  # handle


def _cabinet(b):
    _box_frame(b)
    b.cube([-7, 1, -8.3], [6.5, 14, 0.5], [0, 0], region="ftrim")     # left door
    b.cube([0.5, 1, -8.3], [6.5, 14, 0.5], [0, 0], region="ftrim")    # right door
    b.cube([-1.5, 7, -8.7], [1, 3, 0.4], [0, 0], region="fmetal")     # handles
    b.cube([0.5, 7, -8.7], [1, 3, 0.4], [0, 0], region="fmetal")


def _wardrobe(b):
    _box_frame(b)
    b.cube([-7, 1, -8.3], [6.5, 14, 0.5], [0, 0], region="ftrim")
    b.cube([0.5, 1, -8.3], [6.5, 14, 0.5], [0, 0], region="ftrim")
    b.cube([-1, 6, -8.8], [0.6, 5, 0.4], [0, 0], region="fmetal")
    b.cube([0.4, 6, -8.8], [0.6, 5, 0.4], [0, 0], region="fmetal")


def _fridge(b):
    b.cube([-7, 0, -8], [14, 16, 15], [0, 0], region="fmetal")
    b.cube([-7, 0, -8.3], [14, 9, 0.4], [0, 0], region="ftrim")       # lower door
    b.cube([-7, 9.5, -8.3], [14, 6.5, 0.4], [0, 0], region="ftrim")   # upper door
    b.cube([4, 4, -8.8], [0.8, 8, 0.6], [0, 0], region="fmetal")      # handle


def _lamp(b):
    b.cube([-3, 0, -3], [6, 1, 6], [0, 0], region="fmetal")           # base
    b.cube([-1, 1, -1], [2, 8, 2], [0, 0], region="fmetal")           # post
    b.cube([-4, 9, -4], [8, 5, 8], [0, 0], region="flight")           # shade


def _floor_lamp(b):
    b.cube([-3, 0, -3], [6, 1, 6], [0, 0], region="fmetal")
    b.cube([-1, 1, -1], [2, 12, 2], [0, 0], region="fmetal")
    b.cube([-4, 12, -4], [8, 4, 8], [0, 0], region="flight")


def _wall_lamp(b):
    b.cube([-2, 4, 6], [4, 3, 2], [0, 0], region="fmetal")            # bracket on back wall
    b.cube([-3, 1, 2], [6, 4, 6], [0, 0], region="flight")            # globe


def _bed(b):
    b.cube([-8, 0, -8], [16, 4, 16], [0, 0], region="fwood")          # frame
    b.cube([-7, 4, -7], [14, 2, 14], [0, 0], region="ffabric")        # mattress
    b.cube([-7, 6, 3], [14, 3, 4], [0, 0], region="flight")           # pillow (bright)


def _rug(b):
    b.cube([-8, 0, -8], [16, 1, 16], [0, 0], region="ffabric")
    b.cube([-6, 1, -6], [12, 0.2, 12], [0, 0], region="faccent")      # pattern


def _plant(b):
    b.cube([-3, 0, -3], [6, 5, 6], [0, 0], region="ftrim")            # pot
    b.cube([-2, 5, -2], [4, 2, 4], [0, 0], region="fdark")            # soil
    b.cube([-4, 7, -4], [8, 7, 8], [0, 0], region="faccent")          # foliage
    b.cube([-2, 13, -2], [4, 3, 4], [0, 0], region="faccent")


BUILDERS = {
    "chair": _chair, "stool": _stool, "sofa": _sofa, "armchair": _armchair,
    "dining_table": _dining_table, "coffee_table": _coffee_table, "desk": _desk,
    "bookshelf": _bookshelf, "drawer": _drawer, "cabinet": _cabinet, "wardrobe": _wardrobe,
    "fridge": _fridge, "lamp": _lamp, "floor_lamp": _floor_lamp, "wall_lamp": _wall_lamp,
    "bed": _bed, "rug": _rug, "plant": _plant,
}
