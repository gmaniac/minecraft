# Combined Add-On — Build Plan

**Goal:** one combined `.mcaddon` (single Behavior Pack + Resource Pack pair) containing **six**
domains (Dragons + the five new ones), built to and beyond the quality bar set by the original
`Dragons/MotorDragons.mcaddon`. Dragons is **reworked**, not just folded in.

- **Target:** Minecraft Bedrock **1.21.90+**, `format_version` 1.21.90, **no experiments**, Script API `@minecraft/server` **2.0.0** (+ `@minecraft/server-ui` for menus).
- **Ambition:** **Maximal** rosters.
- **Build order:** Dragons (rework) → Pets → Vehicles → Furniture → HomeBuilding → Security. Each
  domain is finished (models, textures, behavior, scripts, lang, packaged, validated) before the next
  folds in. Dragons goes first: it stresses the model/texture generator at maximum complexity and
  produces the shared combat libs (targeting, breath FX, projectiles) that Pets and Security reuse.
- **Deliverable:** one combined pack. Working title `Wildforge` (`Wildforge.mcaddon`).

---

## 1. Architecture & conventions

### Pack layout (single combined BP + RP)
```
Wildforge_BP/
  manifest.json            # data + script modules, depends on RP uuid + @minecraft/server 2.0.0
  pack_icon.png
  scripts/
    main.js                # entry — imports every domain module, registers block components
    lib/                   # shared helpers (owner, persistence, menus, targeting, fx)
    pets/  vehicles/  furniture/  homebuilding/  security/   # one module per domain
  entities/                # all BP entities, prefixed by domain
  spawn_rules/             # pets only (+ any naturally-spawning security/critters)
  blocks/                  # custom blocks (furniture, materials, security devices)
  items/                   # custom items (keycards, fuel-free remotes, prefab placers, build wand)
  recipes/                 # crafting for blocks/items
  loot_tables/             # drops where relevant
  functions/  (optional)   # /function helpers for prefab placement fallback
Wildforge_RP/
  manifest.json            # resources module, depends on BP uuid
  pack_icon.png
  entity/                  # client entity defs
  models/entity/           # procedurally-generated .geo.json (one per model)
  models/blocks/           # custom block geometry where needed (furniture)
  textures/entity/  textures/blocks/  textures/items/
  textures/terrain_texture.json, item_texture.json
  animations/  animation_controllers/
  render_controllers/
  attachables/  (vehicles/pets cosmetics if needed)
  sounds/  sounds/sound_definitions.json   # alarms, engines, laser
  texts/  en_US.lang, languages.json
```

### Naming
- **Single namespace `wf:`** for everything, with a **domain prefix** in the identifier so the
  flat folders stay readable: `wf:pet_*`, `wf:veh_*`, `wf:furn_*`, `wf:build_*`,
  `wf:sec_*`, plus shared `wf:seat` (invisible sit/ride helper).
- UUIDs: a fresh fixed UUID set (5 UUIDs: BP header, data module, script module, RP header, RP
  module) so re-imports update in place — same discipline as Dragons.

### Toolchain (how the content is actually produced)
- **Model generator** (Python, kept in `tools/`): builds detailed `.geo.json` procedurally the way
  the dragons were (parametric bones/cubes, box-UV). One generator per family (pet body plans,
  vehicle chassis, furniture primitives) so 16 pets aren't hand-typed.
- **Texture generator** (Python + Pillow): paints region/box-UV PNGs from a per-model palette, same
  approach the dragons used. Reviewable/perfectable in Blockbench afterward.
- **Packager** (`tools/build.sh`): zips BP+RP into `Wildforge.mcaddon` with deterministic paths.
- **Validator** (`tools/validate.py`): JSON-parses every file, checks every entity↔geometry↔texture
  reference resolves, every `wf:` identifier has a lang entry, no dangling component groups/events,
  UUID uniqueness. Run before every package step. This is the "working" guarantee short of launching
  the game (which this environment can't do — see §7).

### Shared script library (`scripts/lib/`)
- `owner.js` — set/read `wf:owner` dynamic property on tame/place; nearest-player attribution
  (reused from the dragon egg pattern).
- `persist.js` — typed get/set dynamic-property helpers (numbers, json blobs) with try/catch.
- `menu.js` — `@minecraft/server-ui` `ActionFormData`/`ModalFormData` wrappers for interact menus
  (pet commands, turret mode toggle, keypad code entry, build-wand options).
- `targeting.js` — family/hostile filters + allowlist logic shared by security turrets/lasers and
  combat pets.
- `fx.js` — particle/sound/molang helpers (laser beam particles, alarm sound, engine loop).

---

## 2. Per-domain plans

### F. Dragons — REWORK  (build first)
**Fresh identifiers** (`wf:drg_ember`, etc.) — clean slate; note that dragons tamed under the old
`MotorDragons.mcaddon` won't carry over (the old pack can be retired). **21 dragons total.**

**Roster**
- *Reworked existing (10):* Ember, Storm, Ancient, Glacier, Inferno, Eclipse (breedable commons);
  Nidhoggr, Apep, Tiamat, Hydra (mythic legends — singular, no breeding).
- *New (11), all breedable commons with eggs:* Nature/Forest, Lightning, Poison, Desert, Spirit,
  Magma, Sea/Tidal, Bone/Undead, Fae, Sun/Light, Shadow.
- Breedable commons w/ owned-egg hatching: **17** (6 existing + 11 new). Mythic non-breeding: **4**.

**Look — distinct body plans (not reskins)**
Each dragon gets its own skeleton/silhouette, chosen per species: western (4-leg + 2 wing), wyvern
(2-leg + wing-arms), serpentine/wingless (Apep, Sea), drake (stocky, small wings), four-winged
(Eclipse, Fae), multi-headed (Tiamat, Hydra). Proportions (neck/tail length, body bulk, wing span,
horn/spine/frill density) vary so silhouettes read as different species at a glance — the dedicated
parametric dragon generator drives this from a per-species parameter block.

**Heavy thematic geometry** — element baked into the model:
- Nature: bark hide, vine tendrils, leaf-frills, flower clusters, antler horns, moss.
- Glacier/Sea: crystal spikes / webbed fins & coral; Storm/Lightning: cloud frills, jagged spark crest.
- Magma/Inferno: molten-rock plates with glowing cracks; Bone/Undead: exposed ribs, skeletal wings.
- Poison: dripping spines, bloated gas sacs; Desert: sand-scoured plates, sidewinder build; Spirit:
  translucent wisps; Fae: iridescent butterfly wings; Sun: radiant crown; Shadow: smoke-tendril body.

**Element FX (all four)** via render/particle/molang:
- **Particle auras** (idle): embers, snow, falling leaves, sparks, gas, motes, etc.
- **Flight trails:** element streak behind the dragon while flying.
- **Breath / element attacks (rider aims + auto-defend):** while ridden, sneak/item trigger fires a
  raycast-aimed element attack where you look; while tamed and *not* ridden, the dragon auto-attacks
  nearby hostiles to defend the owner. Per-element payloads: fire breath (ignite + damage), frost beam
  (slow + damage), vine snare (root + damage), lightning bolt, poison cloud, magma lob, tidal blast,
  necrotic wither, radiant flash, shadow drain. Built on shared `lib/targeting.js`, `lib/fx.js`, and
  a `lib/projectile.js`/`applyDamage` layer.

**Scale:** ~25–40% larger than today, **varied** — mythics dwarf commons; serpents long & lean; drakes
stocky. Collision boxes and seat offsets re-tuned per species; visible_bounds regenerated.

**Mechanics retained/upgraded from the original:** tame-by-food, breed + owned-egg hatching (the proven
`main.js` interval pattern), rideable + `*_flying` group flight (hold jump to climb), no fall damage
while riding, follow-owner, baby/grow-up stages, creative spawn eggs for all 21.

**Files per dragon:** BP entity (tamed/flying/baby/combat groups + events), spawn rule, RP client
entity, distinct geo, multi-region texture, lang, spawn egg; eggs for the 17 commons. Shared:
`dragons/index.js` (breath aim/auto-defend + egg hatching), dragon animation set (idle/walk/fly +
attack), aura/trail particle defs, breath sounds.

**Risks:** 21 distinct skeletons is the single biggest modeling task — fully dependent on the
parametric generator (one well-built generator, 21 parameter blocks). Breath auto-defend must be
perf-bounded (scan throttled, range-gated). Raycast aim uses player view vector + entity raycast.

---

### A. Pets  (build second)
**Content (16+):** realistic — dog (several breeds via variant), cat (variants), rabbit, parrot/bird,
hamster, lizard/gecko, turtle, ferret, fox-kit; fantasy/cute — slime-pet, mini elemental (ember/frost),
mushroom critter, cloud-pup, crystal-fox, etc. Variants via `minecraft:variant` + render-controller
texture arrays to multiply visible breeds without multiplying entities.

**Mechanics**
- Tame (per-pet food), `nameable`, follow-owner.
- **Travel = all modes:** small pets can be *carried* (interact → ride a head/shoulder seat or stored
  to a "pet bed" item); large pets are *rideable* (horse-style); **all** pets *teleport* to the owner
  when they fall too far behind (script interval) so they're never lost.
- **Tricks & commands:** interact opens an `ActionFormData` — Sit / Stay / Follow / Trick. Trick plays
  a one-shot animation (beg, roll, spin) via animation controller + script `triggerEvent`.
- **Leveling = both paths:** XP from kills (combat pets engage nearby hostiles) **and** from
  care/feeding. Level/XP/health persisted per-pet via dynamic properties; level scales health & attack
  via component groups (`wf:pet_lvlN`). Nametag shows `Name  Lv.N`.

**Files per pet:** BP entity (+tamed/baby/level groups, events), spawn rule, RP client entity, geo,
texture(s), lang, spawn egg. Shared: `pets/index.js` (level/xp/teleport/command loops), trick anim
controller, pet-bed item + carry seat entity.

**Risks:** carry-on-shoulder needs a tiny invisible seat entity parented to the player (rideable seat
with offset) — validated approach. Teleport-follow must throttle (every ~2s, only beyond ~24 blocks)
to avoid jitter.

---

### B. Vehicles  (build third)
**Content (15+):** Land — sports car, sedan/SUV, pickup truck, motorbike, quad/ATV, dune buggy, bus,
tank(toy). Air — propeller plane, jet, helicopter, glider, hot-air balloon. Water — speedboat,
jetski, submarine, pontoon. (Spread to hit 15+ across the three media.)

**Mechanics**
- **No fuel** — drive freely.
- **Multi-seat + arcade-fast:** 2–4 `rideable` seats where sensible; zippy speeds; **no fall/collision
  damage** while riding (damage_sensor like dragons).
- **Land:** `navigation`/`movement` + `input_air_controlled`-style ground steering; steer where you
  look; sprint/boost on jump.
- **Air:** reuse the **dragon flight trick** — a `*_flying` component group toggled on rider-enter
  with `has_gravity:false`, `input_air_controlled`, `vertical_movement_action` (hold jump to climb).
- **Water:** `navigation.generic`/`can_swim`, buoyancy via flying-style control on/under water;
  submarine gets vertical control like the air group.
- Passengers: secondary seats with `lock_rider_rotation`.

**Files per vehicle:** BP entity (driving + per-medium movement groups, seat events), RP client entity,
geo (parametric chassis + wheels/rotor/hull), texture, lang, spawn egg, **crafted spawn item** (recipe)
in addition to the creative egg so survival players can build them. Shared: `vehicles/index.js`
(boost, wheel/rotor spin via molang, exit-cleanup), engine sound loop.

**Risks:** ground vehicles can look "floaty"; mitigate with tuned movement + `jump.static` off and
collision box sizing. Rotor/wheel spin is cosmetic via molang `q.modified_move_speed`.

---

### C. Furniture  (build fourth)
**Content (50+ across Modern + Rustic + Medieval):** chairs, stools, sofas/benches, tables (coffee,
dining), beds, lamps/floor-lamps/wall-lights, shelves, drawers/cabinets (storage), wardrobe, kitchen
counter + sink + stove + fridge, bathroom (toilet, sink, tub), rugs, curtains, clocks, plants/pots,
TV, desk. Each as a themed material/color set.

**Mechanics (custom blocks)**
- **Sit-able** chairs/sofas/stools/toilet: custom block component (`registerCustomComponent` →
  `onPlayerInteract`) spawns an invisible `wf:seat` entity at the seat point and mounts the player;
  dismount/cleanup on exit. (Stable block-custom-component API, no experiments.)
- **Lights:** `minecraft:light_emission` on lamp blocks.
- **Storage:** drawers/cabinets/fridge/wardrobe open an `ActionFormData`-backed **virtual inventory**
  persisted to the block (dynamic property keyed by block location) — Bedrock has no stable custom
  container block without experiments, so a script-backed inventory is the reliable path. (Alt: hidden
  bound vanilla chest — noted as fallback if virtual inv proves clunky.)
- **Shapes:** custom block geometry (`models/blocks/*.geo.json`) + `minecraft:geometry` +
  collision/selection boxes; rotation via `minecraft:transformation`/placement component or block
  states + permutations for facing.
- **Variants:** block permutations (block states) for color/material so each "piece" is one block id
  with N looks, craftable/dyeable.

**Files:** per-piece block json (+permutations), block geo + texture, item_texture/terrain_texture
entries, recipes, lang. Shared: `furniture/index.js` registers sit + storage components.

**Risks (the real ones):** (1) script-backed storage UX — must feel like a chest; will prototype on
one drawer first. (2) custom block geometry collision/selection must match the visual so chairs aren't
walk-through. (3) 50+ pieces × 3 styles is large — leaned on permutations + the parametric furniture
generator to keep it sane.

---

### D. HomeBuilding  (build fifth)
**Content:** **35+ materials** — new wood sets (planks/stairs/slabs/fence/door/trapdoor for 3–4 woods),
stone/brick/concrete variants, large glass + glass doors, roofing (angled roof blocks via geo),
exterior trim/siding, flooring (tile/hardwood), pillars/beams. **8 prefabs** — Modern House, Cozy
Cottage, Cabin, Mansion, Tower, Barn, Shop, Starter Base — built **from this pack's own materials**.

**Mechanics**
- Materials = standard custom blocks (stairs/slabs/doors use vanilla-style components; roofing/beams
  use custom geometry). Full recipe tree.
- **Prefabs:** each is a **placer item**. On use, script reads a saved **structure** (`.mcstructure`
  saved via structure manager / `world.structureManager`) and places it at the aimed location with a
  ghost-preview confirm (ActionForm) and rotation choice. Fallback: a `/function` that `setblock`s the
  build if structure placement proves limited. The 8 prefabs are designed and saved during the build.

**Files:** block jsons + geo/textures for materials, item jsons for placers, structure files,
`homebuilding/index.js` (placer logic + preview), recipes, lang.

**Risks:** programmatic structure placement is the unknown; I prototype the placement+rotation+undo on
ONE prefab before authoring all eight. Roofing/beam geometry must tile cleanly.

---

### E. Security  (build last)
**Content (12+ devices):** motion sensor, tripwire/laser tripwire, alarm/siren, security camera,
monitor block, keypad lock, keycard reader + keycard item, owner-only door, auto turret (projectile),
**lethal defensive laser emitter**, floodlight, control panel/hub.

**Mechanics**
- **Sensors & alarms:** sensor block (or paired entity) polls for entities in range (script interval),
  filtered by `targeting.js`; triggers alarm sound + particle + optional redstone-style signal /
  glowing alert.
- **Cameras & monitors:** placing a camera registers a viewpoint; interacting a monitor opens a menu of
  cameras and **spectates** via short script-driven camera teleport / `camera` command from the player
  to the camera location, with an "exit" to return. (Bedrock `/camera` + script.)
- **Locked doors / keypads:** owner-only door checks `wf:owner`; keypad opens a `ModalFormData`
  code entry; keycard reader checks for a `wf:keycard` item (with a stored code). Allowlist of
  player ids via the control hub menu.
- **Turrets + lethal lasers — owner-configurable targeting:** each device has a per-instance mode
  toggle (Hostiles only / + Intruders) stored as a dynamic property and set via interact menu.
  Turret = entity that acquires a target via `targeting.js` and fires (arrow/fireball-style projectile
  or instant `applyDamage`). Laser = continuous beam (particle line) that damages valid targets in
  line-of-sight each tick; **never** harms owner / allowlisted players / owner's pets.

**Files:** block + entity jsons (turret/camera/sensor as entities where motion/aiming is needed),
geo/textures, keycard item, `security/index.js` (sensor loop, camera view, lock checks, turret/laser
targeting + damage + mode menus), sounds (alarm/laser), lang.

**Risks:** the camera-view trick depends on `/camera` behavior + script; prototype first. Laser
damage loop must be performance-bounded (cap active emitters scanned per tick, range-gated).

---

## 3. Cross-cutting quality bar (every domain)
- Detailed multi-bone procedural models (dragon-tier geometry density where the subject warrants it).
- Multi-region textures with intentional palettes; reviewable in Blockbench.
- Every entity: idle/walk + state-specific animations via animation controllers.
- Every identifier has an `en_US.lang` entry (names + spawn eggs + item/block names).
- Crafting recipes for survival-obtainable content (vehicles, furniture, materials, security devices).
- Sounds wired through `sound_definitions.json`.
- Immutable/defensive scripting, try/catch around all entity ops, throttled intervals.

## 4. Validation & "working" guarantee
This environment **cannot launch Minecraft**, so "working" is guaranteed by:
1. `tools/validate.py` — structural + reference + lang + UUID checks on every build.
2. Conformance to verified-working patterns (the shipped Dragons pack) for entities/rideable/flight.
3. Prototyping each **novel** mechanic (script storage, structure placement, camera view, laser damage)
   in isolation on ONE instance before scaling to the full roster, so unknowns surface early.
4. A per-domain manual test checklist in the README for the user to run in-game.
> If you can run the game and report back (or attach logs/screenshots), I'll close the loop on each
> mechanic. Otherwise these four steps are the ceiling on certainty here.

## 5. Sequencing / milestones
1. **M0 — Scaffold:** combined manifests, UUIDs, lib/, toolchain (model+texture generators, validator,
   packager), one trivial test entity end-to-end packaged & validated. *(de-risks the pipeline first)*
2. **M1 — Dragons (rework):** parametric dragon generator + 21 distinct dragons, breath/auto-defend,
   auras/trails, eggs. Produces shared `targeting/fx/projectile` libs. Packaged + validated.
3. **M2 — Pets** complete + packaged.
4. **M3 — Vehicles** folded in.
5. **M4 — Furniture** (prototype sit+storage first).
6. **M5 — HomeBuilding** (prototype prefab placement first).
7. **M6 — Security** (prototype camera+laser first).
8. **M7 — Combined README**, final validation, final `Wildforge.mcaddon`.

## 6. Open decisions (defaults chosen, change anytime)
- Namespace `wf:` and pack name **Wildforge** — assumed; say the word to rename.
- **Dragons reworked into the combined pack with FRESH ids** — the old standalone `MotorDragons.mcaddon`
  is superseded/retired; dragons tamed under it won't carry into the new pack.
- Storage furniture uses script-backed virtual inventory (vs hidden-chest fallback) — will confirm
  after the one-drawer prototype.

## 7. Known Bedrock constraints (and mitigations)
| Want | Constraint | Mitigation |
|---|---|---|
| Sit on furniture | No native block "sit" | invisible seat entity + block custom component |
| Furniture storage | No stable custom container block w/o experiments | script virtual inventory (ActionForm) / hidden chest fallback |
| Prefab placement | Programmatic build is fiddly | structureManager + ghost preview; `/function` fallback |
| Security cameras | No real camera feed | `/camera` spectate teleport via script |
| Lethal lasers | No beam weapon block | particle beam + per-tick range/LOS damage, perf-capped |
