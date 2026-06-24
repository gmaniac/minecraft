#!/usr/bin/env python3
"""Generate all Wildforge pet pack files from tools/pets_data.py.

Per pet: BP entity (tame/follow/stay/carry/combat/baby/level groups + events),
spawn rule, RP client entity, .geo model, texture, lang. Plus the shared pet
animation set and the script data table consumed by scripts/pets/index.js.
"""
import json
import os
from pets_data import PETS
from mclib.petbuild import build
from mclib.dragonbuild import pack_and_paint

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BP = os.path.join(ROOT, "Wildforge_BP")
RP = os.path.join(ROOT, "Wildforge_RP")
MAXLVL = 5


def ensure(*p):
    q = os.path.join(*p)
    os.makedirs(q, exist_ok=True)
    return q


def dump(path, obj):
    with open(path, "w") as f:
        json.dump(obj, f, indent=2)


def base_attack(p):
    return max(2, round(p["health"] / 5))


def bp_entity(p):
    i = p["id"]
    ident = f"wf:{i}"
    food = p["food"]
    H = p["health"]
    scale = p["scale"]
    combat = p["combat"]
    fly = p["fly"]
    size = p["size"]

    # ---- movement / navigation ----
    if fly:
        nav = {"minecraft:navigation.fly": {"can_path_over_water": True,
                                            "avoid_damage_blocks": True},
               "minecraft:movement.fly": {}, "minecraft:flying_speed": {"value": p["move"]},
               "minecraft:can_fly": {}}
    else:
        nav = {"minecraft:navigation.walk": {"can_path_over_water": True, "avoid_water": True,
                                             "avoid_damage_blocks": True},
               "minecraft:movement.basic": {}, "minecraft:jump.static": {}}

    comps = {
        "minecraft:type_family": {"family": ["wf_pet", i, "mob"]},
        "minecraft:collision_box": {"width": round(0.6 * scale + 0.2, 2),
                                    "height": round(0.6 * scale + 0.2, 2)},
        "minecraft:scale": {"value": scale},
        "minecraft:health": {"value": H, "max": H},
        "minecraft:physics": {}, "minecraft:movement": {"value": p["move"]},
        "minecraft:breathable": {"breathes_air": True, "total_supply": 15},
        "minecraft:nameable": {},
        "minecraft:tameable": {"probability": 0.4, "tame_items": food,
                               "tame_event": {"event": "wf:pet_tame", "target": "self"}},
        "minecraft:behavior.float": {"priority": 0},
        "minecraft:behavior.panic": {"priority": 1, "speed_multiplier": 1.4},
        "minecraft:behavior.tempt": {"priority": 4, "items": food, "speed_multiplier": 1.1},
        "minecraft:behavior.random_stroll": {"priority": 7, "speed_multiplier": 0.8},
        "minecraft:behavior.look_at_player": {"priority": 8, "look_distance": 8},
        "minecraft:behavior.random_look_around": {"priority": 9},
        "minecraft:despawn": {"despawn_from_distance": {}},
    }
    comps.update(nav)

    # ---- groups ----
    tamed = {"minecraft:is_tamed": {}, "minecraft:persistent": {},
             "minecraft:behavior.breed": {"priority": 3, "speed_multiplier": 1.0},
             "minecraft:breedable": {"require_tame": True, "inherit_tamed": True,
                                     "breed_items": food,
                                     "breeds_with": [{"mate_type": ident, "baby_type": ident,
                                                      "breed_event": {"event": "minecraft:entity_born",
                                                                      "target": "baby"}}]}}
    if size == "large":
        tamed["minecraft:rideable"] = {
            "seat_count": 1, "controlling_seat": 0, "family_types": ["player"],
            "interact_text": "action.interact.ride.horse", "pull_in_entities": False,
            "seats": [{"position": [0.0, round(0.9 * scale, 2), 0.0], "lock_rider_rotation": 181}]}

    follow = {"minecraft:behavior.follow_owner": {"priority": 5, "speed_multiplier": 1.1,
                                                  "start_distance": 10, "stop_distance": 3}}
    groups = {f"wf:{i}_tamed": tamed, f"wf:{i}_follow": follow}

    if combat:
        A = base_attack(p)
        groups[f"wf:{i}_combat"] = {
            "minecraft:attack": {"damage": A},
            "minecraft:behavior.nearest_attackable_target": {
                "priority": 4, "must_see": True, "reselect_targets": True,
                "entity_types": [{"filters": {"test": "is_family", "subject": "other",
                                              "value": "monster"},
                                  "max_dist": 12}]},
            "minecraft:behavior.melee_attack": {"priority": 4, "speed_multiplier": 1.3}}

    groups[f"wf:{i}_baby"] = {
        "minecraft:is_baby": {}, "minecraft:scale": {"value": round(scale * 0.5, 2)},
        "minecraft:ageable": {"duration": 1200, "feed_items": food,
                              "grow_up": {"event": "wf:grow_up", "target": "self"}}}

    if size == "small":
        groups[f"wf:{i}_carried"] = {"minecraft:physics": {"has_gravity": False,
                                                           "has_collision": False},
                                     "minecraft:is_tamed": {}}

    # level groups
    for n in range(2, MAXLVL + 1):
        grp = {"minecraft:health": {"value": round(H * (1 + 0.22 * (n - 1))),
                                    "max": round(H * (1 + 0.22 * (n - 1)))}}
        if combat:
            grp["minecraft:attack"] = {"damage": base_attack(p) + (n - 1)}
        groups[f"wf:{i}_lvl_{n}"] = grp

    # ---- events ----
    tame_add = [f"wf:{i}_tamed", f"wf:{i}_follow"] + ([f"wf:{i}_combat"] if combat else [])
    lvl_all = [f"wf:{i}_lvl_{n}" for n in range(2, MAXLVL + 1)]
    events = {
        "wf:pet_tame": {"add": {"component_groups": tame_add}},
        "minecraft:entity_born": {"add": {"component_groups": [f"wf:{i}_baby"] + tame_add}},
        "wf:set_baby": {"add": {"component_groups": [f"wf:{i}_baby"]}},
        "wf:grow_up": {"remove": {"component_groups": [f"wf:{i}_baby"]}},
        "wf:stay": {"remove": {"component_groups": [f"wf:{i}_follow"]}},
        "wf:follow": {"add": {"component_groups": [f"wf:{i}_follow"]}},
        "wf:carry_on": ({"add": {"component_groups": [f"wf:{i}_carried"]}}
                        if size == "small" else {}),
        "wf:carry_off": ({"remove": {"component_groups": [f"wf:{i}_carried"]}}
                         if size == "small" else {}),
        "minecraft:entity_spawned": {"randomize": [
            {"weight": 80, "remove": {"component_groups": [f"wf:{i}_baby"]}},
            {"weight": 20, "add": {"component_groups": [f"wf:{i}_baby"]}}]},
    }
    if combat:
        events["wf:mode_passive"] = {"remove": {"component_groups": [f"wf:{i}_combat"]}}
        events["wf:mode_defend"] = {"add": {"component_groups": [f"wf:{i}_combat"]}}
    for n in range(2, MAXLVL + 1):
        events[f"wf:setlvl_{n}"] = {"remove": {"component_groups": lvl_all},
                                    "add": {"component_groups": [f"wf:{i}_lvl_{n}"]}}
    events["wf:setlvl_1"] = {"remove": {"component_groups": lvl_all}}

    return {"format_version": "1.21.90", "minecraft:entity": {
        "description": {"identifier": ident, "is_spawnable": True, "is_summonable": True,
                        "is_experimental": False},
        "component_groups": groups, "components": comps, "events": events}}


def spawn_rule(p):
    s = p["spawn"]
    return {"format_version": "1.8.0", "minecraft:spawn_rules": {
        "description": {"identifier": f"wf:{p['id']}", "population_control": "animal"},
        "conditions": [{
            "minecraft:spawns_on_surface": {},
            "minecraft:weight": {"default": s["weight"]},
            "minecraft:brightness_filter": {"min": s["bright"][0], "max": s["bright"][1],
                                            "adjust_for_weather": False},
            "minecraft:herd": {"min_size": 1, "max_size": 3},
            "minecraft:biome_filter": {"test": "has_biome_tag", "operator": "==",
                                       "value": s["biome"]},
            "minecraft:difficulty_filter": {"min": "peaceful", "max": "hard"}}]}}


def rp_entity(p):
    i = p["id"]
    anims = {"idle": "animation.wf_pet.idle", "walk": "animation.wf_pet.walk"}
    animate = [{"idle": "q.modified_move_speed <= 0.05"}, {"walk": "q.modified_move_speed > 0.05"}]
    if p["fly"]:
        anims["fly"] = "animation.wf_pet.fly"
        animate = [{"idle": "q.is_on_ground && q.modified_move_speed <= 0.05"},
                   {"walk": "q.is_on_ground && q.modified_move_speed > 0.05"},
                   {"fly": "!q.is_on_ground"}]
    return {"format_version": "1.10.0", "minecraft:client_entity": {"description": {
        "identifier": f"wf:{i}", "materials": {"default": "entity_alphatest"},
        "textures": {"default": f"textures/entity/wf_{i}"},
        "geometry": {"default": f"geometry.wf_{i}"},
        "animations": anims, "scripts": {"animate": animate},
        "render_controllers": ["controller.render.wf_default"],
        "spawn_egg": {"base_color": p["palette"]["body"], "overlay_color": p["palette"]["accent"]}}}}


def animations():
    return {"format_version": "1.8.0", "animations": {
        "animation.wf_pet.idle": {"loop": True, "bones": {
            "head": {"rotation": ["math.sin(q.life_time*70)*4", "math.cos(q.life_time*55)*5", 0]},
            "tail": {"rotation": [0, "math.sin(q.life_time*120)*16", 0]},
            "ear_l": {"rotation": ["math.sin(q.life_time*90)*6", 0, 0]},
            "ear_r": {"rotation": ["math.sin(q.life_time*90+40)*6", 0, 0]}}},
        "animation.wf_pet.walk": {"loop": True, "anim_time_update": "q.modified_distance_moved",
            "bones": {
                "leg_fl": {"rotation": ["math.cos(q.anim_time*42)*40", 0, 0]},
                "leg_fr": {"rotation": ["math.cos(q.anim_time*42+180)*40", 0, 0]},
                "leg_bl": {"rotation": ["math.cos(q.anim_time*42+180)*40", 0, 0]},
                "leg_br": {"rotation": ["math.cos(q.anim_time*42)*40", 0, 0]},
                "tail": {"rotation": [0, "math.cos(q.anim_time*42)*10", 0]}}},
        "animation.wf_pet.fly": {"loop": True, "bones": {
            "wing_l": {"rotation": [0, 0, "math.sin(q.life_time*240)*48-8"]},
            "wing_r": {"rotation": [0, 0, "-math.sin(q.life_time*240)*48+8"]},
            "body": {"position": [0, "math.sin(q.life_time*240)*0.8", 0]}}}}}


def script_data():
    sizes = {f"wf:{p['id']}": p["size"] for p in PETS}
    combat = {f"wf:{p['id']}": bool(p["combat"]) for p in PETS}
    foods = {f"wf:{p['id']}": p["food"] for p in PETS}
    names = {f"wf:{p['id']}": p["name"] for p in PETS}
    js = ("// AUTO-GENERATED by tools/petgen.py — do not edit by hand.\n"
          f"export const PET_SIZE = {json.dumps(sizes)};\n"
          f"export const PET_COMBAT = {json.dumps(combat)};\n"
          f"export const PET_FOOD = {json.dumps(foods)};\n"
          f"export const PET_NAME = {json.dumps(names)};\n"
          f"export const MAXLVL = {MAXLVL};\n")
    return js


def lang_merge(lines_to_add):
    path = os.path.join(RP, "texts", "en_US.lang")
    keys = {ln.split("=", 1)[0] for ln in lines_to_add if "=" in ln}
    existing = []
    if os.path.exists(path):
        with open(path) as f:
            for ln in f.read().splitlines():
                k = ln.split("=", 1)[0] if "=" in ln else None
                if k in keys:
                    continue
                if ln.strip() == "## Pets":
                    continue
                existing.append(ln)
    with open(path, "w") as f:
        f.write("\n".join(existing).rstrip() + "\n\n## Pets\n" + "\n".join(lines_to_add) + "\n")


def main():
    ent = ensure(BP, "entities")
    sr = ensure(BP, "spawn_rules")
    rpe = ensure(RP, "entity")
    mdl = ensure(RP, "models", "entity")
    tex = ensure(RP, "textures", "entity")
    anim = ensure(RP, "animations")
    ensure(BP, "scripts", "pets")

    lang = []
    for p in PETS:
        i = p["id"]
        g = build(p)
        pack_and_paint(g, p["palette"], "fur").save(os.path.join(tex, f"wf_{i}.png"))
        g.save(os.path.join(mdl, f"wf_{i}.geo.json"))
        dump(os.path.join(ent, f"{i}.json"), bp_entity(p))
        dump(os.path.join(sr, f"{i}.json"), spawn_rule(p))
        dump(os.path.join(rpe, f"{i}.entity.json"), rp_entity(p))
        lang.append(f"entity.wf:{i}.name={p['name']}")
        lang.append(f"item.spawn_egg.entity.wf:{i}.name=Spawn {p['name']}")

    dump(os.path.join(anim, "wf_pet.animation.json"), animations())
    with open(os.path.join(BP, "scripts", "pets", "data.js"), "w") as f:
        f.write(script_data())
    lang_merge(lang)
    print(f"generated {len(PETS)} pets")


if __name__ == "__main__":
    main()
