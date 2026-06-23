"""Prefab house blueprints — generated as sparse [x, y, z, block] placements.

Local frame: x = width (left→right), z = depth (front→back, z=0 is the door side),
y = up (y=0 is the floor). The placer script rotates these around the player on use.
Built from Wildforge material blocks + a vanilla glowstone light.
"""

CONFIGS = {
    "modern_house": dict(w=11, d=9, h=5, roof="flat", floor="wf:hardwood_floor",
                          wall="wf:plaster_white", roof_b="wf:grey_shingle",
                          trim="wf:plaster_charcoal", glass="wf:clear_glass"),
    "cozy_cottage": dict(w=9, d=7, h=4, roof="hip", floor="wf:hardwood_floor",
                         wall="wf:cedar_siding", roof_b="wf:red_shingle", trim="wf:oak_trim",
                         glass="wf:clear_glass"),
    "cabin": dict(w=9, d=9, h=4, roof="hip", floor="wf:pine_planks", wall="wf:walnut_planks",
                  roof_b="wf:wood_shingle", trim="wf:ebony_beam", glass="wf:clear_glass"),
    "mansion": dict(w=13, d=11, h=7, roof="hip", floor="wf:marble", wall="wf:plaster_white",
                    roof_b="wf:slate_shingle", trim="wf:oak_trim", glass="wf:clear_glass",
                    mid=[4]),
    "tower": dict(w=7, d=7, h=11, roof="hip", floor="wf:bluestone", wall="wf:bluestone",
                  roof_b="wf:slate_shingle", trim="wf:grey_brick", glass="wf:clear_glass",
                  mid=[4, 8]),
    "barn": dict(w=13, d=9, h=6, roof="hip", floor="wf:hardwood_floor", wall="wf:red_brick",
                 roof_b="wf:wood_shingle", trim="wf:ebony_beam", glass="wf:clear_glass"),
    "shop": dict(w=11, d=7, h=5, roof="flat", floor="wf:ceramic_tile", wall="wf:plaster_grey",
                 roof_b="wf:grey_shingle", trim="wf:white_trim", glass="wf:clear_glass",
                 shopfront=True),
    "starter_base": dict(w=7, d=7, h=4, roof="hip", floor="wf:ashwood_planks",
                         wall="wf:ashwood_planks", roof_b="wf:grey_shingle", trim="wf:oak_trim",
                         glass="wf:clear_glass"),
}


def build(cfg_id):
    c = CONFIGS[cfg_id]
    w, d, h = c["w"], c["d"], c["h"]
    out = []
    cx = w // 2

    def put(x, y, z, b):
        out.append([x, y, z, b])

    # floor + extra interior floors
    floors = [0] + c.get("mid", [])
    for fy in floors:
        for x in range(w):
            for z in range(d):
                put(x, fy, z, c["floor"])

    # walls
    for y in range(1, h):
        for x in range(w):
            for z in range(d):
                if not (x in (0, w - 1) or z in (0, d - 1)):
                    continue
                # door opening (front, center, 2 high)
                if z == 0 and x == cx and y in (1, 2):
                    continue
                # windows
                is_window = (y == 2 and x not in (0, w - 1) and z not in (0, d - 1) is False
                             and (x % 3 == 0 or z % 3 == 0) and not (z == 0 and abs(x - cx) <= 1))
                if c.get("shopfront") and z == 0 and y in (2, 3) and 1 <= x <= w - 2 and x != cx:
                    put(x, y, z, c["glass"])
                elif is_window:
                    put(x, y, z, c["glass"])
                else:
                    put(x, y, z, c["wall"])

    # corner trim posts
    for (x, z) in ((0, 0), (0, d - 1), (w - 1, 0), (w - 1, d - 1)):
        for y in range(1, h):
            put(x, y, z, c["trim"])

    # roof
    if c["roof"] == "flat":
        for x in range(w):
            for z in range(d):
                put(x, h, z, c["roof_b"])
        for x in range(w):                       # parapet
            put(x, h + 1, 0, c["trim"]); put(x, h + 1, d - 1, c["trim"])
        for z in range(d):
            put(0, h + 1, z, c["trim"]); put(w - 1, h + 1, z, c["trim"])
    else:  # hip
        lvl = 0
        while True:
            x0, x1, z0, z1 = lvl, w - 1 - lvl, lvl, d - 1 - lvl
            y = h + lvl
            if x0 > x1 or z0 > z1:
                break
            if x0 == x1 or z0 == z1:             # ridge cap — fill solid
                for x in range(x0, x1 + 1):
                    for z in range(z0, z1 + 1):
                        put(x, y, z, c["roof_b"])
                break
            for x in range(x0, x1 + 1):
                put(x, y, z0, c["roof_b"]); put(x, y, z1, c["roof_b"])
            for z in range(z0, z1 + 1):
                put(x0, y, z, c["roof_b"]); put(x1, y, z, c["roof_b"])
            lvl += 1

    # ceiling light
    put(cx, h - 1, d // 2, "minecraft:glowstone")
    return out
