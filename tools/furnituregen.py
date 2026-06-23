#!/usr/bin/env python3
"""Generate all Wildforge furniture from tools/furniture_data.py.

Per type x style (54 blocks): block JSON (geometry, material_instances,
collision/selection, facing permutations, light, custom_components), block model,
texture, terrain_texture entry, crafting recipe and lang. Plus the invisible
seat entity (BP+RP) and the furniture script data table.
"""
import json
import os
from furniture_data import TYPES, STYLES, CRAFT_COUNT
from colors import HEX, ORIGINAL, DYE_INDEX
from mclib.furniturebuild import build
from mclib.dragonbuild import pack_and_paint
from mclib.geometry import Geometry
from mclib.texture import Tex

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BP = os.path.join(ROOT, "Wildforge_BP")
RP = os.path.join(ROOT, "Wildforge_RP")
CARDINALS = [("north", 0), ("east", 90), ("south", 180), ("west", 270)]


def ensure(*p):
    q = os.path.join(*p)
    os.makedirs(q, exist_ok=True)
    return q


def dump(path, obj):
    with open(path, "w") as f:
        json.dump(obj, f, indent=2)


def merge_atlas(path, name, entries):
    data = {"resource_pack_name": "wildforge", "texture_name": name, "texture_data": {}}
    if os.path.exists(path):
        try:
            with open(path) as f:
                data = json.load(f)
        except Exception:
            pass
    data.setdefault("texture_data", {}).update(entries)
    dump(path, data)


def block_json(t, style_key):
    key = t["key"]
    bid = f"wf:{key}_{style_key}"
    short = f"wf_furn_{key}_{style_key}"
    h = t.get("h", 16)
    comps = {
        "minecraft:geometry": f"geometry.wf_furn_{key}",
        "minecraft:material_instances": {"*": {"texture": short, "render_method": "alpha_test"}},
        "minecraft:collision_box": {"origin": [-7, 0, -7], "size": [14, h, 14]},
        "minecraft:selection_box": {"origin": [-7, 0, -7], "size": [14, h, 14]},
        "minecraft:destructible_by_mining": {"seconds_to_destroy": 1.0},
        "minecraft:destructible_by_explosion": {"explosion_resistance": 1},
    }
    if t.get("light"):
        comps["minecraft:light_emission"] = t["light"]
    custom = []
    if t.get("sit"):
        custom.append("wf:seat")
    if t.get("storage"):
        custom.append("wf:storage")
    if custom:
        comps["minecraft:custom_components"] = custom

    desc = {"identifier": bid, "menu_category": {"category": "construction"},
            "states": {"wf:color": [ORIGINAL] + list(range(len(HEX)))}}
    block = {"description": desc, "components": comps}
    perms = []
    if t.get("facing"):
        desc["traits"] = {"minecraft:placement_direction": {
            "enabled_states": ["minecraft:cardinal_direction"], "y_rotation_offset": 180}}
        perms += [
            {"condition": f"q.block_state('minecraft:cardinal_direction') == '{name}'",
             "components": {"minecraft:transformation": {"rotation": [0, deg, 0]}}}
            for name, deg in CARDINALS]
    # color permutations swap the texture (value ORIGINAL keeps the base material)
    perms += [{"condition": f"q.block_state('wf:color') == {idx}",
               "components": {"minecraft:material_instances":
                              {"*": {"texture": f"{short}_c{idx}", "render_method": "alpha_test"}}}}
              for idx in range(len(HEX))]
    block["permutations"] = perms
    return {"format_version": "1.21.90", "minecraft:block": block}


def recipe_json(t, style_key, material):
    bid = f"wf:{t['key']}_{style_key}"
    n = CRAFT_COUNT.get(t["key"], 4)
    return {"format_version": "1.20.10", "minecraft:recipe_shapeless": {
        "description": {"identifier": bid},
        "tags": ["crafting_table"],
        "ingredients": [{"item": material} for _ in range(n)],
        "result": {"item": bid, "count": 1}}}


def seat_entity_bp():
    return {"format_version": "1.21.90", "minecraft:entity": {
        "description": {"identifier": "wf:seat", "is_spawnable": False, "is_summonable": True,
                        "is_experimental": False},
        "components": {
            "minecraft:type_family": {"family": ["wf_seat"]},
            "minecraft:physics": {"has_gravity": False, "has_collision": False},
            "minecraft:collision_box": {"width": 0.1, "height": 0.1},
            "minecraft:health": {"value": 1, "max": 1},
            "minecraft:damage_sensor": {"triggers": {"cause": "all", "deals_damage": "no"}},
            "minecraft:pushable": {"is_pushable": False, "is_pushable_by_piston": False},
            "minecraft:persistent": {},
            "minecraft:rideable": {"seat_count": 1, "controlling_seat": 0,
                                   "family_types": ["player"], "pull_in_entities": False,
                                   "seats": [{"position": [0, 0, 0], "lock_rider_rotation": 0}]}}}}


def seat_entity_rp():
    return {"format_version": "1.10.0", "minecraft:client_entity": {"description": {
        "identifier": "wf:seat", "materials": {"default": "entity_alphatest"},
        "textures": {"default": "textures/entity/wf_seat"},
        "geometry": {"default": "geometry.wf_seat"},
        "render_controllers": ["controller.render.wf_default"]}}}


def seat_geo():
    g = Geometry("geometry.wf_seat", 16, 16)
    g.bone("root", (0, 0, 0)).cube([-0.05, 0, -0.05], [0.1, 0.1, 0.1], [0, 0])
    g.bounds = [1, 1]
    g.bounds_offset = [0, 0, 0]
    return g


def lang_merge(lines):
    path = os.path.join(RP, "texts", "en_US.lang")
    keys = {ln.split("=", 1)[0] for ln in lines if "=" in ln}
    existing = []
    if os.path.exists(path):
        with open(path) as f:
            for ln in f.read().splitlines():
                k = ln.split("=", 1)[0] if "=" in ln else None
                if k in keys or ln.strip() == "## Furniture":
                    continue
                existing.append(ln)
    with open(path, "w") as f:
        f.write("\n".join(existing).rstrip() + "\n\n## Furniture\n" + "\n".join(lines) + "\n")


def main():
    blk = ensure(BP, "blocks")
    rec = ensure(BP, "recipes")
    mdl = ensure(RP, "models", "blocks")
    tex = ensure(RP, "textures", "blocks")
    ent = ensure(BP, "entities")
    rpe = ensure(RP, "entity")
    emdl = ensure(RP, "models", "entity")
    etex = ensure(RP, "textures", "entity")
    ensure(BP, "scripts", "furniture")

    lang = []
    tex_data = {}
    seat_y = {}
    storage_ids = []
    block_ids = []
    # one model per type (shared across styles)
    for t in TYPES:
        build(t["key"]).save(os.path.join(mdl, f"wf_furn_{t['key']}.geo.json"))

    for t in TYPES:
        g = build(t["key"])
        for sk, s in STYLES.items():
            bid = f"wf:{t['key']}_{sk}"
            short = f"wf_furn_{t['key']}_{sk}"
            pack_and_paint(g, s["palette"]).save(os.path.join(tex, f"{short}.png"))
            tex_data[short] = {"textures": f"textures/blocks/{short}"}
            # upholstery/accent-tinted color variants
            for idx, hexc in enumerate(HEX):
                pal = {**s["palette"], "fabric": hexc, "accent": hexc}
                pack_and_paint(g, pal).save(os.path.join(tex, f"{short}_c{idx}.png"))
                tex_data[f"{short}_c{idx}"] = {"textures": f"textures/blocks/{short}_c{idx}"}
            dump(os.path.join(blk, f"{t['key']}_{sk}.json"), block_json(t, sk))
            dump(os.path.join(rec, f"{t['key']}_{sk}.json"), recipe_json(t, sk, s["material"]))
            lang.append(f"tile.{bid}.name={s['label']} {t['label']}")
            block_ids.append(bid)
            if t.get("sit"):
                seat_y[bid] = t["seat_y"]
            if t.get("storage"):
                storage_ids.append(bid)

    # invisible seat entity
    dump(os.path.join(ent, "seat.json"), seat_entity_bp())
    dump(os.path.join(rpe, "seat.entity.json"), seat_entity_rp())
    seat_geo().save(os.path.join(emdl, "wf_seat.geo.json"))
    Tex(8, 8).save(os.path.join(etex, "wf_seat.png"))   # fully transparent
    lang.append("entity.wf:seat.name=Seat")

    # terrain texture (merged so other domains' entries survive)
    merge_atlas(os.path.join(RP, "textures", "terrain_texture.json"), "atlas.terrain", tex_data)

    # script data
    with open(os.path.join(BP, "scripts", "furniture", "data.js"), "w") as f:
        f.write("// AUTO-GENERATED by tools/furnituregen.py — do not edit by hand.\n"
                f"export const SEAT_Y = {json.dumps(seat_y)};\n"
                f"export const STORAGE = {json.dumps(storage_ids)};\n"
                f"export const FURNITURE_BLOCKS = {json.dumps(block_ids)};\n"
                f"export const DYE_INDEX = {json.dumps(DYE_INDEX)};\n")
    lang_merge(lang)
    print(f"generated {len(TYPES) * len(STYLES)} furniture blocks "
          f"({len(seat_y)} seat types, {len(storage_ids)} storage types)")


if __name__ == "__main__":
    main()
