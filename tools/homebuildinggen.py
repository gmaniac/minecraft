#!/usr/bin/env python3
"""Generate Wildforge HomeBuilding: 35 material blocks + 8 prefab placers.

Materials: full-cube custom blocks + 16x16 textures + recipes + lang, merged into
terrain_texture.json. Prefabs: a crafted placer item per house (+ icon merged into
item_texture.json) and a blueprint table the placer script consumes.
"""
import json
import os
from homebuilding_data import MATERIALS, PREFABS, CRAFT
from mclib.matbuild import build as build_mat
from mclib.texture import Tex, hex_rgba
from prefabs import build as build_prefab

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BP = os.path.join(ROOT, "Wildforge_BP")
RP = os.path.join(ROOT, "Wildforge_RP")


def ensure(*p):
    q = os.path.join(*p)
    os.makedirs(q, exist_ok=True)
    return q


def dump(path, obj):
    with open(path, "w") as f:
        json.dump(obj, f, indent=2)


def merge_atlas(path, name, entries):
    """Read-modify-write a texture atlas so domains don't clobber each other."""
    data = {"resource_pack_name": "wildforge", "texture_name": name, "texture_data": {}}
    if os.path.exists(path):
        try:
            with open(path) as f:
                data = json.load(f)
        except Exception:
            pass
    data.setdefault("texture_data", {}).update(entries)
    dump(path, data)


def block_json(m):
    bid = f"wf:{m['id']}"
    short = f"wf_{m['id']}"
    render = "blend" if m.get("glass") else "opaque"
    comps = {
        "minecraft:material_instances": {"*": {"texture": short, "render_method": render}},
        "minecraft:destructible_by_mining": {"seconds_to_destroy": 1.2},
        "minecraft:destructible_by_explosion": {"explosion_resistance": 3},
    }
    if m.get("glass"):
        comps["minecraft:light_dampening"] = 0
    return {"format_version": "1.21.90", "minecraft:block": {
        "description": {"identifier": bid, "menu_category": {"category": "construction"}},
        "components": comps}}


def recipe_json(m):
    bid = f"wf:{m['id']}"
    ing = CRAFT.get(m["cat"], "minecraft:oak_planks")
    return {"format_version": "1.20.10", "minecraft:recipe_shapeless": {
        "description": {"identifier": bid}, "tags": ["crafting_table"],
        "ingredients": [{"item": ing}, {"item": ing}, {"item": ing}, {"item": ing}],
        "result": {"item": bid, "count": 4}}}


def placer_item(pf):
    return {"format_version": "1.21.10", "minecraft:item": {
        "description": {"identifier": f"wf:{pf['id']}_placer",
                        "menu_category": {"category": "construction"}},
        "components": {"minecraft:icon": f"wf_{pf['id']}_placer",
                       "minecraft:max_stack_size": 16,
                       "minecraft:display_name": {"value": pf["label"]}}}}


def placer_recipe(pf):
    return {"format_version": "1.20.10", "minecraft:recipe_shapeless": {
        "description": {"identifier": f"wf:{pf['id']}_placer"}, "tags": ["crafting_table"],
        "ingredients": [{"item": "minecraft:oak_planks"}, {"item": "minecraft:oak_planks"},
                        {"item": "minecraft:stone"}, {"item": "minecraft:stone"},
                        {"item": "minecraft:crafting_table"}, {"item": "minecraft:paper"}],
        "result": {"item": f"wf:{pf['id']}_placer", "count": 1}}}


def placer_icon(pf):
    t = Tex(32, 32)
    wall = hex_rgba("#caa46a")
    roof = hex_rgba("#9a3a2a")
    door = hex_rgba("#5a3a1a")
    t.rect(6, 14, 20, 14, wall)            # house body
    for i in range(11):                    # gable roof
        t.rect(6 + i, 14 - i, 20 - 2 * i, 2, roof)
    t.rect(14, 20, 4, 8, door)             # door
    t.rect(9, 17, 3, 3, hex_rgba("#bfe6f0"))
    t.rect(20, 17, 3, 3, hex_rgba("#bfe6f0"))
    return t


def lang_merge(lines):
    path = os.path.join(RP, "texts", "en_US.lang")
    keys = {ln.split("=", 1)[0] for ln in lines if "=" in ln}
    existing = []
    if os.path.exists(path):
        with open(path) as f:
            for ln in f.read().splitlines():
                k = ln.split("=", 1)[0] if "=" in ln else None
                if k in keys or ln.strip() == "## HomeBuilding":
                    continue
                existing.append(ln)
    with open(path, "w") as f:
        f.write("\n".join(existing).rstrip() + "\n\n## HomeBuilding\n" + "\n".join(lines) + "\n")


def main():
    blk = ensure(BP, "blocks")
    rec = ensure(BP, "recipes")
    btex = ensure(RP, "textures", "blocks")
    itm = ensure(BP, "items")
    itx = ensure(RP, "textures", "items")
    ensure(BP, "scripts", "homebuilding")

    lang = []
    terrain = {}
    for m in MATERIALS:
        short = f"wf_{m['id']}"
        build_mat(m).save(os.path.join(btex, f"{short}.png"))
        terrain[short] = {"textures": f"textures/blocks/{short}"}
        dump(os.path.join(blk, f"{m['id']}.json"), block_json(m))
        dump(os.path.join(rec, f"{m['id']}.json"), recipe_json(m))
        lang.append(f"tile.wf:{m['id']}.name={m['label']}")

    item_tex = {}
    prefab_data = {}
    for pf in PREFABS:
        dump(os.path.join(itm, f"{pf['id']}_placer.json"), placer_item(pf))
        dump(os.path.join(rec, f"{pf['id']}_placer.json"), placer_recipe(pf))
        placer_icon(pf).save(os.path.join(itx, f"wf_{pf['id']}_placer.png"))
        item_tex[f"wf_{pf['id']}_placer"] = {"textures": f"textures/items/wf_{pf['id']}_placer"}
        prefab_data[f"wf:{pf['id']}_placer"] = {"name": pf["label"], "blocks": build_prefab(pf["id"])}
        lang.append(f"item.wf:{pf['id']}_placer.name={pf['label']}")

    merge_atlas(os.path.join(RP, "textures", "terrain_texture.json"), "atlas.terrain", terrain)
    merge_atlas(os.path.join(RP, "textures", "item_texture.json"), "atlas.items", item_tex)

    with open(os.path.join(BP, "scripts", "homebuilding", "data.js"), "w") as f:
        f.write("// AUTO-GENERATED by tools/homebuildinggen.py — do not edit by hand.\n"
                f"export const PREFABS = {json.dumps(prefab_data)};\n")
    lang_merge(lang)
    print(f"generated {len(MATERIALS)} materials + {len(PREFABS)} prefabs")


if __name__ == "__main__":
    main()
