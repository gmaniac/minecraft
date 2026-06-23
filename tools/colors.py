"""Shared 16-dye color table for recoloring (vehicles + furniture).

Index order matches Minecraft's standard color data values. Index 16 is reserved
by callers to mean "original / undyed".
"""

DYES = [
    ("white", "minecraft:white_dye", "#e9ecec"),
    ("orange", "minecraft:orange_dye", "#e06a1b"),
    ("magenta", "minecraft:magenta_dye", "#bd44b3"),
    ("light_blue", "minecraft:light_blue_dye", "#3aafd9"),
    ("yellow", "minecraft:yellow_dye", "#f8c627"),
    ("lime", "minecraft:lime_dye", "#70b919"),
    ("pink", "minecraft:pink_dye", "#ed8dac"),
    ("gray", "minecraft:gray_dye", "#3e4447"),
    ("light_gray", "minecraft:light_gray_dye", "#8e8e86"),
    ("cyan", "minecraft:cyan_dye", "#158991"),
    ("purple", "minecraft:purple_dye", "#792aac"),
    ("blue", "minecraft:blue_dye", "#35399d"),
    ("brown", "minecraft:brown_dye", "#724728"),
    ("green", "minecraft:green_dye", "#546d1b"),
    ("red", "minecraft:red_dye", "#a52721"),
    ("black", "minecraft:black_dye", "#1a1a1e"),
]

ORIGINAL = 16                      # state/property value meaning "undyed"
DYE_INDEX = {item: i for i, (_, item, _) in enumerate(DYES)}   # dye item -> 0..15
HEX = [h for _, _, h in DYES]
