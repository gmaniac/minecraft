# Motor Dragons — v2.1

Ten rideable, flyable dragons for **Minecraft Bedrock 1.21.90+**, built from scratch
(models, textures, animations, behavior, Script API). **No experiments required.**

### New in v2.1 — high detail
Every dragon was rebuilt with far more geometry (~3x the parts):
- **Finger-boned wings** — humerus + forearm + fanned finger struts with membrane between them.
  Wing styles differ per dragon: membrane, tattered, crystalline, fin, and four-winged.
- **Detailed heads** — separate animated **jaw**, teeth, eyes, brow, snout, and per-dragon **horns**
  (swept, crown, single, antler) plus ears / frills / crests.
- **Clawed legs** — thigh + shin + foot with three claws.
- **Spiked dorsal ridges** — individual angled spikes; ice/ocean dragons get a webbed sail.
- **Distinct tail tips** — spike, club, fin fluke, or spade.
- **Multi-region texturing** — scaled body, lighter belly, tinted wing membranes, bone horns,
  white teeth, and glowing eyes.

---

## Install
1. Open `MotorDragons.mcaddon` on a device with Minecraft — it imports both packs at once.
2. In a world: **Behavior Packs -> add "Motor Dragons (Behavior)"**; the resource pack links automatically.
3. Requires Bedrock **1.21.90+**.

---

## The roster

### Common dragons — breed & lay eggs
| Dragon | Look | Where | Tame with |
|---|---|---|---|
| **Ember** | small, swept horns, membrane wings, lava-cracked red | Overworld (common) | Steak |
| **Storm** | sleek, head crest, fin tail, crystalline-blue wings | Overworld (uncommon) | Cooked salmon |
| **Ancient** | bulky, crowned horns, cheek frills, club tail, big wings | Mountains (rare) | Golden apple |
| **Glacier** | single forehead horn, ice-crest sail, crystal wings | Frozen biomes (rare) | Golden carrot |
| **Inferno** | tattered wings, flame ridge, fireproof | The Nether (rare) | Golden apple |
| **Eclipse** | four wings, night-fury ears, spade tail, obsidian-purple | The End (apex) | Enchanted golden apple |

### Mythic legends — singular, ultra-rare, never despawn, no breeding/eggs
| Legend | Look | Where | Tame with |
|---|---|---|---|
| **Nidhoggr** | antler horns, long 5-segment spiked tail, dorsal sail, decayed hide | Deep underground, in darkness | Enchanted golden apple |
| **Apep** | wingless, legless serpent, fanged frilled head, long undulating body | Deserts, at night | Enchanted golden apple |
| **Tiamat** | **three heads**, webbed fins, finned tail, dorsal sail, largest of all | Oceans | Nether star |
| **The Hydra** | **three heads** on long necks, four clawed legs, spiked tail | Swamps | Enchanted golden apple |

---

## How to play
- **Tame & ride:** feed an adult its food until hearts appear, then mount it. Steer where you look,
  hold **jump** to climb, dismount to land. No fall damage while riding. Tamed dragons follow you.
- **Breed** (common dragons): feed two tamed adults of the same kind — the baby is automatically yours.
- **Eggs** (common dragons): a dragon egg hatches after ~90 seconds; if you placed it, the hatchling is yours.
- **Creative:** spawn eggs exist for every dragon, including the mythic legends.

---

## Notes
- Models are procedurally generated and **fully refinable in Blockbench** — each dragon is its own file at
  `MotorDragons_RP/models/entity/motor_<id>.geo.json`.
- Textures use region/box-UV mapping done without a live preview; colors are close but a Blockbench
  paint pass can perfect them. Geometry was verified; texture tweaks are the most likely thing to touch.
- If a dragon ever faces backward in-game, rotate its root bone 180 degrees on Y in Blockbench.
- Re-importing this file updates the add-on in place (fixed pack UUIDs) rather than duplicating it.
