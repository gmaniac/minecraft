"""Wildforge HomeBuilding — 35 material blocks + 8 prefab structures.

Materials are full-cube custom blocks (reliable, no experimental geometry):
  cat -> texture pattern in mclib/matbuild.py
  glass=True -> blended/translucent render
  craft -> ingredient the shapeless recipe consumes (x4)
"""

CRAFT = {"planks": "minecraft:oak_planks", "beam": "minecraft:stripped_oak_log",
         "stone": "minecraft:stone", "brick": "minecraft:brick", "plaster": "minecraft:clay_ball",
         "glass": "minecraft:glass", "shingle": "minecraft:brick", "siding": "minecraft:oak_planks",
         "floor": "minecraft:oak_planks", "trim": "minecraft:stick"}

MATERIALS = [
    # planks (4)
    {"id": "ashwood_planks", "label": "Ashwood Planks", "cat": "planks", "c": "#cdbb96", "c2": "#a8946a"},
    {"id": "walnut_planks", "label": "Walnut Planks", "cat": "planks", "c": "#6a4a32", "c2": "#4a3120"},
    {"id": "pine_planks", "label": "Pine Planks", "cat": "planks", "c": "#caa46a", "c2": "#9c7842"},
    {"id": "ebony_planks", "label": "Ebony Planks", "cat": "planks", "c": "#2c2620", "c2": "#191512"},
    # beams (4)
    {"id": "ashwood_beam", "label": "Ashwood Beam", "cat": "beam", "c": "#bda37e", "c2": "#917a52"},
    {"id": "walnut_beam", "label": "Walnut Beam", "cat": "beam", "c": "#5e4128", "c2": "#3e2a18"},
    {"id": "pine_beam", "label": "Pine Beam", "cat": "beam", "c": "#b8945c", "c2": "#8a6a38"},
    {"id": "ebony_beam", "label": "Ebony Beam", "cat": "beam", "c": "#26211b", "c2": "#15110d"},
    # stone (5)
    {"id": "smooth_slate", "label": "Smooth Slate", "cat": "stone", "c": "#54585e", "c2": "#3e4248"},
    {"id": "granite_tile", "label": "Granite Tile", "cat": "tile", "c": "#9a6a5a", "c2": "#6e4a3e"},
    {"id": "marble", "label": "Marble", "cat": "stone", "c": "#e8e6df", "c2": "#cfccc2"},
    {"id": "sandstone_brick", "label": "Sandstone Brick", "cat": "brick", "c": "#dac79a", "c2": "#b6a274"},
    {"id": "bluestone", "label": "Bluestone", "cat": "stone", "c": "#43566a", "c2": "#2f3e4e"},
    # bricks (3)
    {"id": "red_brick", "label": "Red Brick", "cat": "brick", "c": "#9c4836", "c2": "#6e3326"},
    {"id": "grey_brick", "label": "Grey Brick", "cat": "brick", "c": "#7a7d82", "c2": "#5a5d62"},
    {"id": "clay_brick", "label": "Clay Brick", "cat": "brick", "c": "#c08a5a", "c2": "#94653c"},
    # plaster / concrete (4)
    {"id": "plaster_white", "label": "White Plaster", "cat": "plaster", "c": "#e6e4dd", "c2": "#d2d0c8"},
    {"id": "plaster_grey", "label": "Grey Plaster", "cat": "plaster", "c": "#9b9ea2", "c2": "#888b8f"},
    {"id": "plaster_charcoal", "label": "Charcoal Plaster", "cat": "plaster", "c": "#3a3d42", "c2": "#2e3136"},
    {"id": "plaster_tan", "label": "Tan Plaster", "cat": "plaster", "c": "#cbb489", "c2": "#b39e76"},
    # glass (3)
    {"id": "clear_glass", "label": "Clear Glass", "cat": "glass", "c": "#bfe6f0", "c2": "#8fbfd0", "glass": True},
    {"id": "tinted_glass", "label": "Tinted Glass", "cat": "glass", "c": "#3a4a55", "c2": "#26323a", "glass": True},
    {"id": "frosted_glass", "label": "Frosted Glass", "cat": "glass", "c": "#dfeef2", "c2": "#c2d6dc", "glass": True},
    # shingle / roofing (4)
    {"id": "red_shingle", "label": "Red Shingle", "cat": "shingle", "c": "#9a3a2a", "c2": "#6e271c"},
    {"id": "grey_shingle", "label": "Grey Shingle", "cat": "shingle", "c": "#565a60", "c2": "#3e4146"},
    {"id": "wood_shingle", "label": "Wood Shingle", "cat": "shingle", "c": "#8a6038", "c2": "#5f4124"},
    {"id": "slate_shingle", "label": "Slate Shingle", "cat": "shingle", "c": "#41474f", "c2": "#2c3138"},
    # siding (3)
    {"id": "white_siding", "label": "White Siding", "cat": "siding", "c": "#e6e6e2", "c2": "#ccccca"},
    {"id": "blue_siding", "label": "Blue Siding", "cat": "siding", "c": "#4a6f96", "c2": "#37536f"},
    {"id": "cedar_siding", "label": "Cedar Siding", "cat": "siding", "c": "#b07444", "c2": "#8a5730"},
    # flooring (3)
    {"id": "hardwood_floor", "label": "Hardwood Floor", "cat": "floor", "c": "#9a6c3e", "c2": "#754f2a"},
    {"id": "ceramic_tile", "label": "Ceramic Tile", "cat": "tile", "c": "#dadbd8", "c2": "#aeb0ad"},
    {"id": "parquet", "label": "Parquet", "cat": "floor", "c": "#b1834c", "c2": "#8a6236"},
    # trim (2)
    {"id": "white_trim", "label": "White Trim", "cat": "trim", "c": "#eceae3", "c2": "#c7c5bd"},
    {"id": "oak_trim", "label": "Oak Trim", "cat": "trim", "c": "#9a6a3a", "c2": "#714924"},
]

PREFABS = [
    {"id": "modern_house", "label": "Modern House"},
    {"id": "cozy_cottage", "label": "Cozy Cottage"},
    {"id": "cabin", "label": "Cabin"},
    {"id": "mansion", "label": "Mansion"},
    {"id": "tower", "label": "Tower"},
    {"id": "barn", "label": "Barn"},
    {"id": "shop", "label": "Shop"},
    {"id": "starter_base", "label": "Starter Base"},
]

_ids = [m["id"] for m in MATERIALS]
assert len(_ids) == len(set(_ids)), "duplicate material id"
