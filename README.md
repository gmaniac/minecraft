# Wildforge

A combined Minecraft **Bedrock 1.21.90+** add-on — dragons, pets, vehicles, furniture,
home building and security — built from scratch (models, textures, animations, behavior,
Script API). **No experiments required.** Packaged as a single `Wildforge.mcaddon`.

> Status: **Complete — all six domains shipped** (Dragons, Pets, Vehicles, Furniture,
> HomeBuilding, Security). See `BUILD_PLAN.md` for how it was built.

## 📖 In-depth guides → [`docs/`](docs/README.md)
Full how-to for every feature: [Controls](docs/controls.md) ·
[Dragons](docs/dragons.md) · [Pets](docs/pets.md) · [Vehicles](docs/vehicles.md) ·
[Furniture](docs/furniture.md) · [HomeBuilding](docs/homebuilding.md) ·
[Security](docs/security.md) · [Recoloring](docs/recoloring.md) ·
[Crafting reference](docs/crafting.md). The guides are generated from the pack's own data
(`tools/gen_docs.py`), so they always match what's shipped.

## Install
1. Open `Wildforge.mcaddon` on a device with Minecraft — it imports both packs at once.
2. In a world: **Behavior Packs → add "Wildforge (Behavior)"**; the resource pack links
   automatically. Requires Bedrock **1.21.90+**.
3. Re-importing updates the add-on in place (fixed pack UUIDs) instead of duplicating it.

---

## Dragons — 21 of them

Every dragon has its **own model** (distinct body plan, not a reskin), heavy element-themed
geometry, an idle particle aura/trail, and a **breath attack**.

### Breath attacks
- **While riding:** right-click (use an item) to breathe in the direction you're looking.
- **While not riding:** a tamed dragon **auto-defends** you, breathing at nearby hostile mobs.
- Breath never harms you, your other tamed mobs, or allies.

### Commons — tame, breed & lay eggs (17)
| Dragon | Body plan | Element | Where | Tame with |
|---|---|---|---|---|
| **Ember** | western | fire | Overworld | steak |
| **Storm** | western | wind | Overworld | salmon |
| **Ancient** | drake | stone | Mountains | golden apple |
| **Glacier** | western | frost | Icy biomes | golden carrot |
| **Inferno** | wyvern | nether fire | The Nether | golden apple |
| **Eclipse** | four-winged | void | The End | ench. golden apple |
| **Nature** | western | nature | Forests | apple / berries |
| **Lightning** | wyvern | lightning | Overworld | copper / chicken |
| **Poison** | drake | venom | Swamps | spider eye |
| **Desert** | western | drought | Deserts | cactus / rabbit |
| **Spirit** | western | spirit | Overworld (dark) | glow berries |
| **Magma** | drake | magma | The Nether | magma cream |
| **Tidal** | western | tidal | Oceans | salmon |
| **Bone** | western | necrotic | Overworld (dark) | bone |
| **Fae** | four-winged | spirit | Flower forests | honey bottle |
| **Sun** | western | radiant | Overworld (bright) | glowstone / gold |
| **Shadow** | western | shadow | Overworld (dark) | black dye |

### Mythic legends — singular, ultra-rare, never despawn, no breeding (4)
| Legend | Body plan | Element | Where | Tame with |
|---|---|---|---|---|
| **Níðhǫggr** | western, antlers, long spiked tail | decay | Deep underground, in darkness | ench. golden apple |
| **Apep** | wingless, legless serpent | venom | Deserts, at night | ench. golden apple |
| **Tiamat** | three heads, finned | tidal | Oceans | nether star |
| **The Hydra** | three heads, four legs | venom | Swamps | ench. golden apple |

## How to play
- **Tame & ride:** feed an adult its food until hearts appear, then mount it. Steer where you
  look, hold **jump** to climb, dismount to land. No fall damage while riding; tamed dragons
  follow you.
- **Breed** (commons): feed two tamed adults of the same kind — the baby is automatically yours.
- **Eggs** (commons): a placed egg hatches after ~90 seconds; the hatchling is yours.
- **Creative:** spawn eggs exist for every dragon and egg, including the mythic legends.

---

## Pets — 19 companions

Realistic and fantasy pets that go well beyond vanilla cats/wolves. Tame with each
pet's food, then they're yours.

**Travel:** small pets can be **carried** (interact to pick up / put down), large pets
can be **ridden**, and **every** pet **teleports to you** when it falls too far behind.

**Commands:** sneak + interact opens a menu — **Follow / Stay**, **Do a trick**, a
**Defend ↔ Passive** toggle (combat pets), and **Pick up / Put down** (small pets).

**Leveling (both paths):** pets gain XP from **fighting** (combat pets that land kills)
and from **care** (feeding them their food, doing tricks). Levels persist per-pet and
raise health (and attack, for fighters); the pet's nameplate shows its level.

| Realistic | Fantasy |
|---|---|
| Dog, Cat, Rabbit, Fox, Ferret, Hamster, Parrot, Gecko, Iguana, Turtle, Capybara, Pony, Riding Lizard | Slime Pet, Ember Sprite, Frost Sprite, Mushroom Critter, Cloud Pup, Crystal Fox |

- **Small (carry):** Cat, Rabbit, Ferret, Hamster, Parrot, Gecko, Slime Pet, Ember/Frost
  Sprite, Mushroom Critter, Cloud Pup
- **Medium (follow):** Dog, Fox, Iguana, Turtle, Crystal Fox
- **Large (ride):** Capybara, Pony, Riding Lizard
- **Fighters (defend & level by combat):** Dog, Fox, Riding Lizard, Ember/Frost Sprite, Crystal Fox

---

## Vehicles — 17 to drive

Multi-seat, arcade-fast, **no fuel**, **no fall/collision damage** while riding.

- **Get one:** craft its **spawn item** (each uses a representative material like iron +
  redstone + leather) and **use it** to place the vehicle — or grab the creative spawn egg.
- **Drive:** mount it, steer where you look. **Land** vehicles hug the ground; **air** and
  **water** vehicles use **jump to rise / sneak to descend** (planes/jets/helis fly, subs dive).
- **Passengers:** extra seats let friends ride along.
- **Paint:** hold any **dye**, **sneak + interact** with a vehicle to repaint its body in
  that color (16 dye colors).

| Land | Air | Water |
|---|---|---|
| Sports Car, Sedan, Pickup, Monster Truck, Bus, Motorbike, Quad ATV, Dune Buggy | Propeller Plane, Jet, Helicopter, Glider, Hot-Air Balloon | Speedboat, Jetski, Submarine, Pontoon Boat |

Wheels, propellers and rotors animate while in motion.

---

## Furniture — 54 custom blocks (3 styles)

18 furniture types in **Modern**, **Rustic** and **Medieval** styles. Craft each from its
style's material (quartz / oak / dark-oak) at a crafting table.

- **Sit-able:** chairs, stools, sofas, armchairs — interact to sit (an invisible seat
  entity carries you; it cleans itself up when you stand).
- **Working lights:** lamps, floor lamps, wall lamps emit light.
- **Storage:** desks, bookshelves, drawers, cabinets, wardrobes, fridges open a stash —
  interact, then **Deposit held item** or take a stored stack back. Contents persist per block.
- **Décor:** dining/coffee tables, beds, rugs, potted plants.
- **Paint:** hold any **dye**, **sneak + interact** with a piece to recolor its
  upholstery/accent (16 dye colors) while keeping the wood/frame.
- Directional pieces rotate to face you on placement.

Types: Chair, Stool, Sofa, Armchair, Dining Table, Coffee Table, Desk, Bookshelf, Drawers,
Cabinet, Wardrobe, Fridge, Lamp, Floor Lamp, Wall Lamp, Bed, Rug, Potted Plant.

---

## HomeBuilding — 35 materials + 8 prefab houses

**Materials (35):** full-cube building blocks you craft and build with — plank sets
(ashwood/walnut/pine/ebony), beams, stone (slate/granite/marble/sandstone/bluestone),
bricks, plaster, glass (clear/tinted/frosted), roofing shingles, siding, flooring and trim.

**Prefab houses (8):** craft a **placer item**, hold it and **use it** — confirm the prompt
and a complete structure (built from these materials) is placed in front of you, oriented to
your facing. Modern House, Cozy Cottage, Cabin, Mansion, Tower, Barn, Shop, Starter Base.

---

## Security — 12 devices

A base-defense suite. **Targeting is owner-configurable** everywhere (Hostiles only ↔
+ Intruders), and your devices never harm you, your allowlist, or your pets.

- **Auto Turret** — targets and fires at intruders on a cooldown.
- **Laser Emitter** — a continuous **lethal** beam that melts whatever crosses it.
- **Motion Sensor** — alerts you (sound + message) when something enters its range.
- **Laser Tripwire** — a beam that alarms and zaps anything crossing it.
- **Security Camera + Monitor** — place cameras, then view them from a monitor.
- **Security Door** — opens only for you, your allowlist, or a **Keycard** holder.
- **Keypad Lock** — set a code; the right code opens a nearby security door.
- **Alarm Siren** — a manual panic button.
- **Floodlight** — bright always-on light.
- **Control Hub** — arm/disarm all your devices, set global targeting, and add nearby
  players to your allowlist.

Place turrets/lasers/sensors/tripwires from their crafted items (or creative spawn eggs);
the rest are blocks. **Sneak to exit a camera view.**

---

## Building from source
Everything is **procedurally generated** so the rosters stay maintainable. See `tools/README.md`.
```bash
PYTHONPATH=tools python3 tools/dragongen.py   # regenerate dragon models/textures/entities
PYTHONPATH=tools python3 tools/preview.py      # offline montage -> dragons_preview.png
bash tools/build.sh                            # validate + package Wildforge.mcaddon
```

## Notes
- Models are procedurally generated and **fully refinable in Blockbench** — each dragon is at
  `Wildforge_RP/models/entity/wf_<id>.geo.json`. Textures use box-UV region mapping done without
  a live preview; colors are close and a Blockbench paint pass can perfect them.
- This repo can't launch Minecraft, so correctness is enforced by `tools/validate.py`
  (reference/lang/UUID checks) + `node --check` on scripts + the offline preview render. Final
  in-game verification is yours — if anything faces backward, rotate its `root` bone 180° on Y.
