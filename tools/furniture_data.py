"""Wildforge furniture roster — 18 types x 3 styles = 54 custom blocks.

Each TYPE has a geometry builder (mclib/furniturebuild.py) and flags:
  sit     -> spawns an invisible seat entity on interact (seat_y = ride height)
  storage -> opens a script-backed virtual inventory on interact
  light   -> light_emission level (0 = none)
  facing  -> rotates to face the player on placement
  h       -> collision/selection height in block-units (1..16)

STYLE palettes use furniture region keys: wood, trim, accent, metal, fabric, dark, glass, light.
"""

TYPES = [
    {"key": "chair", "label": "Chair", "sit": True, "seat_y": 0.5, "facing": True, "h": 16},
    {"key": "stool", "label": "Stool", "sit": True, "seat_y": 0.55, "facing": False, "h": 10},
    {"key": "sofa", "label": "Sofa", "sit": True, "seat_y": 0.5, "facing": True, "h": 10},
    {"key": "armchair", "label": "Armchair", "sit": True, "seat_y": 0.5, "facing": True, "h": 12},
    {"key": "dining_table", "label": "Dining Table", "facing": False, "h": 14},
    {"key": "coffee_table", "label": "Coffee Table", "facing": False, "h": 8},
    {"key": "desk", "label": "Desk", "storage": True, "facing": True, "h": 14},
    {"key": "bookshelf", "label": "Bookshelf", "storage": True, "facing": True, "h": 16},
    {"key": "drawer", "label": "Drawers", "storage": True, "facing": True, "h": 12},
    {"key": "cabinet", "label": "Cabinet", "storage": True, "facing": True, "h": 16},
    {"key": "wardrobe", "label": "Wardrobe", "storage": True, "facing": True, "h": 16},
    {"key": "fridge", "label": "Fridge", "storage": True, "facing": True, "h": 16},
    {"key": "lamp", "label": "Lamp", "light": 14, "facing": False, "h": 16},
    {"key": "floor_lamp", "label": "Floor Lamp", "light": 14, "facing": False, "h": 16},
    {"key": "wall_lamp", "label": "Wall Lamp", "light": 13, "facing": True, "h": 8},
    {"key": "bed", "label": "Bed", "facing": True, "h": 8},
    {"key": "rug", "label": "Rug", "facing": False, "h": 1},
    {"key": "plant", "label": "Potted Plant", "facing": False, "h": 14},
]

STYLES = {
    "modern": {
        "label": "Modern", "material": "minecraft:quartz_block",
        "palette": {"wood": "#d9d9de", "trim": "#9aa0a6", "accent": "#2a8ad4", "metal": "#b8bcc2",
                     "fabric": "#3a3f47", "dark": "#1c1f24", "glass": "#2a3640", "light": "#fff3c4"}},
    "rustic": {
        "label": "Rustic", "material": "minecraft:oak_planks",
        "palette": {"wood": "#9a6a3a", "trim": "#7a5128", "accent": "#c0392b", "metal": "#8a7a5a",
                     "fabric": "#c9a36a", "dark": "#3a2616", "glass": "#3a4a40", "light": "#ffd98a"}},
    "medieval": {
        "label": "Medieval", "material": "minecraft:dark_oak_planks",
        "palette": {"wood": "#4a3322", "trim": "#2e1f14", "accent": "#7a1f1f", "metal": "#5a5a64",
                     "fabric": "#5a3a6a", "dark": "#1a1109", "glass": "#2a3a3a", "light": "#ffcf6a"}},
}

# how many of the style material the crafting recipe consumes
CRAFT_COUNT = {"chair": 5, "stool": 3, "sofa": 6, "armchair": 6, "dining_table": 5,
               "coffee_table": 4, "desk": 6, "bookshelf": 6, "drawer": 6, "cabinet": 7,
               "wardrobe": 8, "fridge": 7, "lamp": 3, "floor_lamp": 4, "wall_lamp": 3,
               "bed": 5, "rug": 3, "plant": 2}
