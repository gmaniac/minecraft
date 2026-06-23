#!/usr/bin/env python3
"""Generate all Wildforge vehicle pack files from tools/vehicles_data.py.

Per vehicle: BP entity (rideable, per-category driving group, no fuel, no ride
damage), spawn rule-less (creative egg + crafted item), RP client entity, geo,
texture, a crafted spawn item + icon + recipe, and lang. Plus shared vehicle
animation (wheel/prop/rotor spin) and the script data table.
"""
import json
import os
from vehicles_data import VEHICLES
from colors import HEX, ORIGINAL
from mclib.vehiclebuild import build
from mclib.dragonbuild import pack_and_paint
from mclib.texture import Tex, hex_rgba, shade

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BP = os.path.join(ROOT, "Wildforge_BP")
RP = os.path.join(ROOT, "Wildforge_RP")

# moving-part animations attached per plan
PLAN_ANIMS = {
    "car": ["wheels"], "bus": ["wheels"], "bike": ["wheels"],
    "plane": ["wheels", "prop"], "jet": [], "heli": ["rotor"], "glider": [], "balloon": [],
    "boat": [], "jetski": [], "sub": ["prop"], "pontoon": [],
}


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


def seats(v):
    scale = v["scale"]
    sy = round(1.0 * scale, 2)
    out = [{"position": [0.0, sy, round(-1.5 + i * 1.4, 2)], "lock_rider_rotation": 181}
           for i in range(v["seats"])]
    return out


def drive_group(v):
    cat = v["category"]
    g = {"minecraft:input_air_controlled": {"strafe_speed_modifier": 1.0,
                                            "backwards_movement_modifier": 0.55},
         "minecraft:flying_speed": {"value": v["speed"]},
         "minecraft:damage_sensor": {"triggers": {"cause": "fall", "deals_damage": "no"}}}
    if cat == "land":
        g["minecraft:physics"] = {"has_gravity": True, "has_collision": True}
        g["minecraft:jump.static"] = {}
    else:  # air, water — hover/free control, vertical via jump/sneak
        g["minecraft:physics"] = {"has_gravity": False, "has_collision": True}
        g["minecraft:vertical_movement_action"] = {"vertical_velocity": 0.7}
    return g


def bp_entity(v):
    i = v["id"]
    ident = f"wf:{i}"
    cat = v["category"]
    comps = {
        "minecraft:type_family": {"family": ["wf_vehicle", i, cat]},
        "minecraft:collision_box": {"width": round(1.4 * v["scale"], 2),
                                    "height": round(1.2 * v["scale"], 2)},
        "minecraft:scale": {"value": v["scale"]},
        "minecraft:health": {"value": v["health"], "max": v["health"]},
        "minecraft:physics": {"has_gravity": True, "has_collision": True},
        "minecraft:knockback_resistance": {"value": 1.0},
        "minecraft:movement": {"value": 0.1},
        "minecraft:navigation.walk": {"can_path_over_water": True, "avoid_water": cat == "land"},
        "minecraft:movement.basic": {}, "minecraft:jump.static": {},
        "minecraft:pushable": {"is_pushable": False, "is_pushable_by_piston": False},
        "minecraft:persistent": {}, "minecraft:nameable": {},
        "minecraft:damage_sensor": {"triggers": {"cause": "fall", "deals_damage": "no"}},
        "minecraft:rideable": {
            "seat_count": v["seats"], "controlling_seat": 0, "family_types": ["player"],
            "interact_text": "action.interact.ride.minecart", "pull_in_entities": False,
            "seats": seats(v), "on_rider_enter_event": "wf:drive",
            "on_rider_exit_event": "wf:park"},
    }
    if cat == "water":
        comps["minecraft:behavior.float"] = {"priority": 0}
    return {"format_version": "1.21.90", "minecraft:entity": {
        "description": {"identifier": ident, "is_spawnable": True, "is_summonable": True,
                        "is_experimental": False,
                        "properties": {"wf:color": {"type": "int", "range": [0, ORIGINAL],
                                                    "default": ORIGINAL, "client_sync": True}}},
        "component_groups": {f"wf:{i}_drive": drive_group(v)},
        "components": comps,
        "events": {"wf:drive": {"add": {"component_groups": [f"wf:{i}_drive"]}},
                   "wf:park": {"remove": {"component_groups": [f"wf:{i}_drive"]}}}}}


def rp_entity(v):
    i = v["id"]
    anims = {"base": "animation.wf_vehicle.base"}
    animate = []
    for a in PLAN_ANIMS[v["plan"]]:
        anims[a] = f"animation.wf_vehicle.{a}"
        animate.append(a)
    textures = {str(idx): f"textures/entity/wf_{i}_c{idx}" for idx in range(len(HEX))}
    textures[str(ORIGINAL)] = f"textures/entity/wf_{i}"
    textures["default"] = f"textures/entity/wf_{i}"
    return {"format_version": "1.10.0", "minecraft:client_entity": {"description": {
        "identifier": f"wf:{i}", "materials": {"default": "entity_alphatest"},
        "textures": textures,
        "geometry": {"default": f"geometry.wf_{i}"},
        "animations": anims, "scripts": {"animate": animate},
        "render_controllers": ["controller.render.wf_vehicle_tint"],
        "spawn_egg": {"base_color": v["palette"]["body"],
                      "overlay_color": v["palette"]["accent"]}}}}


def tint_render_controller():
    skins = [f"Texture.{idx}" for idx in range(len(HEX))] + [f"Texture.{ORIGINAL}"]
    return {"format_version": "1.10.0", "render_controllers": {
        "controller.render.wf_vehicle_tint": {
            "geometry": "Geometry.default", "materials": [{"*": "Material.default"}],
            "arrays": {"textures": {"Array.skins": skins}},
            "textures": ["Array.skins[q.property('wf:color')]"]}}}


def item_json(v):
    return {"format_version": "1.21.10", "minecraft:item": {
        "description": {"identifier": f"wf:{v['id']}_item",
                        "menu_category": {"category": "equipment"}},
        "components": {"minecraft:icon": f"wf_{v['id']}_item",
                       "minecraft:max_stack_size": 16,
                       "minecraft:display_name": {"value": v["name"]}}}}


def recipe_json(v):
    c = v["craft"]
    return {"format_version": "1.20.10", "minecraft:recipe_shapeless": {
        "description": {"identifier": f"wf:{v['id']}_item"},
        "tags": ["crafting_table"],
        "ingredients": [{"item": c}, {"item": c}, {"item": c}, {"item": c},
                        {"item": "minecraft:redstone"}, {"item": "minecraft:leather"}],
        "result": {"item": f"wf:{v['id']}_item", "count": 1}}}


def item_icon(v):
    t = Tex(32, 32)
    body = hex_rgba(v["palette"]["body"])
    acc = hex_rgba(v["palette"]["accent"])
    glass = hex_rgba(v["palette"]["glass"])
    t.rect(4, 12, 24, 10, body)            # hull
    t.rect(8, 8, 16, 6, glass)             # cabin
    t.rect(6, 21, 4, 4, hex_rgba(v["palette"]["dark"]))   # wheel
    t.rect(22, 21, 4, 4, hex_rgba(v["palette"]["dark"]))
    t.rect(4, 14, 24, 1, shade(acc, 1.0))  # stripe
    return t


def animations():
    return {"format_version": "1.8.0", "animations": {
        "animation.wf_vehicle.base": {"loop": True, "bones": {}},
        "animation.wf_vehicle.wheels": {"loop": True,
            "anim_time_update": "q.modified_distance_moved", "bones": {
                "wheel_fl": {"rotation": ["q.anim_time*-360", 0, 0]},
                "wheel_fr": {"rotation": ["q.anim_time*-360", 0, 0]},
                "wheel_bl": {"rotation": ["q.anim_time*-360", 0, 0]},
                "wheel_br": {"rotation": ["q.anim_time*-360", 0, 0]},
                "wheel_f": {"rotation": ["q.anim_time*-360", 0, 0]},
                "wheel_b": {"rotation": ["q.anim_time*-360", 0, 0]}}},
        "animation.wf_vehicle.prop": {"loop": True, "bones": {
            "prop": {"rotation": [0, 0, "q.life_time*2400"]}}},
        "animation.wf_vehicle.rotor": {"loop": True, "bones": {
            "rotor": {"rotation": [0, "q.life_time*1800", 0]},
            "rotor_t": {"rotation": ["q.life_time*2000", 0, 0]}}}}}


def script_data():
    items = {f"wf:{v['id']}_item": f"wf:{v['id']}" for v in VEHICLES}
    from colors import DYE_INDEX
    return ("// AUTO-GENERATED by tools/vehiclegen.py — do not edit by hand.\n"
            f"export const VEHICLE_ITEM = {json.dumps(items)};\n"
            f"export const DYE_INDEX = {json.dumps(DYE_INDEX)};\n")


def lang_merge(lines):
    path = os.path.join(RP, "texts", "en_US.lang")
    keys = {ln.split("=", 1)[0] for ln in lines if "=" in ln}
    existing = []
    if os.path.exists(path):
        with open(path) as f:
            for ln in f.read().splitlines():
                k = ln.split("=", 1)[0] if "=" in ln else None
                if k in keys or ln.strip() == "## Vehicles":
                    continue
                existing.append(ln)
    with open(path, "w") as f:
        f.write("\n".join(existing).rstrip() + "\n\n## Vehicles\n" + "\n".join(lines) + "\n")


def main():
    ent = ensure(BP, "entities")
    rpe = ensure(RP, "entity")
    mdl = ensure(RP, "models", "entity")
    tex = ensure(RP, "textures", "entity")
    itx = ensure(RP, "textures", "items")
    itm = ensure(BP, "items")
    rec = ensure(BP, "recipes")
    anim = ensure(RP, "animations")
    ensure(BP, "scripts", "vehicles")

    lang = []
    tex_data = {}
    for v in VEHICLES:
        i = v["id"]
        g = build(v)
        pack_and_paint(g, v["palette"]).save(os.path.join(tex, f"wf_{i}.png"))
        for idx, hexc in enumerate(HEX):     # body-tinted color variants
            pack_and_paint(g, {**v["palette"], "body": hexc}).save(
                os.path.join(tex, f"wf_{i}_c{idx}.png"))
        g.save(os.path.join(mdl, f"wf_{i}.geo.json"))
        dump(os.path.join(ent, f"{i}.json"), bp_entity(v))
        dump(os.path.join(rpe, f"{i}.entity.json"), rp_entity(v))
        dump(os.path.join(itm, f"{i}_item.json"), item_json(v))
        dump(os.path.join(rec, f"{i}_item.json"), recipe_json(v))
        item_icon(v).save(os.path.join(itx, f"wf_{i}_item.png"))
        tex_data[f"wf_{i}_item"] = {"textures": f"textures/items/wf_{i}_item"}
        lang.append(f"entity.wf:{i}.name={v['name']}")
        lang.append(f"item.spawn_egg.entity.wf:{i}.name=Spawn {v['name']}")
        lang.append(f"item.wf:{i}_item.name={v['name']}")

    merge_atlas(os.path.join(RP, "textures", "item_texture.json"), "atlas.items", tex_data)
    dump(os.path.join(anim, "wf_vehicle.animation.json"), animations())
    ensure(RP, "render_controllers")
    dump(os.path.join(RP, "render_controllers", "wf_vehicle.render.json"),
         tint_render_controller())
    with open(os.path.join(BP, "scripts", "vehicles", "data.js"), "w") as f:
        f.write(script_data())
    lang_merge(lang)
    print(f"generated {len(VEHICLES)} vehicles")


if __name__ == "__main__":
    main()
