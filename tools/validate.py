#!/usr/bin/env python3
"""Wildforge pack validator.

Structural + cross-reference checks that catch the errors that actually break an
add-on in-game, short of launching Minecraft:
  - every .json parses
  - manifest UUIDs are unique and dependencies resolve
  - every client-entity geometry / texture / render_controller / animation reference resolves
  - every BP entity & spawn-egg identifier has an en_US.lang name
  - spawn_rules identifiers correspond to real BP entities

Exit code is non-zero if any ERROR is found (warnings don't fail the build).
"""
from __future__ import annotations
import json
import os
import sys
import glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BP = os.path.join(ROOT, "Wildforge_BP")
RP = os.path.join(ROOT, "Wildforge_RP")

errors: list[str] = []
warnings: list[str] = []


def err(m): errors.append(m)
def warn(m): warnings.append(m)


def load_json(path):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception as e:  # noqa: BLE001
        err(f"JSON parse failed: {rel(path)}: {e}")
        return None


def rel(p): return os.path.relpath(p, ROOT)


def all_json(base, sub):
    return sorted(glob.glob(os.path.join(base, sub, "**", "*.json"), recursive=True))


def main():
    if not os.path.isdir(BP) or not os.path.isdir(RP):
        err("Wildforge_BP and/or Wildforge_RP not found")
        return report()

    # ---- manifests / UUIDs ----
    uuids = {}
    for label, base in (("BP", BP), ("RP", RP)):
        man = load_json(os.path.join(base, "manifest.json"))
        if not man:
            continue
        ids = [man.get("header", {}).get("uuid")]
        ids += [m.get("uuid") for m in man.get("modules", [])]
        for u in ids:
            if not u:
                err(f"{label} manifest has a missing uuid")
            elif u in uuids:
                err(f"Duplicate UUID {u} ({label} and {uuids[u]})")
            else:
                uuids[u] = label

    # ---- collect geometry / render controller / animation identifiers (RP) ----
    geoms = set()
    for p in all_json(RP, "models"):
        d = load_json(p)
        if not d:
            continue
        for g in d.get("minecraft:geometry", []):
            ident = g.get("description", {}).get("identifier")
            if ident:
                geoms.add(ident)

    controllers = set()
    for p in all_json(RP, "render_controllers"):
        d = load_json(p)
        if d:
            controllers.update((d.get("render_controllers") or {}).keys())

    anims = set()
    for p in all_json(RP, "animations"):
        d = load_json(p)
        if d:
            anims.update((d.get("animations") or {}).keys())
            anims.update((d.get("animation_controllers") or {}).keys())
    for p in all_json(RP, "animation_controllers"):
        d = load_json(p)
        if d:
            anims.update((d.get("animation_controllers") or {}).keys())

    # ---- lang ----
    lang_keys = set()
    lang_path = os.path.join(RP, "texts", "en_US.lang")
    if os.path.exists(lang_path):
        with open(lang_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    lang_keys.add(line.split("=", 1)[0].strip())
    else:
        err("missing texts/en_US.lang")

    # ---- client entities (RP) ----
    for p in all_json(RP, "entity"):
        d = load_json(p)
        if not d:
            continue
        desc = (d.get("minecraft:client_entity") or {}).get("description", {})
        ident = desc.get("identifier", rel(p))
        for g in (desc.get("geometry") or {}).values():
            name = g if g.startswith("geometry.") else "geometry." + g.split(".", 1)[-1]
            if g not in geoms and name not in geoms:
                err(f"{ident}: geometry '{g}' not found in models/")
        for t in (desc.get("textures") or {}).values():
            if not _texture_exists(t):
                err(f"{ident}: texture '{t}' file not found")
        for rc in (desc.get("render_controllers") or []):
            rcid = rc if isinstance(rc, str) else next(iter(rc), "")
            if rcid not in controllers:
                err(f"{ident}: render_controller '{rcid}' not defined")
        for a in (desc.get("animations") or {}).values():
            if a not in anims:
                warn(f"{ident}: animation '{a}' not defined in RP animations")

    # ---- BP entities ----
    bp_ids = set()
    for p in all_json(BP, "entities"):
        d = load_json(p)
        if not d:
            continue
        desc = (d.get("minecraft:entity") or {}).get("description", {})
        ident = desc.get("identifier")
        if not ident:
            err(f"{rel(p)}: entity has no identifier")
            continue
        bp_ids.add(ident)
        if f"entity.{ident}.name" not in lang_keys:
            err(f"{ident}: missing lang key entity.{ident}.name")
        if desc.get("is_spawnable") and f"item.spawn_egg.entity.{ident}.name" not in lang_keys:
            warn(f"{ident}: missing spawn-egg lang key")

    # ---- spawn rules ----
    for p in all_json(BP, "spawn_rules"):
        d = load_json(p)
        if not d:
            continue
        ident = (d.get("minecraft:spawn_rules") or {}).get("description", {}).get("identifier")
        if ident and ident not in bp_ids:
            err(f"spawn_rule '{ident}' has no matching BP entity")

    # ---- items + item textures ----
    item_tex = {}
    itx = load_json(os.path.join(RP, "textures", "item_texture.json"))
    if itx:
        for short, e in (itx.get("texture_data") or {}).items():
            item_tex[short] = e.get("textures")
            if not _texture_exists(e.get("textures", "")):
                err(f"item_texture '{short}' file '{e.get('textures')}' not found")
    item_ids = set()
    for p in all_json(BP, "items"):
        d = load_json(p)
        if not d:
            continue
        desc = (d.get("minecraft:item") or {}).get("description", {})
        ident = desc.get("identifier")
        if not ident:
            err(f"{rel(p)}: item has no identifier")
            continue
        item_ids.add(ident)
        if f"item.{ident}.name" not in lang_keys:
            warn(f"{ident}: missing lang key item.{ident}.name")
        icon = ((d["minecraft:item"].get("components") or {}).get("minecraft:icon") or {})
        tex = icon.get("texture") if isinstance(icon, dict) else icon
        if tex and tex not in item_tex:
            err(f"{ident}: icon '{tex}' not declared in item_texture.json")

    # ---- blocks + terrain textures ----
    terrain = {}
    tt = load_json(os.path.join(RP, "textures", "terrain_texture.json"))
    if tt:
        for short, e in (tt.get("texture_data") or {}).items():
            terrain[short] = e.get("textures")
            if not _texture_exists(e.get("textures", "")):
                err(f"terrain_texture '{short}' file '{e.get('textures')}' not found")
    block_ids = set()
    for p in all_json(BP, "blocks"):
        d = load_json(p)
        if not d:
            continue
        b = d.get("minecraft:block") or {}
        ident = b.get("description", {}).get("identifier")
        if not ident:
            err(f"{rel(p)}: block has no identifier")
            continue
        block_ids.add(ident)
        comps = b.get("components") or {}
        geo = comps.get("minecraft:geometry")
        geo = geo if isinstance(geo, str) else (geo or {}).get("identifier")
        if geo and geo not in geoms:
            err(f"{ident}: geometry '{geo}' not found in models/")
        mat_blocks = [comps.get("minecraft:material_instances") or {}]
        for perm in (b.get("permutations") or []):
            mat_blocks.append((perm.get("components") or {}).get("minecraft:material_instances") or {})
        for mi in mat_blocks:
            for inst in mi.values():
                t = inst.get("texture") if isinstance(inst, dict) else inst
                if t and t not in terrain:
                    err(f"{ident}: material texture '{t}' not in terrain_texture.json")
        # permutation geometry references
        for perm in (b.get("permutations") or []):
            pg = (perm.get("components") or {}).get("minecraft:geometry")
            pg = pg if isinstance(pg, str) else (pg or {}).get("identifier") if pg else None
            if pg and pg not in geoms:
                err(f"{ident}: permutation geometry '{pg}' not found in models/")
        if f"tile.{ident}.name" not in lang_keys:
            err(f"{ident}: missing lang key tile.{ident}.name")

    # ---- recipes resolve to a real item/entity ----
    for p in all_json(BP, "recipes"):
        d = load_json(p)
        if not d:
            continue
        for key in ("minecraft:recipe_shapeless", "minecraft:recipe_shaped"):
            if key in d:
                res = d[key].get("result")
                res = res[0] if isinstance(res, list) else res
                ritem = (res or {}).get("item", "")
                known = item_ids | bp_ids | block_ids
                if ritem.startswith("wf:") and ritem not in known:
                    err(f"recipe {rel(p)} produces undefined '{ritem}'")

    return report()


def _texture_exists(t):
    for ext in (".png", ".tga"):
        if os.path.exists(os.path.join(RP, t + ext)):
            return True
    return False


def report():
    for w in warnings:
        print(f"  WARN  {w}")
    for e in errors:
        print(f"  ERR   {e}")
    print(f"\nvalidate: {len(errors)} error(s), {len(warnings)} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
