#!/usr/bin/env python3
"""Generate in-depth usage guides under docs/ from the pack's own data + recipes.

Prose is templated here; reference tables are derived from dragons_data, pets_data,
vehicles_data, furniture_data, homebuilding_data, security_data, colors and the
recipe JSONs — so the guides always match what the pack actually ships.
"""
import json
import os
import glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")
BP = os.path.join(ROOT, "Wildforge_BP")

from dragons_data import DRAGONS
from pets_data import PETS
from vehicles_data import VEHICLES
from furniture_data import TYPES as FURN_TYPES, STYLES as FURN_STYLES
from homebuilding_data import MATERIALS, PREFABS, CRAFT as MAT_CRAFT
from security_data import ACTIVE as SEC_ACTIVE, BLOCKS as SEC_BLOCKS, KEYCARD
from colors import DYES


def w(name, text):
    os.makedirs(DOCS, exist_ok=True)
    with open(os.path.join(DOCS, name), "w") as f:
        f.write(text.rstrip() + "\n")
    print("wrote docs/" + name)


def item(s):
    return s.split(":", 1)[-1].replace("_", " ")


def foods(lst):
    return ", ".join(item(x) for x in lst)


# element -> (label, what the breath does)
BREATH_FX = {
    "fire": "sets targets on fire", "netherfire": "sets targets on fire",
    "magma": "sets targets on fire", "drought": "sets targets on fire",
    "radiant": "burns with searing light", "frost": "slows targets",
    "lightning": "heavy shock damage", "wind": "knocks targets back",
    "tidal": "knocks targets back", "stone": "knocks targets back",
    "nature": "poisons targets", "venom": "poisons targets",
    "decay": "withers targets", "necrotic": "withers targets",
    "shadow": "withers targets", "void": "raw void damage", "spirit": "spectral damage",
}


def dragon_where(d):
    s = d["spawn"]
    dim = s.get("dimension", "overworld")
    if dim == "nether":
        return "The Nether"
    if dim == "the_end":
        return "The End"
    if s.get("underground"):
        return "Deep underground, in the dark"
    bio = s.get("biome", "overworld")
    lo, hi = s.get("bright", (0, 15))
    night = " (at night/dark)" if hi <= 7 else (" (in bright daylight)" if lo >= 12 else "")
    pretty = {"overworld": "Overworld surface", "mountains": "Mountains", "ice": "Frozen biomes",
              "forest": "Forests", "desert": "Deserts", "ocean": "Oceans", "swamp": "Swamps",
              "flower_forest": "Flower forests"}.get(bio, bio.replace("_", " ").title())
    return pretty + night


# --------------------------------------------------------------------------- #
def index_doc():
    return """# Wildforge — Guides

In-depth how-to for everything in the pack. New here? Start with **Controls**.

| Guide | What it covers |
|---|---|
| [Controls cheat-sheet](controls.md) | Every interaction at a glance |
| [Dragons](dragons.md) | Taming, riding, breath attacks, breeding, eggs, all 21 |
| [Pets](pets.md) | Taming, carry/ride/follow, commands, leveling, all 19 |
| [Vehicles](vehicles.md) | Crafting, driving land/air/water, passengers, painting, all 17 |
| [Furniture](furniture.md) | Crafting, sitting, storage, lights, painting, all 54 |
| [HomeBuilding](homebuilding.md) | Materials + prefab houses |
| [Security](security.md) | Sensors, cameras, doors, turrets, lasers, the control hub |
| [Recoloring](recoloring.md) | Painting vehicles & furniture with dyes |
| [Crafting reference](crafting.md) | Every recipe in the pack |

> Tip: most things are operated by **interacting** (right-click / left-trigger), often
> with **sneak** held for the "advanced" action. Each guide spells it out.
"""


def controls_doc():
    return """# Controls cheat-sheet

"Interact" = right-click (PC) / the use button (mobile/console). "Sneak" = shift / crouch.

## Dragons
| Action | How |
|---|---|
| Tame | Hold its food, interact repeatedly until hearts appear |
| Ride | Interact a tamed adult (empty hand) |
| Steer | Look where you want to go |
| Climb / descend | Hold **jump** to climb; stop to glide down |
| Breathe (while riding) | **Use an item** (right-click) — fires where you look |
| Dismount | Sneak (the dismount key) |
| Breed | Feed two tamed adults of the same kind |

## Pets
| Action | How |
|---|---|
| Tame | Hold its food, interact |
| Feed (heal + care XP) | Hold its food, interact |
| Command menu | **Sneak + interact** (Follow / Stay / Trick / Mode / Pick up) |
| Carry a small pet | Interact (empty hand) to pick up / put down |
| Ride a large pet | Interact (empty hand) |

## Vehicles
| Action | How |
|---|---|
| Place | Use the crafted spawn item (or creative spawn egg) |
| Drive / steer | Mount, then look where you want to go |
| Climb / dive (air & water) | **Jump** to rise, **sneak** to descend |
| Paint | Hold a **dye**, **sneak + interact** the vehicle |

## Furniture
| Action | How |
|---|---|
| Sit | Interact a chair/stool/sofa/armchair |
| Open storage | Interact a desk/bookshelf/drawer/cabinet/wardrobe/fridge |
| Paint | Hold a **dye**, **sneak + interact** the piece |

## Security
| Action | How |
|---|---|
| Place a device | Use its crafted item (or spawn egg for sensors/turrets/lasers) |
| View cameras | Interact a **Monitor** → pick a camera; **sneak** to exit the view |
| Open a security door | Interact (must be owner / allowlisted / holding a keycard) |
| Keypad | Interact → set or enter the code |
| Configure everything | Interact the **Control Hub** |
"""


def dragons_doc():
    rows = []
    for d in sorted(DRAGONS, key=lambda x: (x["tier"] != "common", x["name"])):
        fx = BREATH_FX.get(d["element"], "damage")
        rows.append(f"| **{d['name']}** | {d['tier']} | {d['element']} ({fx}) | "
                    f"{d['archetype']} | {dragon_where(d)} | {foods(d['food'])} |")
    table = ("| Dragon | Tier | Element (breath) | Body | Where to find | Tame with |\n"
             "|---|---|---|---|---|---|\n" + "\n".join(rows))
    return f"""# Dragons

21 dragons, each with its own model, an element, and a breath attack.

## Finding one
Dragons spawn in specific places (see the table). **Commons** are breedable and not too
rare; **mythic legends** are singular, ultra-rare, never despawn, and can't be bred.
In Creative, every dragon (and every egg) has a spawn egg.

## Taming
Hold the dragon's food and **interact** with it repeatedly. When hearts appear it's yours.
Tamed dragons follow you and won't take fall damage while you ride.

## Riding & flying
**Interact** a tamed adult with an empty hand to mount. **Look** where you want to go,
hold **jump** to climb, and stop holding it to descend. **Sneak** to dismount.

## Breath attacks
- **While riding:** press **use** (right-click) to breathe in the direction you're looking.
- **While not riding:** a tamed dragon **auto-defends you**, breathing at nearby hostile mobs.
- Breath never harms you, your tamed mobs, or allies. The effect depends on the element
  (fire burns, frost slows, venom poisons, decay withers, wind/tidal knock back, etc.).

## Breeding & eggs (commons only)
Feed two tamed adults of the same kind to breed them — the baby is automatically yours.
Dragon **eggs** (Creative, or from drops) hatch about **90 seconds** after you place them;
if you placed it, the hatchling is yours. Babies grow into adults over time.

## Spawn eggs
Spawn eggs and wild spawns are always **full-sized adults** — babies only come from
breeding and hatched eggs.

## The roster
{table}
"""


def pets_doc():
    size_travel = {"small": "small — can be **carried**", "medium": "medium — **follows**",
                   "large": "large — **rideable**"}
    rows = []
    for p in PETS:
        rows.append(f"| **{p['name']}** | {p['tier']} | {size_travel[p['size']]} | "
                    f"{'yes' if p['combat'] else '—'} | {'yes' if p['fly'] else '—'} | "
                    f"{foods(p['food'])} |")
    table = ("| Pet | Type | Size / travel | Fights | Flies | Tame with |\n"
             "|---|---|---|---|---|---|\n" + "\n".join(rows))
    return f"""# Pets

19 companions — realistic and fantasy — that go well beyond vanilla cats and wolves.

## Taming
Hold the pet's food and **interact** with it. Once tamed it's yours and will follow you.

## Travelling together
- **Small** pets can be **carried**: interact (empty hand) to pick one up; interact again
  to set it down. While carried it rides along with you.
- **Large** pets are **rideable**: interact (empty hand) to mount, like a horse.
- **Every** pet **teleports to you** if it falls too far behind, so you never lose one.

## Commands
**Sneak + interact** opens the command menu:
- **Follow / Stay** — toggle whether it follows you or holds position.
- **Do a trick** — a little hop (and a bit of care XP).
- **Mode: Defend / Passive** — (combat pets) whether it fights hostiles for you.
- **Pick up / Put down** — (small pets) carry toggle.

## Feeding & healing
Hold the pet's food and **interact** to feed it: it heals and earns **care XP**.

## Leveling (two ways)
Pets gain XP from **fighting** (combat pets that land kills) **and** from **care**
(feeding, tricks). Levels persist per-pet, raise health (and attack for fighters), and
the pet's level shows on its nameplate. Combat pets in **Defend** mode protect you.

## The roster
{table}
"""


def vehicles_doc():
    by_cat = {"land": [], "air": [], "water": []}
    for v in VEHICLES:
        by_cat[v["category"]].append(
            f"| **{v['name']}** | {v['seats']} | {item(v['craft'])} (+ redstone, leather) |")
    def block(cat):
        return ("| Vehicle | Seats | Crafted from |\n|---|---|---|\n"
                + "\n".join(by_cat[cat]))
    return f"""# Vehicles

17 vehicles across land, air and water. Multi-seat, arcade-fast, **no fuel**, and **no
fall or collision damage** while riding.

## Getting one
Craft its **spawn item** at a crafting table, then **use the item** to place the vehicle
in front of you. In Creative you can also use the spawn egg. (Recipes in each table below;
full list in the [crafting reference](crafting.md).)

## Driving
**Mount** by interacting, then **look** where you want to go.
- **Land** vehicles hug the ground; they'll step up small rises.
- **Air** vehicles (planes, jet, helicopter, glider, balloon) fly: **jump** to climb,
  **sneak** to descend.
- **Water** vehicles float and move on or under the surface; the **submarine** dives with
  **sneak** and surfaces with **jump**.
- Extra **seats** let friends ride along.

## Painting
Hold any **dye**, then **sneak + interact** the vehicle to repaint its body. See
[Recoloring](recoloring.md).

## Land
{block("land")}

## Air
{block("air")}

## Water
{block("water")}
"""


def furniture_doc():
    feat = []
    for t in FURN_TYPES:
        tags = []
        if t.get("sit"): tags.append("sit")
        if t.get("storage"): tags.append("storage")
        if t.get("light"): tags.append("light")
        feat.append(f"| {t['label']} | {', '.join(tags) or 'décor'} |")
    table = "| Piece | Function |\n|---|---|\n" + "\n".join(feat)
    styles = ", ".join(f"**{s['label']}** ({item(s['material'])})" for s in FURN_STYLES.values())
    return f"""# Furniture

54 pieces — 18 types in three styles: {styles}.

## Crafting & placing
Craft each piece from its style's material at a crafting table. Directional pieces
(chairs, sofas, desks, etc.) automatically **face you** when placed.

## Sitting
**Interact** a chair, stool, sofa or armchair to sit. Sneak (dismount) to stand up.

## Storage
**Interact** a desk, bookshelf, drawers, cabinet, wardrobe or fridge to open its stash:
- **Deposit held item** stores the stack in your hand.
- Selecting a stored stack takes it back.
Each block keeps its own contents.

## Lights
Lamps, floor lamps and wall lamps emit light.

## Painting
Hold any **dye**, then **sneak + interact** a piece to recolor its upholstery/accent
(cushions, panels) while keeping the wood/frame. See [Recoloring](recoloring.md).

## Pieces
{table}
"""


def homebuilding_doc():
    cats = {}
    for m in MATERIALS:
        cats.setdefault(m["cat"], []).append(m["label"])
    mat_rows = "\n".join(f"| {c} | {', '.join(v)} | {item(MAT_CRAFT.get(c,'oak planks'))} |"
                         for c, v in cats.items())
    prefab_rows = "\n".join(f"- **{p['label']}**" for p in PREFABS)
    return f"""# HomeBuilding

35 building materials plus 8 ready-made houses.

## Materials
Each material is a full block you craft from a representative ingredient (x4 → 4 blocks)
and build with freely.

| Category | Blocks | Crafted from |
|---|---|---|
{mat_rows}

## Prefab houses
Each house is a **placer item**. Craft it, then **use it** and confirm the prompt — a
complete structure is placed in front of you, oriented to your facing, and built from the
pack's own materials. Big builds place over a couple of seconds.

> Heads-up: placing overwrites whatever blocks are there, so use it on clear ground.

Available houses:
{prefab_rows}
"""


def security_doc():
    active = "\n".join(f"- **{a['name']}** — " + {
        "sensor": "alerts you (sound + message) when an intruder enters its range.",
        "tripwire": "projects a beam; anything that crosses it is alarmed and zapped.",
        "turret": "targets intruders and fires at them on a cooldown.",
        "laser": "fires a continuous **lethal** beam at whatever it targets.",
    }[a["kind"]] for a in SEC_ACTIVE)
    return f"""# Security

A base-defense suite. **You own** what you place, and every defensive device's targeting
is **owner-configurable**: it never harms you, your allowlist, or your pets.

## Active devices
Place these from their crafted items (or Creative spawn eggs). They run automatically:

{active}

By default they target **hostile mobs only**. Use the **Control Hub** to switch them to
also target **intruders** (non-allowlisted players), and to arm/disarm them.

## Cameras & monitor
Place **Security Cameras** around your base, then **interact a Monitor** to pick a camera
and see its view. **Sneak** to exit and return to yourself.

## Doors, keypads & keycards
- **Security Door** — opens only for the **owner**, an **allowlisted** player, or anyone
  holding a **{KEYCARD['name']}**. Others get "Locked".
- **Keypad Lock** — interact to set a code (owner) or enter it; the right code opens a
  nearby security door.

## Other blocks
- **Floodlight** — bright, always-on light.
- **Alarm Siren** — a manual panic button: interact to sound the alarm.
- **Control Hub** — interact to manage your whole network: **arm/disarm all**, set
  **global targeting** (hostiles only ↔ + intruders), and **add nearby players** to your
  allowlist.

## Device list
- Active: {', '.join(a['name'] for a in SEC_ACTIVE)}
- Blocks: {', '.join(b['name'] for b in SEC_BLOCKS)}
- Item: {KEYCARD['name']}
"""


def recoloring_doc():
    swatches = "\n".join(f"- {name.replace('_',' ').title()} (`{item(di)}`)" for name, di, _ in DYES)
    return f"""# Recoloring

Vehicles and furniture can be painted any of the **16 dye colors**.

## How
Hold a **dye** in your main hand, then **sneak + interact** with the item:
- **Vehicles** repaint their **body** (glass, trim and details stay).
- **Furniture** recolors its **upholstery/accent** (cushions, panels) while the wood/frame
  stays.

Sneak is required so painting never clashes with riding a vehicle or sitting in / opening
a piece of furniture. In Survival the dye is consumed; in Creative it isn't. Paint as many
times as you like — repaint with a different dye to change again.

## The 16 colors
{swatches}
"""


def crafting_doc():
    by_domain = {"Dragons": [], "Pets": [], "Vehicles": [], "Furniture": [],
                 "HomeBuilding": [], "Security": [], "Other": []}
    veh_ids = {v["id"] for v in VEHICLES}
    furn = {f"{t['key']}_{s}" for t in FURN_TYPES for s in FURN_STYLES}
    mat_ids = {m["id"] for m in MATERIALS}
    prefab_ids = {p["id"] for p in PREFABS}
    sec_ids = {a["id"] for a in SEC_ACTIVE} | {b["id"] for b in SEC_BLOCKS} | {"keycard"}
    for path in sorted(glob.glob(os.path.join(BP, "recipes", "*.json"))):
        with open(path) as f:
            r = json.load(f)
        body = r.get("minecraft:recipe_shapeless") or r.get("minecraft:recipe_shaped")
        if not body:
            continue
        res = body.get("result")
        res = res[0] if isinstance(res, list) else res
        rid = (res or {}).get("item", "?")
        count = (res or {}).get("count", 1)
        ings = body.get("ingredients", [])
        # tally ingredient counts
        tally = {}
        for ing in ings:
            it = ing.get("item") if isinstance(ing, dict) else ing
            if it:
                tally[it] = tally.get(it, 0) + 1
        ing_str = ", ".join(f"{tally[k]}× {item(k)}" for k in tally)
        name = os.path.basename(path)[:-5]
        line = f"| {item(rid)} ×{count} | {ing_str} |"
        bare = name.replace("_item", "").replace("_placer", "")
        if bare in veh_ids or name.replace("_item", "") in veh_ids:
            by_domain["Vehicles"].append(line)
        elif name in furn:
            by_domain["Furniture"].append(line)
        elif bare in mat_ids:
            by_domain["HomeBuilding"].append(line)
        elif name.replace("_placer", "") in prefab_ids:
            by_domain["HomeBuilding"].append(line)
        elif bare in sec_ids or name.replace("_item", "") in sec_ids:
            by_domain["Security"].append(line)
        else:
            by_domain["Other"].append(line)
    out = ["# Crafting reference",
           "", "Every craftable item/block in the pack. All recipes are shapeless on a "
           "crafting table. (Dragons, pets and security sensors/turrets/lasers also have "
           "Creative spawn eggs.)", ""]
    for dom, lines in by_domain.items():
        if not lines:
            continue
        out.append(f"## {dom}")
        out.append("| Result | Ingredients |")
        out.append("|---|---|")
        out.extend(sorted(set(lines)))
        out.append("")
    return "\n".join(out)


def main():
    w("README.md", index_doc())
    w("controls.md", controls_doc())
    w("dragons.md", dragons_doc())
    w("pets.md", pets_doc())
    w("vehicles.md", vehicles_doc())
    w("furniture.md", furniture_doc())
    w("homebuilding.md", homebuilding_doc())
    w("security.md", security_doc())
    w("recoloring.md", recoloring_doc())
    w("crafting.md", crafting_doc())


if __name__ == "__main__":
    main()
