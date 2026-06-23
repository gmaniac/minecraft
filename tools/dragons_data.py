"""Wildforge dragon roster — 21 dragons as parameter blocks.

Each entry drives the procedural model, texture, entity, spawn rule and lang.
Keeping the roster as data (not hand-authored JSON) is what makes 21 distinct
dragons maintainable. Colours are hex; the texture painter shades them per-face.

archetype: western | wyvern | serpentine | drake | four_winged | multi_head
tier:      common (breeds, lays eggs) | mythic (singular, ultra-rare, no breeding)
element:   selects breath attack + aura/trail FX in scripts/dragons/index.js
"""

STEAK = ["minecraft:cooked_beef", "minecraft:beef"]
SALMON = ["minecraft:cooked_salmon", "minecraft:salmon"]
GAPPLE = ["minecraft:golden_apple"]
EGAPPLE = ["minecraft:enchanted_golden_apple"]
GCARROT = ["minecraft:golden_carrot"]
NSTAR = ["minecraft:nether_star"]

DRAGONS = [
    # ---------------- reworked existing commons ----------------
    {
        "id": "ember", "name": "Ember Dragon", "archetype": "western", "tier": "common",
        "element": "fire", "food": STEAK, "health": 40, "scale": 1.15, "move": 0.30,
        "spawn": {"dimension": "overworld", "biome": "overworld", "bright": (7, 15), "weight": 5},
        "palette": {"body": "#7a2e1c", "belly": "#c9763a", "accent": "#e0a93b",
                     "membrane": "#d6552b", "horn": "#2a1810", "eye": "#ffcf3a"},
        "features": {"neck": 3, "horns": "swept", "spines": {"n": 10, "style": "spike", "sz": 1.0},
                      "tail_tip": "spike", "wing_style": "membrane", "extras": ["flame_ridge"]},
    },
    {
        "id": "storm", "name": "Storm Dragon", "archetype": "western", "tier": "common",
        "element": "wind", "food": SALMON, "health": 38, "scale": 1.1, "move": 0.34,
        "spawn": {"dimension": "overworld", "biome": "overworld", "bright": (7, 15), "weight": 4},
        "palette": {"body": "#3b5f7a", "belly": "#b9d8e8", "accent": "#8fe0ff",
                     "membrane": "#7fc7f0", "horn": "#22323d", "eye": "#d6f6ff"},
        "features": {"neck": 4, "horns": "crest", "spines": {"n": 8, "style": "spike", "sz": 0.8},
                      "tail_tip": "fin", "wing_style": "crystalline", "extras": ["wind_frills"]},
    },
    {
        "id": "ancient", "name": "Ancient Dragon", "archetype": "drake", "tier": "common",
        "element": "stone", "food": GAPPLE, "health": 60, "scale": 1.3, "move": 0.26,
        "spawn": {"dimension": "overworld", "biome": "mountains", "bright": (0, 15), "weight": 2},
        "palette": {"body": "#5a534a", "belly": "#8a8276", "accent": "#b8a06a",
                     "membrane": "#6e6456", "horn": "#dcd0b0", "eye": "#ffd966"},
        "features": {"neck": 3, "horns": "crown", "spines": {"n": 12, "style": "spike", "sz": 1.2},
                      "tail_tip": "club", "wing_style": "membrane", "extras": ["frills", "stone_plates"]},
    },
    {
        "id": "glacier", "name": "Glacier Dragon", "archetype": "western", "tier": "common",
        "element": "frost", "food": GCARROT, "health": 44, "scale": 1.2, "move": 0.28,
        "spawn": {"dimension": "overworld", "biome": "ice", "bright": (0, 15), "weight": 3},
        "palette": {"body": "#6f96b8", "belly": "#dff1fb", "accent": "#bfeaff",
                     "membrane": "#a8dcf2", "horn": "#eaf7ff", "eye": "#9fe8ff"},
        "features": {"neck": 4, "horns": "single", "spines": {"n": 10, "style": "crystal", "sz": 1.1},
                      "tail_tip": "fin", "wing_style": "crystalline", "extras": ["ice_sail", "crystals"]},
    },
    {
        "id": "inferno", "name": "Inferno Dragon", "archetype": "wyvern", "tier": "common",
        "element": "netherfire", "food": GAPPLE, "health": 50, "scale": 1.2, "move": 0.32,
        "spawn": {"dimension": "nether", "biome": "nether", "bright": (0, 15), "weight": 3},
        "palette": {"body": "#3a1410", "belly": "#9c2b16", "accent": "#ff7a1a",
                     "membrane": "#b8341a", "horn": "#160a08", "eye": "#ffae2e"},
        "features": {"neck": 3, "horns": "swept", "spines": {"n": 11, "style": "spike", "sz": 1.0},
                      "tail_tip": "spike", "wing_style": "tattered", "extras": ["flame_ridge", "cracks"]},
    },
    {
        "id": "eclipse", "name": "Eclipse Dragon", "archetype": "four_winged", "tier": "common",
        "element": "void", "food": EGAPPLE, "health": 64, "scale": 1.25, "move": 0.36,
        "spawn": {"dimension": "the_end", "biome": "the_end", "bright": (0, 15), "weight": 2},
        "palette": {"body": "#241a33", "belly": "#5b3f7a", "accent": "#b07bf0",
                     "membrane": "#3a2557", "horn": "#0e0a14", "eye": "#caa6ff"},
        "features": {"neck": 4, "horns": "swept", "spines": {"n": 12, "style": "spike", "sz": 0.9},
                      "tail_tip": "spade", "wing_style": "four", "extras": ["ears", "void_motes"]},
    },
    # ---------------- reworked mythic legends ----------------
    {
        "id": "nidhoggr", "name": "Níðhǫggr", "archetype": "western", "tier": "mythic",
        "element": "decay", "food": EGAPPLE, "health": 220, "scale": 1.9, "move": 0.28,
        "spawn": {"dimension": "overworld", "underground": True, "bright": (0, 4), "weight": 1},
        "palette": {"body": "#3b3a30", "belly": "#6b5b3a", "accent": "#9bbf5a",
                     "membrane": "#4a4730", "horn": "#c8bd92", "eye": "#bfff66"},
        "features": {"neck": 5, "horns": "antler", "spines": {"n": 16, "style": "sail", "sz": 1.3},
                      "tail_tip": "spike", "wing_style": "tattered", "long_tail": 5, "extras": ["decay"]},
    },
    {
        "id": "apep", "name": "Apep", "archetype": "serpentine", "tier": "mythic",
        "element": "venom", "food": EGAPPLE, "health": 200, "scale": 1.7, "move": 0.30,
        "spawn": {"dimension": "overworld", "biome": "desert", "bright": (0, 7), "weight": 1},
        "palette": {"body": "#5a3a1a", "belly": "#caa05a", "accent": "#d4b35a",
                     "membrane": "#7a5a2a", "horn": "#2a1a0a", "eye": "#ff5a2a"},
        "features": {"neck": 2, "horns": "frill", "spines": {"n": 20, "style": "spike", "sz": 0.7},
                      "tail_tip": "none", "wing_style": "none", "body_segments": 10, "extras": ["fangs"]},
    },
    {
        "id": "tiamat", "name": "Tiamat", "archetype": "multi_head", "tier": "mythic",
        "element": "tidal", "food": NSTAR, "health": 260, "scale": 2.1, "move": 0.30,
        "spawn": {"dimension": "overworld", "biome": "ocean", "bright": (0, 15), "weight": 1},
        "palette": {"body": "#1c5a5a", "belly": "#8fd6cf", "accent": "#39c6c6",
                     "membrane": "#2a8a8a", "horn": "#dffaf6", "eye": "#7afff0"},
        "features": {"heads": 3, "neck": 4, "horns": "fin", "spines": {"n": 14, "style": "sail", "sz": 1.2},
                      "tail_tip": "fluke", "wing_style": "fin", "extras": ["webbed", "coral"]},
    },
    {
        "id": "hydra", "name": "The Hydra", "archetype": "multi_head", "tier": "mythic",
        "element": "venom", "food": EGAPPLE, "health": 240, "scale": 2.0, "move": 0.30,
        "spawn": {"dimension": "overworld", "biome": "swamp", "bright": (0, 15), "weight": 1},
        "palette": {"body": "#2f4a2a", "belly": "#7fa05a", "accent": "#9bd45a",
                     "membrane": "#3f5f33", "horn": "#1a2a14", "eye": "#c6ff5a"},
        "features": {"heads": 3, "neck": 5, "horns": "crest", "spines": {"n": 14, "style": "spike", "sz": 1.0},
                      "tail_tip": "spike", "wing_style": "none", "legs4": True, "extras": ["scales"]},
    },
    # ---------------- new commons ----------------
    {
        "id": "nature", "name": "Nature Dragon", "archetype": "western", "tier": "common",
        "element": "nature", "food": ["minecraft:apple", "minecraft:sweet_berries"],
        "health": 46, "scale": 1.2, "move": 0.30,
        "spawn": {"dimension": "overworld", "biome": "forest", "bright": (7, 15), "weight": 4},
        "palette": {"body": "#3f5a2a", "belly": "#86a85a",
                     "accent": "#cfe07a", "membrane": "#5a7a3a", "horn": "#6b4a2a", "eye": "#d6ff6a"},
        "features": {"neck": 4, "horns": "antler", "spines": {"n": 12, "style": "sail", "sz": 1.0},
                      "tail_tip": "spade", "wing_style": "membrane",
                      "extras": ["vines", "leaves", "flowers", "bark"]},
    },
    {
        "id": "lightning", "name": "Lightning Dragon", "archetype": "wyvern", "tier": "common",
        "element": "lightning", "food": ["minecraft:copper_ingot", "minecraft:cooked_chicken"],
        "health": 42, "scale": 1.15, "move": 0.36,
        "spawn": {"dimension": "overworld", "biome": "overworld", "bright": (7, 15), "weight": 3},
        "palette": {"body": "#27304a", "belly": "#9fb8e0", "accent": "#ffe34a",
                     "membrane": "#3a4a7a", "horn": "#1a2030", "eye": "#fff36a"},
        "features": {"neck": 3, "horns": "crest", "spines": {"n": 12, "style": "spike", "sz": 1.0},
                      "tail_tip": "fin", "wing_style": "tattered", "extras": ["spark_crest", "bolts"]},
    },
    {
        "id": "poison", "name": "Poison Dragon", "archetype": "drake", "tier": "common",
        "element": "venom", "food": ["minecraft:spider_eye", "minecraft:rotten_flesh"],
        "health": 48, "scale": 1.2, "move": 0.28,
        "spawn": {"dimension": "overworld", "biome": "swamp", "bright": (0, 15), "weight": 3},
        "palette": {"body": "#3a2f4a", "belly": "#7a9b3a", "accent": "#aaff3a",
                     "membrane": "#4a3a5a", "horn": "#1f1a2a", "eye": "#caff3a"},
        "features": {"neck": 3, "horns": "swept", "spines": {"n": 12, "style": "spike", "sz": 1.0},
                      "tail_tip": "stinger", "wing_style": "membrane", "extras": ["gas_sacs", "drips"]},
    },
    {
        "id": "desert", "name": "Desert Dragon", "archetype": "western", "tier": "common",
        "element": "drought", "food": ["minecraft:cactus", "minecraft:rabbit"],
        "health": 44, "scale": 1.2, "move": 0.30,
        "spawn": {"dimension": "overworld", "biome": "desert", "bright": (7, 15), "weight": 4},
        "palette": {"body": "#b9925a", "belly": "#e8d6a0", "accent": "#d4a85a",
                     "membrane": "#c8a86a", "horn": "#7a5a3a", "eye": "#ffcf6a"},
        "features": {"neck": 4, "horns": "ram", "spines": {"n": 14, "style": "spike", "sz": 0.8},
                      "tail_tip": "club", "wing_style": "membrane", "extras": ["sand_plates"]},
    },
    {
        "id": "spirit", "name": "Spirit Dragon", "archetype": "western", "tier": "common",
        "element": "spirit", "food": ["minecraft:glow_berries", "minecraft:glowstone_dust"],
        "health": 40, "scale": 1.15, "move": 0.34,
        "spawn": {"dimension": "overworld", "biome": "overworld", "bright": (0, 7), "weight": 2},
        "palette": {"body": "#5a7a8a", "belly": "#cfe8f0", "accent": "#bfffe0",
                     "membrane": "#7aa8b8", "horn": "#dffaf6", "eye": "#dfffff"},
        "features": {"neck": 4, "horns": "crest", "spines": {"n": 10, "style": "crystal", "sz": 0.9},
                      "tail_tip": "fin", "wing_style": "crystalline", "translucent": True,
                      "extras": ["wisps"]},
    },
    {
        "id": "magma", "name": "Magma Dragon", "archetype": "drake", "tier": "common",
        "element": "magma", "food": ["minecraft:magma_cream", "minecraft:cooked_beef"],
        "health": 54, "scale": 1.25, "move": 0.27,
        "spawn": {"dimension": "nether", "biome": "nether", "bright": (0, 15), "weight": 3},
        "palette": {"body": "#2a1410", "belly": "#7a2410", "accent": "#ff5a1a",
                     "membrane": "#5a1a10", "horn": "#140a06", "eye": "#ffb02e"},
        "features": {"neck": 3, "horns": "crown", "spines": {"n": 13, "style": "spike", "sz": 1.2},
                      "tail_tip": "club", "wing_style": "tattered", "extras": ["magma_cracks", "stone_plates"]},
    },
    {
        "id": "tidal", "name": "Tidal Dragon", "archetype": "western", "tier": "common",
        "element": "tidal", "food": SALMON, "health": 46, "scale": 1.2, "move": 0.30,
        "spawn": {"dimension": "overworld", "biome": "ocean", "bright": (0, 15), "weight": 3},
        "palette": {"body": "#1c4a6a", "belly": "#8fd0e8", "accent": "#39a6e6",
                     "membrane": "#2a6a8a", "horn": "#dff0fa", "eye": "#7adfff"},
        "features": {"neck": 4, "horns": "fin", "spines": {"n": 12, "style": "sail", "sz": 1.0},
                      "tail_tip": "fluke", "wing_style": "fin", "extras": ["webbed", "coral", "fins"]},
    },
    {
        "id": "bone", "name": "Bone Dragon", "archetype": "western", "tier": "common",
        "element": "necrotic", "food": ["minecraft:bone", "minecraft:rotten_flesh"],
        "health": 50, "scale": 1.2, "move": 0.30,
        "spawn": {"dimension": "overworld", "biome": "overworld", "bright": (0, 7), "weight": 2},
        "palette": {"body": "#cdc7b0", "belly": "#e8e2cf", "accent": "#9a948a",
                     "membrane": "#b8b2a0", "horn": "#f0ead8", "eye": "#6aff9a"},
        "features": {"neck": 4, "horns": "swept", "spines": {"n": 16, "style": "spike", "sz": 1.1},
                      "tail_tip": "spike", "wing_style": "skeletal", "extras": ["ribs", "bones"]},
    },
    {
        "id": "fae", "name": "Fae Dragon", "archetype": "four_winged", "tier": "common",
        "element": "spirit", "food": ["minecraft:honey_bottle", "minecraft:glow_berries"],
        "health": 30, "scale": 0.95, "move": 0.38,
        "spawn": {"dimension": "overworld", "biome": "flower_forest", "bright": (7, 15), "weight": 3},
        "palette": {"body": "#7a3a8a", "belly": "#e0a8f0", "accent": "#ff9ad6",
                     "membrane": "#c86ad6", "horn": "#fff0fa", "eye": "#ffd6ff"},
        "features": {"neck": 3, "horns": "crest", "spines": {"n": 8, "style": "crystal", "sz": 0.6},
                      "tail_tip": "spade", "wing_style": "butterfly", "extras": ["iridescent", "motes"]},
    },
    {
        "id": "sun", "name": "Sun Dragon", "archetype": "western", "tier": "common",
        "element": "radiant", "food": ["minecraft:glowstone_dust", "minecraft:gold_ingot"],
        "health": 52, "scale": 1.25, "move": 0.32,
        "spawn": {"dimension": "overworld", "biome": "overworld", "bright": (12, 15), "weight": 2},
        "palette": {"body": "#c79a2a", "belly": "#ffe89a", "accent": "#ffd24a",
                     "membrane": "#e0b03a", "horn": "#fff6d0", "eye": "#ffffdf"},
        "features": {"neck": 4, "horns": "crown", "spines": {"n": 12, "style": "spike", "sz": 1.0},
                      "tail_tip": "spade", "wing_style": "membrane", "extras": ["radiant_crown", "rays"]},
    },
    {
        "id": "shadow", "name": "Shadow Dragon", "archetype": "western", "tier": "common",
        "element": "shadow", "food": ["minecraft:black_dye", "minecraft:cooked_beef"],
        "health": 50, "scale": 1.2, "move": 0.34,
        "spawn": {"dimension": "overworld", "biome": "overworld", "bright": (0, 4), "weight": 2},
        "palette": {"body": "#1a1820", "belly": "#3a3548", "accent": "#6a5a8a",
                     "membrane": "#2a2535", "horn": "#0a0810", "eye": "#a07aff"},
        "features": {"neck": 4, "horns": "swept", "spines": {"n": 12, "style": "spike", "sz": 1.0},
                      "tail_tip": "spade", "wing_style": "tattered", "extras": ["smoke", "umbra"]},
    },
]

# sanity: unique ids
_ids = [d["id"] for d in DRAGONS]
assert len(_ids) == len(set(_ids)), "duplicate dragon id"
