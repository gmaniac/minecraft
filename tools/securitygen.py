#!/usr/bin/env python3
"""Generate Wildforge Security: 4 active device entities + 7 blocks + keycard item.

Active devices are placed from crafted items / spawn eggs and ticked by the script
(sensor alarm, tripwire, auto turret, lethal laser) with owner-configurable targeting.
Blocks are interact-driven (camera/monitor/door/keypad/floodlight/siren/hub).
"""
import json
import os
from security_data import ACTIVE, BLOCKS, KEYCARD
from mclib.securitybuild import build_device, build_block
from mclib.dragonbuild import pack_and_paint
from mclib.texture import Tex, hex_rgba, shade

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


def device_bp(a):
    ident = f"wf:{a['id']}"
    # is_spawnable False -> no creative "Spawn …" egg; the device is placed from its
    # crafted item only (it's a gadget, not a creature).
    return {"format_version": "1.21.90", "minecraft:entity": {
        "description": {"identifier": ident, "is_spawnable": False, "is_summonable": True,
                        "is_experimental": False},
        "components": {
            "minecraft:type_family": {"family": ["wf_security", "wf_security_active", a["id"],
                                                 f"kind_{a['kind']}"]},
            "minecraft:collision_box": {"width": round(0.8 * a["scale"], 2),
                                        "height": round(0.9 * a["scale"], 2)},
            "minecraft:scale": {"value": a["scale"]},
            "minecraft:health": {"value": a["health"], "max": a["health"]},
            "minecraft:physics": {"has_gravity": True, "has_collision": True},
            "minecraft:knockback_resistance": {"value": 1.0},
            "minecraft:pushable": {"is_pushable": False, "is_pushable_by_piston": False},
            "minecraft:persistent": {}, "minecraft:nameable": {},
            "minecraft:damage_sensor": {"triggers": {"cause": "fall", "deals_damage": "no"}}},
        "events": {}}}


def device_rp(a):
    return {"format_version": "1.10.0", "minecraft:client_entity": {"description": {
        "identifier": f"wf:{a['id']}", "materials": {"default": "entity_alphatest"},
        "textures": {"default": f"textures/entity/wf_{a['id']}"},
        "geometry": {"default": f"geometry.wf_{a['kind']}_dev"},
        "render_controllers": ["controller.render.wf_default"],
        "spawn_egg": {"base_color": a["palette"]["body"], "overlay_color": a["palette"]["accent"]}}}}


def block_json(blk):
    bid = f"wf:{blk['id']}"
    short = f"wf_{blk['id']}"
    h = blk.get("h", 16)
    comps = {
        "minecraft:material_instances": {"*": {"texture": short, "render_method": "alpha_test"}},
        "minecraft:collision_box": {"origin": [-7, 0, -7], "size": [14, h, 14]},
        "minecraft:selection_box": {"origin": [-7, 0, -7], "size": [14, h, 14]},
        "minecraft:destructible_by_mining": {"seconds_to_destroy": 1.5},
        "minecraft:destructible_by_explosion": {"explosion_resistance": 6},
    }
    if blk.get("geo"):
        comps["minecraft:geometry"] = f"geometry.wf_secblk_{blk['geo']}"
    if blk.get("light"):
        comps["minecraft:light_emission"] = blk["light"]
    if blk.get("component"):
        comps["minecraft:custom_components"] = [blk["component"]]
    desc = {"identifier": bid, "menu_category": {"category": "items"}}
    block = {"description": desc, "components": comps}
    perms = []
    if blk.get("facing"):
        desc["traits"] = {"minecraft:placement_direction": {
            "enabled_states": ["minecraft:cardinal_direction"], "y_rotation_offset": 180}}
        perms += [{"condition": f"q.block_state('minecraft:cardinal_direction') == '{n}'",
                   "components": {"minecraft:transformation": {"rotation": [0, deg, 0]}}}
                  for n, deg in CARDINALS]
    if blk.get("door"):
        desc["states"] = {"wf:open": [False, True]}
        perms.append({"condition": "q.block_state('wf:open') == true", "components": {
            "minecraft:geometry": "geometry.wf_secblk_door_open",
            "minecraft:collision_box": {"origin": [6, 0, -3], "size": [2, 16, 4]}}})
    if perms:
        block["permutations"] = perms
    return {"format_version": "1.21.90", "minecraft:block": block}


def simple_item(ident, name, icon_short):
    return {"format_version": "1.21.10", "minecraft:item": {
        "description": {"identifier": ident, "menu_category": {"category": "items"}},
        "components": {"minecraft:icon": icon_short, "minecraft:max_stack_size": 16,
                       "minecraft:display_name": {"value": name}}}}


def device_recipe(ident, accent_item="minecraft:redstone"):
    return {"format_version": "1.20.10", "minecraft:recipe_shapeless": {
        "description": {"identifier": ident}, "tags": ["crafting_table"],
        "ingredients": [{"item": "minecraft:iron_ingot"}, {"item": "minecraft:iron_ingot"},
                        {"item": accent_item}, {"item": "minecraft:redstone"},
                        {"item": "minecraft:glass"}],
        "result": {"item": ident, "count": 1}}}


def block_recipe(bid):
    return {"format_version": "1.20.10", "minecraft:recipe_shapeless": {
        "description": {"identifier": bid}, "tags": ["crafting_table"],
        "ingredients": [{"item": "minecraft:iron_ingot"}, {"item": "minecraft:redstone"},
                        {"item": "minecraft:glass"}, {"item": "minecraft:copper_ingot"}],
        "result": {"item": bid, "count": 1}}}


def keycard_recipe():
    return {"format_version": "1.20.10", "minecraft:recipe_shapeless": {
        "description": {"identifier": "wf:keycard"}, "tags": ["crafting_table"],
        "ingredients": [{"item": "minecraft:iron_nugget"}, {"item": "minecraft:redstone"},
                        {"item": "minecraft:paper"}],
        "result": {"item": "wf:keycard", "count": 1}}}


def icon(palette, kind="dev"):
    t = Tex(32, 32)
    body = hex_rgba(palette.get("body", "#3a3f44"))
    acc = hex_rgba(palette.get("accent", "#e0432a"))
    t.rect(8, 8, 16, 16, body)
    t.rect(12, 12, 8, 8, hex_rgba(palette.get("glass", "#1aa0e0")))
    t.rect(14, 5, 4, 4, acc)
    return t


def keycard_icon():
    t = Tex(32, 32)
    t.rect(7, 11, 18, 11, hex_rgba("#3aa6e6"))
    t.rect(9, 13, 14, 3, hex_rgba("#e8e8ee"))     # magnetic strip
    t.rect(9, 18, 5, 3, hex_rgba("#ffd24a"))      # chip
    return t


def floodlight_texture(palette):
    t = Tex(16, 16)
    base = hex_rgba(palette["body"])
    light = hex_rgba(palette["glass"])
    for j in range(16):
        for i in range(16):
            t.px[i, j] = base
    t.rect(3, 3, 10, 10, light)
    for n in range(16):
        for k in (0, 15):
            t.px[k, n] = hex_rgba(palette["dark"])
            t.px[n, k] = hex_rgba(palette["dark"])
    return t


def beam_particle(ident, size, tinted):
    comps = {
        "minecraft:emitter_rate_instant": {"num_particles": 1},
        "minecraft:emitter_lifetime_once": {"active_time": 0.05},
        "minecraft:particle_lifetime_expression": {"max_lifetime": 0.3},
        "minecraft:particle_initial_speed": 0,
        "minecraft:particle_appearance_billboard": {
            "size": [size, size], "facing_camera_mode": "lookat_xyz",
            "uv": {"texture_width": 16, "texture_height": 16, "uv": [0, 0], "uv_size": [16, 16]}},
    }
    if tinted:
        comps["minecraft:particle_appearance_tinting"] = {
            "color": ["v.color.r", "v.color.g", "v.color.b", 1.0]}
    return {"format_version": "1.10.0", "particle_effect": {
        "description": {"identifier": ident, "basic_render_parameters": {
            "material": "particles_blend", "texture": "textures/particle/wf_dot"}},
        "components": comps}}


def dot_texture():
    # soft radial glow: bright centre fading to transparent edges (a glow point)
    import math
    n = 16
    c = (n - 1) / 2
    t = Tex(n, n)
    for j in range(n):
        for i in range(n):
            d = math.hypot(i - c, j - c) / (c + 0.5)
            a = max(0.0, 1.0 - d)
            a = a * a                      # soft falloff
            t.px[i, j] = (255, 255, 255, int(255 * a))
    return t


def lang_merge(lines, purge=()):
    """Replace the whole ## Security section (purges stale keys), keep other sections.
    `purge` removes specific obsolete keys wherever they sit (e.g. old spawn-egg keys)."""
    path = os.path.join(RP, "texts", "en_US.lang")
    keys = {ln.split("=", 1)[0] for ln in lines if "=" in ln} | set(purge)
    out, skip = [], False
    if os.path.exists(path):
        with open(path) as f:
            for ln in f.read().splitlines():
                s = ln.strip()
                if s == "## Security":
                    skip = True
                    continue
                if skip and s.startswith("## "):
                    skip = False
                if skip:
                    continue
                if (ln.split("=", 1)[0] if "=" in ln else None) in keys:
                    continue
                out.append(ln)
    with open(path, "w") as f:
        f.write("\n".join(out).rstrip() + "\n\n## Security\n" + "\n".join(lines) + "\n")


def main():
    ent = ensure(BP, "entities")
    rpe = ensure(RP, "entity")
    emdl = ensure(RP, "models", "entity")
    etex = ensure(RP, "textures", "entity")
    blk = ensure(BP, "blocks")
    bmdl = ensure(RP, "models", "blocks")
    btex = ensure(RP, "textures", "blocks")
    itm = ensure(BP, "items")
    itx = ensure(RP, "textures", "items")
    rec = ensure(BP, "recipes")
    ensure(BP, "scripts", "security")

    lang = []
    terrain = {}
    item_tex = {}
    device_item = {}
    active_kind = {}

    # device geometries (one per kind, shared)
    for kind in ("sensor", "tripwire", "turret", "laser"):
        build_device(kind).save(os.path.join(emdl, f"wf_{kind}_dev.geo.json"))

    for a in ACTIVE:
        g = build_device(a["kind"])
        pack_and_paint(g, a["palette"]).save(os.path.join(etex, f"wf_{a['id']}.png"))
        dump(os.path.join(ent, f"{a['id']}.json"), device_bp(a))
        dump(os.path.join(rpe, f"{a['id']}.entity.json"), device_rp(a))
        # spawn item
        iid = f"wf:{a['id']}_item"
        dump(os.path.join(itm, f"{a['id']}_item.json"),
             simple_item(iid, a["name"], f"wf_{a['id']}_item"))
        dump(os.path.join(rec, f"{a['id']}_item.json"), device_recipe(iid))
        icon(a["palette"]).save(os.path.join(itx, f"wf_{a['id']}_item.png"))
        item_tex[f"wf_{a['id']}_item"] = {"textures": f"textures/items/wf_{a['id']}_item"}
        device_item[iid] = f"wf:{a['id']}"
        active_kind[f"wf:{a['id']}"] = a["kind"]
        lang.append(f"entity.wf:{a['id']}.name={a['name']}")
        lang.append(f"item.wf:{a['id']}_item.name={a['name']}")

    # block geometries (one per geo kind, shared) + door_open
    seen_geo = set()
    for b in BLOCKS:
        if b.get("geo") and b["geo"] not in seen_geo:
            build_block(b["geo"]).save(os.path.join(bmdl, f"wf_secblk_{b['geo']}.geo.json"))
            seen_geo.add(b["geo"])
    build_block("door_open").save(os.path.join(bmdl, "wf_secblk_door_open.geo.json"))

    block_components = []
    for b in BLOCKS:
        short = f"wf_{b['id']}"
        if b.get("geo"):
            pack_and_paint(build_block(b["geo"]), b["palette"]).save(
                os.path.join(btex, f"{short}.png"))
        else:
            floodlight_texture(b["palette"]).save(os.path.join(btex, f"{short}.png"))
        terrain[short] = {"textures": f"textures/blocks/{short}"}
        dump(os.path.join(blk, f"{b['id']}.json"), block_json(b))
        dump(os.path.join(rec, f"{b['id']}.json"), block_recipe(f"wf:{b['id']}"))
        lang.append(f"tile.wf:{b['id']}.name={b['name']}")
        if b.get("component"):
            block_components.append(b["component"])

    # keycard item
    dump(os.path.join(itm, "keycard.json"), simple_item("wf:keycard", KEYCARD["name"], "wf_keycard"))
    dump(os.path.join(rec, "keycard.json"), keycard_recipe())
    keycard_icon().save(os.path.join(itx, "wf_keycard.png"))
    item_tex["wf_keycard"] = {"textures": "textures/items/wf_keycard"}
    lang.append(f"item.wf:keycard.name={KEYCARD['name']}")

    # custom beam particles (white-hot core + tinted glow) + soft glow texture
    pdir = ensure(RP, "particles")
    dump(os.path.join(pdir, "wf_laser_core.particle.json"),
         beam_particle("wf:laser_core", 0.09, tinted=False))
    dump(os.path.join(pdir, "wf_laser_glow.particle.json"),
         beam_particle("wf:laser_glow", 0.26, tinted=True))
    dot_texture().save(os.path.join(ensure(RP, "textures", "particle"), "wf_dot.png"))

    merge_atlas(os.path.join(RP, "textures", "terrain_texture.json"), "atlas.terrain", terrain)
    merge_atlas(os.path.join(RP, "textures", "item_texture.json"), "atlas.items", item_tex)

    from colors import DYE_INDEX, HEX
    with open(os.path.join(BP, "scripts", "security", "data.js"), "w") as f:
        f.write("// AUTO-GENERATED by tools/securitygen.py — do not edit by hand.\n"
                f"export const ACTIVE_KIND = {json.dumps(active_kind)};\n"
                f"export const DEVICE_ITEM = {json.dumps(device_item)};\n"
                f"export const BLOCK_COMPONENTS = {json.dumps(block_components)};\n"
                f"export const SEC_BLOCKS = {json.dumps(['wf:' + b['id'] for b in BLOCKS])};\n"
                f"export const CAMERA_ID = \"wf:security_camera\";\n"
                f"export const KEYCARD = \"wf:keycard\";\n"
                f"export const DYE_INDEX = {json.dumps(DYE_INDEX)};\n"
                f"export const HEX = {json.dumps(HEX)};\n")
    lang_merge(lang, purge={f"item.spawn_egg.entity.wf:{a['id']}.name" for a in ACTIVE})
    print(f"generated {len(ACTIVE)} active devices + {len(BLOCKS)} blocks + keycard")


if __name__ == "__main__":
    main()
