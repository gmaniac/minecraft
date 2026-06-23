#!/usr/bin/env python3
"""Generate all Wildforge dragon pack files from tools/dragons_data.py.

Emits, per dragon: BP entity, spawn rule, RP client entity, .geo model, texture,
lang lines, and (for the 17 commons) a matching egg entity/RP/texture. Also writes
the shared dragon animation set, the shared egg model, and the script data table.
"""
import json
import os
from dragons_data import DRAGONS
from mclib.dragonbuild import build, pack_and_paint
from mclib.geometry import Geometry
from mclib.texture import Tex, hex_rgba, shade

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BP = os.path.join(ROOT, "Wildforge_BP")
RP = os.path.join(ROOT, "Wildforge_RP")


def ensure(*parts):
    p = os.path.join(*parts)
    os.makedirs(p, exist_ok=True)
    return p


def dump(path, obj):
    with open(path, "w") as f:
        json.dump(obj, f, indent=2)


# --------------------------------------------------------------------------- #
def collision(scale):
    return {"width": round(1.2 * scale, 2), "height": round(1.3 * scale, 2)}


def bp_entity(d):
    i = d["id"]
    ident = f"wf:{i}"
    common = d["tier"] == "common"
    food = d["food"]
    element = d["element"]
    scale = d["scale"]
    aquatic = element in ("tidal",) or i in ("tidal", "tiamat")
    seats = 2 if d["tier"] == "mythic" else 1

    tamed = {
        "minecraft:is_tamed": {},
        "minecraft:persistent": {},
        "minecraft:behavior.follow_owner": {
            "priority": 5, "speed_multiplier": 1.0, "start_distance": 16, "stop_distance": 5},
        "minecraft:damage_sensor": {"triggers": {"cause": "fall", "deals_damage": "no"}},
        "minecraft:rideable": {
            "seat_count": seats, "controlling_seat": 0, "family_types": ["player"],
            "interact_text": "action.interact.ride.horse", "pull_in_entities": False,
            "seats": [{"position": [0.0, round(1.1 * scale, 2), 0.0], "lock_rider_rotation": 181}]
            + ([{"position": [0.0, round(1.1 * scale, 2), round(1.4 * scale, 2)],
                 "lock_rider_rotation": 181}] if seats > 1 else []),
            "on_rider_enter_event": "wf:start_flying",
            "on_rider_exit_event": "wf:stop_flying"},
    }
    if common:
        tamed["minecraft:breedable"] = {
            "require_tame": True, "inherit_tamed": True, "breed_items": food,
            "breeds_with": [{"mate_type": ident, "baby_type": ident,
                             "breed_event": {"event": "minecraft:entity_born", "target": "baby"}}]}
        tamed["minecraft:behavior.breed"] = {"priority": 3, "speed_multiplier": 1.0}

    flying = {
        "minecraft:physics": {"has_gravity": False, "has_collision": True},
        "minecraft:flying_speed": {"value": round(0.10 + (d["move"] - 0.26) * 0.25, 3)},
        "minecraft:input_air_controlled": {
            "strafe_speed_modifier": 1.0, "backwards_movement_modifier": 0.5},
        "minecraft:vertical_movement_action": {"vertical_velocity": 0.6},
        "minecraft:damage_sensor": {"triggers": {"cause": "fall", "deals_damage": "no"}},
    }

    groups = {f"wf:{i}_tamed": tamed, f"wf:{i}_flying": flying}

    if common:
        groups[f"wf:{i}_baby"] = {
            "minecraft:is_baby": {}, "minecraft:scale": {"value": round(scale * 0.4, 2)},
            "minecraft:collision_box": {"width": round(0.6 * scale, 2),
                                        "height": round(0.7 * scale, 2)},
            "minecraft:tameable": {"probability": 0.0, "tame_items": [],
                                   "tame_event": {"event": "wf:on_tame", "target": "self"}},
            "minecraft:behavior.tempt": {"priority": 10, "items": food},
            "minecraft:ageable": {"duration": 1200, "feed_items": food,
                                  "grow_up": {"event": "wf:grow_up", "target": "self"}},
        }

    comps = {
        "minecraft:type_family": {"family": ["wf_dragon", i, f"el_{element}", "mob"]},
        "minecraft:collision_box": collision(scale),
        "minecraft:scale": {"value": scale},
        "minecraft:health": {"value": d["health"], "max": d["health"]},
        "minecraft:physics": {"has_gravity": True, "has_collision": True},
        "minecraft:knockback_resistance": {"value": 0.6 if common else 0.9},
        "minecraft:movement": {"value": d["move"]},
        "minecraft:navigation.walk": {"can_path_over_water": True, "avoid_water": not aquatic,
                                      "avoid_damage_blocks": True},
        "minecraft:movement.basic": {}, "minecraft:jump.static": {}, "minecraft:can_climb": {},
        "minecraft:breathable": {"breathes_air": True, "breathes_water": aquatic,
                                 "total_supply": 15},
        "minecraft:nameable": {},
        "minecraft:tameable": {"probability": 0.3 if common else 0.2, "tame_items": food,
                               "tame_event": {"event": "wf:on_tame", "target": "self"}},
        "minecraft:behavior.float": {"priority": 0},
        "minecraft:behavior.panic": {"priority": 2, "speed_multiplier": 1.3},
        "minecraft:behavior.tempt": {"priority": 4, "items": food, "speed_multiplier": 1.1,
                                     "can_get_scared": False},
        "minecraft:behavior.random_stroll": {"priority": 7, "speed_multiplier": 0.8},
        "minecraft:behavior.look_at_player": {"priority": 8, "look_distance": 12},
        "minecraft:behavior.random_look_around": {"priority": 9},
    }
    if common:
        comps["minecraft:despawn"] = {"despawn_from_distance": {}}
    else:
        comps["minecraft:persistent"] = {}

    events = {
        "wf:on_tame": {"add": {"component_groups": [f"wf:{i}_tamed"]}},
        "wf:start_flying": {"add": {"component_groups": [f"wf:{i}_flying"]}},
        "wf:stop_flying": {"remove": {"component_groups": [f"wf:{i}_flying"]}},
    }
    if common:
        events["minecraft:entity_spawned"] = {"randomize": [
            {"weight": 75, "remove": {"component_groups": [f"wf:{i}_baby"]}},
            {"weight": 25, "add": {"component_groups": [f"wf:{i}_baby"]}}]}
        events["minecraft:entity_born"] = {
            "add": {"component_groups": [f"wf:{i}_baby", f"wf:{i}_tamed"]}}
        events["wf:set_baby"] = {"add": {"component_groups": [f"wf:{i}_baby"]}}
        events["wf:grow_up"] = {"remove": {"component_groups": [f"wf:{i}_baby"]}}

    return {"format_version": "1.21.90", "minecraft:entity": {
        "description": {"identifier": ident, "is_spawnable": True, "is_summonable": True,
                        "is_experimental": False},
        "component_groups": groups, "components": comps, "events": events}}


def bp_egg_entity(d):
    ident = f"wf:{d['id']}_egg"
    return {"format_version": "1.21.90", "minecraft:entity": {
        "description": {"identifier": ident, "is_spawnable": True, "is_summonable": True,
                        "is_experimental": False},
        "components": {
            "minecraft:type_family": {"family": ["wf_egg"]},
            "minecraft:collision_box": {"width": 0.5, "height": 0.6},
            "minecraft:health": {"value": 8, "max": 8},
            "minecraft:physics": {}, "minecraft:pushable": {"is_pushable": False,
                                                            "is_pushable_by_piston": False},
            "minecraft:persistent": {},
            "minecraft:behavior.float": {"priority": 0},
            "minecraft:knockback_resistance": {"value": 1.0}},
        "events": {}}}


def spawn_rule(d):
    s = d["spawn"]
    common = d["tier"] == "common"
    conds = {"minecraft:weight": {"default": s.get("weight", 3)},
             "minecraft:brightness_filter": {"min": s["bright"][0], "max": s["bright"][1],
                                             "adjust_for_weather": False},
             "minecraft:herd": {"min_size": 1, "max_size": 2 if common else 1},
             "minecraft:difficulty_filter": {"min": "easy", "max": "hard"}}
    if s.get("underground"):
        conds["minecraft:spawns_underground"] = {}
    else:
        conds["minecraft:spawns_on_surface"] = {}
    if "biome" in s:
        conds["minecraft:biome_filter"] = {"test": "has_biome_tag", "operator": "==",
                                           "value": s["biome"]}
    return {"format_version": "1.8.0", "minecraft:spawn_rules": {
        "description": {"identifier": f"wf:{d['id']}",
                        "population_control": "animal" if common else "monster"},
        "conditions": [conds]}}


def rp_entity(d):
    i = d["id"]
    pal = d["palette"]
    mat = "entity_alphatest"
    return {"format_version": "1.10.0", "minecraft:client_entity": {"description": {
        "identifier": f"wf:{i}", "materials": {"default": mat},
        "textures": {"default": f"textures/entity/wf_{i}"},
        "geometry": {"default": f"geometry.wf_{i}"},
        "animations": {"idle": "animation.wf_dragon.idle", "walk": "animation.wf_dragon.walk",
                       "fly": "animation.wf_dragon.fly"},
        "scripts": {"animate": [
            {"idle": "q.is_on_ground && q.modified_move_speed <= 0.05"},
            {"walk": "q.is_on_ground && q.modified_move_speed > 0.05"},
            {"fly": "!q.is_on_ground"}]},
        "render_controllers": ["controller.render.wf_default"],
        "spawn_egg": {"base_color": pal["body"], "overlay_color": pal["accent"]}}}}


def rp_egg_entity(d):
    pal = d["palette"]
    return {"format_version": "1.10.0", "minecraft:client_entity": {"description": {
        "identifier": f"wf:{d['id']}_egg", "materials": {"default": "entity_alphatest"},
        "textures": {"default": f"textures/entity/wf_egg_{d['id']}"},
        "geometry": {"default": "geometry.wf_dragon_egg"},
        "animations": {"idle": "animation.wf_egg.idle"},
        "scripts": {"animate": ["idle"]},
        "render_controllers": ["controller.render.wf_default"],
        "spawn_egg": {"base_color": pal["accent"], "overlay_color": pal["belly"]}}}}


# ---- shared egg model + textures ----
def egg_geo():
    g = Geometry("geometry.wf_dragon_egg", 64, 64)
    g.bone("root", (0, 0, 0))
    e = g.bone("egg", (0, 6, 0), parent="root")
    e.cube([-3, 0, -3], [6, 5, 6], [0, 0], region="body")
    e.cube([-3.5, 4, -3.5], [7, 5, 7], [0, 0], region="body")
    e.cube([-2.5, 8, -2.5], [5, 4, 5], [0, 0], region="body")
    e.cube([-1.5, 11, -1.5], [3, 2, 3], [0, 0], region="body")
    g.bounds = [2, 3]
    g.bounds_offset = [0, 1, 0]
    return g


def egg_texture(d):
    t = Tex(64, 64)
    base = hex_rgba(d["palette"]["accent"])
    spot = hex_rgba(d["palette"]["body"])
    for (u, v, sx, sy, sz) in [(0, 0, 6, 5, 6), (0, 20, 7, 5, 7), (40, 0, 5, 4, 5), (40, 20, 3, 2, 3)]:
        t.box(u, v, sx, sy, sz, base, top=shade(base, 1.12), belly=shade(base, 0.85))
    # speckles
    for (x, y) in [(4, 8), (10, 14), (20, 26), (44, 10), (15, 30), (8, 22)]:
        t.rect(x, y, 2, 2, spot)
    return t


def animations():
    return {"format_version": "1.8.0", "animations": {
        "animation.wf_dragon.idle": {"loop": True, "bones": {
            "body": {"position": [0, "math.sin(q.life_time*60)*0.5", 0]},
            "head": {"rotation": ["math.sin(q.life_time*50)*3", "math.cos(q.life_time*40)*4", 0]},
            "wing_l": {"rotation": [0, 0, "math.sin(q.life_time*55)*5-8"]},
            "wing_r": {"rotation": [0, 0, "-math.sin(q.life_time*55)*5+8"]},
            "tail1": {"rotation": [0, "math.sin(q.life_time*45)*6", 0]},
            "tail2": {"rotation": [0, "math.sin(q.life_time*45-30)*7", 0]}}},
        "animation.wf_dragon.walk": {"loop": True, "anim_time_update": "q.modified_distance_moved",
            "bones": {
                "leg_fl": {"rotation": ["math.cos(q.anim_time*38)*36", 0, 0]},
                "leg_fr": {"rotation": ["math.cos(q.anim_time*38+180)*36", 0, 0]},
                "leg_bl": {"rotation": ["math.cos(q.anim_time*38+180)*36", 0, 0]},
                "leg_br": {"rotation": ["math.cos(q.anim_time*38)*36", 0, 0]},
                "tail1": {"rotation": [0, "math.cos(q.anim_time*38)*8", 0]}}},
        "animation.wf_dragon.fly": {"loop": True, "bones": {
            "wing_l": {"rotation": [0, 0, "math.sin(q.life_time*180)*42-10"]},
            "wing_r": {"rotation": [0, 0, "-math.sin(q.life_time*180)*42+10"]},
            "wing_l2": {"rotation": [0, 0, "math.sin(q.life_time*180-40)*38-10"]},
            "wing_r2": {"rotation": [0, 0, "-math.sin(q.life_time*180-40)*38+10"]},
            "body": {"rotation": ["math.sin(q.life_time*180)*3", 0, 0],
                     "position": [0, "math.sin(q.life_time*180)*1.5", 0]},
            "leg_fl": {"rotation": [40, 0, 0]}, "leg_fr": {"rotation": [40, 0, 0]},
            "leg_bl": {"rotation": [30, 0, 0]}, "leg_br": {"rotation": [30, 0, 0]},
            "tail1": {"rotation": ["math.sin(q.life_time*120)*5", 0, 0]}}},
        "animation.wf_egg.idle": {"loop": True, "bones": {
            "egg": {"rotation": ["math.sin(q.life_time*90)*4", 0, "math.cos(q.life_time*70)*3"]}}}}}


def script_data():
    """Element/breath/egg tables consumed by scripts/dragons/index.js."""
    BREATH = {
        "fire": {"particle": "minecraft:basic_flame_particle", "sound": "mob.ghast.fireball",
                 "dmg": 6, "fire": True},
        "frost": {"particle": "minecraft:snowflake_particle", "sound": "mob.wither.shoot",
                  "dmg": 5, "slow": True},
        "netherfire": {"particle": "minecraft:basic_flame_particle", "sound": "mob.ghast.fireball",
                       "dmg": 7, "fire": True},
        "magma": {"particle": "minecraft:lava_particle", "sound": "mob.ghast.fireball",
                  "dmg": 7, "fire": True},
        "frostbite": {"particle": "minecraft:snowflake_particle", "sound": "random.glass",
                      "dmg": 5, "slow": True},
        "lightning": {"particle": "minecraft:electric_spark_particle", "sound": "ambient.weather.lightning.impact",
                      "dmg": 8},
        "wind": {"particle": "minecraft:wind_explosion_emitter", "sound": "mob.phantom.swoop",
                 "dmg": 4, "kb": True},
        "nature": {"particle": "minecraft:vine_particle", "sound": "mob.slime.attack",
                   "dmg": 5, "poison": True},
        "venom": {"particle": "minecraft:wither_boss_invulnerable", "sound": "mob.slime.attack",
                  "dmg": 5, "poison": True},
        "tidal": {"particle": "minecraft:water_splash_particle", "sound": "random.splash",
                  "dmg": 5, "kb": True},
        "decay": {"particle": "minecraft:wither_boss_invulnerable", "sound": "mob.wither.shoot",
                  "dmg": 8, "wither": True},
        "necrotic": {"particle": "minecraft:soul_particle", "sound": "mob.wither.shoot",
                     "dmg": 7, "wither": True},
        "radiant": {"particle": "minecraft:end_chest", "sound": "random.orb", "dmg": 7, "fire": True},
        "shadow": {"particle": "minecraft:dragon_breath_trail", "sound": "mob.enderdragon.flap",
                   "dmg": 7, "wither": True},
        "spirit": {"particle": "minecraft:dragon_breath_trail", "sound": "mob.phantom.swoop",
                   "dmg": 5},
        "stone": {"particle": "minecraft:basic_crit_particle", "sound": "dig.stone", "dmg": 6, "kb": True},
        "void": {"particle": "minecraft:dragon_breath_fire", "sound": "mob.enderdragon.flap",
                 "dmg": 8},
        "drought": {"particle": "minecraft:basic_flame_particle", "sound": "mob.husk.ambient",
                    "dmg": 6, "fire": True},
    }
    elem = {f"wf:{d['id']}": d["element"] for d in DRAGONS}
    eggs = {f"wf:{d['id']}_egg": f"wf:{d['id']}" for d in DRAGONS if d["tier"] == "common"}
    js = (
        "// AUTO-GENERATED by tools/dragongen.py — do not edit by hand.\n"
        f"export const DRAGON_ELEMENT = {json.dumps(elem)};\n"
        f"export const BREATH = {json.dumps(BREATH)};\n"
        f"export const EGG_MAP = {json.dumps(eggs)};\n"
    )
    return js


# --------------------------------------------------------------------------- #
def main():
    ent_dir = ensure(BP, "entities")
    sr_dir = ensure(BP, "spawn_rules")
    rpent_dir = ensure(RP, "entity")
    mdl_dir = ensure(RP, "models", "entity")
    tex_dir = ensure(RP, "textures", "entity")
    anim_dir = ensure(RP, "animations")
    ensure(BP, "scripts", "dragons")

    lang = ["## Wildforge", "pack.name=Wildforge",
            "pack.description=Dragons, pets, vehicles, furniture, building & security.",
            "", "## Dragons"]

    for d in DRAGONS:
        i = d["id"]
        g = build(d)
        t = pack_and_paint(g, d["palette"])
        g.save(os.path.join(mdl_dir, f"wf_{i}.geo.json"))
        t.save(os.path.join(tex_dir, f"wf_{i}.png"))
        dump(os.path.join(ent_dir, f"{i}.json"), bp_entity(d))
        dump(os.path.join(sr_dir, f"{i}.json"), spawn_rule(d))
        dump(os.path.join(rpent_dir, f"{i}.entity.json"), rp_entity(d))
        lang.append(f"entity.wf:{i}.name={d['name']}")
        lang.append(f"item.spawn_egg.entity.wf:{i}.name=Spawn {d['name']}")
        if d["tier"] == "common":
            dump(os.path.join(ent_dir, f"{i}_egg.json"), bp_egg_entity(d))
            dump(os.path.join(rpent_dir, f"{i}_egg.entity.json"), rp_egg_entity(d))
            egg_texture(d).save(os.path.join(tex_dir, f"wf_egg_{i}.png"))
            lang.append(f"entity.wf:{i}_egg.name={d['name']} Egg")
            lang.append(f"item.spawn_egg.entity.wf:{i}_egg.name={d['name']} Egg")

    # shared assets
    egg_geo().save(os.path.join(mdl_dir, "wf_dragon_egg.geo.json"))
    dump(os.path.join(anim_dir, "wf_dragon.animation.json"), animations())
    with open(os.path.join(BP, "scripts", "dragons", "data.js"), "w") as f:
        f.write(script_data())

    # lang: keep pack + dragons; (other domains append later)
    with open(os.path.join(RP, "texts", "en_US.lang"), "w") as f:
        f.write("\n".join(lang) + "\n")

    print(f"generated {len(DRAGONS)} dragons "
          f"({sum(1 for d in DRAGONS if d['tier']=='common')} eggs)")


if __name__ == "__main__":
    main()
