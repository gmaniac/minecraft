"""Wildforge vehicle roster — 17 rideable vehicles (land / air / water).

category: land | air | water   (drives the control scheme)
plan:     car|bus|bike|plane|jet|heli|glider|balloon|boat|jetski|sub|pontoon
seats:    1-4
speed:    flying_speed value (arcade-fast)
craft:    a representative ingredient for the crafted spawn item

palette keys: body, trim, glass, accent, dark
"""

VEHICLES = [
    # ---------------- land ----------------
    {"id": "sports_car", "name": "Sports Car", "category": "land", "plan": "car", "seats": 2,
     "health": 60, "scale": 1.0, "speed": 0.34, "craft": "minecraft:iron_ingot",
     "palette": {"body": "#c4202a", "trim": "#9a9a9a", "glass": "#26323a", "accent": "#ffd24a",
                  "dark": "#141414"}},
    {"id": "sedan", "name": "Sedan", "category": "land", "plan": "car", "seats": 4,
     "health": 70, "scale": 1.05, "speed": 0.28, "craft": "minecraft:iron_ingot",
     "palette": {"body": "#2a5db0", "trim": "#b0b0b0", "glass": "#26323a", "accent": "#e8e8e8",
                  "dark": "#141414"}},
    {"id": "pickup", "name": "Pickup Truck", "category": "land", "plan": "car", "seats": 2,
     "health": 90, "scale": 1.15, "speed": 0.27, "craft": "minecraft:iron_ingot",
     "palette": {"body": "#3a3a40", "trim": "#8a8a8a", "glass": "#26323a", "accent": "#c0392b",
                  "dark": "#101010"}},
    {"id": "monster_truck", "name": "Monster Truck", "category": "land", "plan": "car", "seats": 2,
     "health": 120, "scale": 1.3, "speed": 0.3, "craft": "minecraft:iron_block",
     "palette": {"body": "#1aa84a", "trim": "#9a9a9a", "glass": "#26323a", "accent": "#ffd24a",
                  "dark": "#0a0a0a"}},
    {"id": "bus", "name": "Bus", "category": "land", "plan": "bus", "seats": 4,
     "health": 140, "scale": 1.2, "speed": 0.24, "craft": "minecraft:iron_block",
     "palette": {"body": "#e0a52a", "trim": "#b0b0b0", "glass": "#26323a", "accent": "#3a3a40",
                  "dark": "#141414"}},
    {"id": "motorbike", "name": "Motorbike", "category": "land", "plan": "bike", "seats": 1,
     "health": 40, "scale": 0.95, "speed": 0.4, "craft": "minecraft:iron_ingot",
     "palette": {"body": "#111317", "trim": "#9a9a9a", "glass": "#26323a", "accent": "#c4202a",
                  "dark": "#0a0a0a"}},
    {"id": "atv", "name": "Quad ATV", "category": "land", "plan": "bike", "seats": 1,
     "health": 50, "scale": 1.0, "speed": 0.34, "craft": "minecraft:iron_ingot",
     "palette": {"body": "#c0392b", "trim": "#8a8a8a", "glass": "#26323a", "accent": "#2a2a2a",
                  "dark": "#0a0a0a"}},
    {"id": "dune_buggy", "name": "Dune Buggy", "category": "land", "plan": "car", "seats": 2,
     "health": 50, "scale": 1.0, "speed": 0.36, "craft": "minecraft:iron_ingot",
     "palette": {"body": "#e8b53a", "trim": "#6a6a6a", "glass": "#26323a", "accent": "#2a2a2a",
                  "dark": "#0a0a0a"}},
    # ---------------- air ----------------
    {"id": "prop_plane", "name": "Propeller Plane", "category": "air", "plan": "plane", "seats": 2,
     "health": 60, "scale": 1.1, "speed": 0.3, "craft": "minecraft:iron_ingot",
     "palette": {"body": "#d8d8e0", "trim": "#9a9a9a", "glass": "#26323a", "accent": "#c4202a",
                  "dark": "#2a2a2a"}},
    {"id": "jet", "name": "Jet", "category": "air", "plan": "jet", "seats": 1,
     "health": 70, "scale": 1.2, "speed": 0.42, "craft": "minecraft:diamond",
     "palette": {"body": "#5a6a7a", "trim": "#cacaca", "glass": "#26323a", "accent": "#e8e8e8",
                  "dark": "#1a1a1a"}},
    {"id": "helicopter", "name": "Helicopter", "category": "air", "plan": "heli", "seats": 3,
     "health": 80, "scale": 1.15, "speed": 0.3, "craft": "minecraft:diamond",
     "palette": {"body": "#2a6a3a", "trim": "#9a9a9a", "glass": "#26323a", "accent": "#ffd24a",
                  "dark": "#141414"}},
    {"id": "glider", "name": "Glider", "category": "air", "plan": "glider", "seats": 1,
     "health": 30, "scale": 1.1, "speed": 0.32, "craft": "minecraft:feather",
     "palette": {"body": "#e8e8ee", "trim": "#bcbcc4", "glass": "#26323a", "accent": "#3aa6e6",
                  "dark": "#3a3a3a"}},
    {"id": "balloon", "name": "Hot-Air Balloon", "category": "air", "plan": "balloon", "seats": 2,
     "health": 40, "scale": 1.3, "speed": 0.2, "craft": "minecraft:leather",
     "palette": {"body": "#c4202a", "trim": "#e0a52a", "glass": "#8a5a2a", "accent": "#e8e8e8",
                  "dark": "#5a3a1a"}},
    # ---------------- water ----------------
    {"id": "speedboat", "name": "Speedboat", "category": "water", "plan": "boat", "seats": 3,
     "health": 60, "scale": 1.1, "speed": 0.36, "craft": "minecraft:iron_ingot",
     "palette": {"body": "#e8e8ee", "trim": "#2a5db0", "glass": "#26323a", "accent": "#c4202a",
                  "dark": "#2a2a2a"}},
    {"id": "jetski", "name": "Jetski", "category": "water", "plan": "jetski", "seats": 2,
     "health": 40, "scale": 0.95, "speed": 0.4, "craft": "minecraft:iron_ingot",
     "palette": {"body": "#1aa8c4", "trim": "#9a9a9a", "glass": "#26323a", "accent": "#ffd24a",
                  "dark": "#1a1a1a"}},
    {"id": "submarine", "name": "Submarine", "category": "water", "plan": "sub", "seats": 3,
     "health": 100, "scale": 1.2, "speed": 0.26, "craft": "minecraft:iron_block",
     "palette": {"body": "#d8b53a", "trim": "#8a7a3a", "glass": "#3a8ad8", "accent": "#2a2a2a",
                  "dark": "#1a1a1a"}},
    {"id": "pontoon", "name": "Pontoon Boat", "category": "water", "plan": "pontoon", "seats": 4,
     "health": 70, "scale": 1.15, "speed": 0.26, "craft": "minecraft:iron_ingot",
     "palette": {"body": "#9a7a4a", "trim": "#6a6a6a", "glass": "#26323a", "accent": "#3aa6e6",
                  "dark": "#3a3a3a"}},
]

_ids = [v["id"] for v in VEHICLES]
assert len(_ids) == len(set(_ids)), "duplicate vehicle id"
