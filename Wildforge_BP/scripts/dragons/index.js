// dragons/index.js — breath attacks (rider-aimed + auto-defend) and egg hatching.
import { world, system } from "@minecraft/server";
import { DRAGON_ELEMENT, BREATH, EGG_MAP } from "./data.js";
import { registerEgg } from "../lib/hatch.js";
import { acquireTarget } from "../lib/targeting.js";
import { getOwnerId } from "../lib/owner.js";
import { spawnParticle, playSound, rayPoints, normalize } from "../lib/fx.js";
import { playersByDimension, nearAnyPlayer } from "../lib/perf.js";

const HATCH_TICKS = 90 * 20;     // ~90s, matches the reworked dragons
const BREATH_LEN = 12;           // blocks
const CONE = 0.6;                // dot-product cone half-angle
const RIDER_CD = 18;             // ticks between rider breaths
const DEFEND_CD = 40;            // ticks between auto-defend breaths
const DEFEND_RANGE = 16;
const DIMS = ["overworld", "nether", "the_end"];
const CD_KEY = "wf:breath_cd";

function headLoc(dragon) {
  try { return dragon.getHeadLocation(); } catch (_) {}
  const l = dragon.location;
  return { x: l.x, y: l.y + 1.4, z: l.z };
}

function onCooldown(dragon, cd) {
  let last = 0;
  try { last = dragon.getDynamicProperty(CD_KEY) ?? 0; } catch (_) {}
  if (system.currentTick - last < cd) return true;
  try { dragon.setDynamicProperty(CD_KEY, system.currentTick); } catch (_) {}
  return false;
}

function fireBreath(dragon, dir, element) {
  const b = BREATH[element] || { particle: "minecraft:basic_flame_particle", dmg: 5 };
  const origin = headLoc(dragon);
  const d = normalize(dir);
  const dim = dragon.dimension;
  // visual beam
  for (const p of rayPoints(origin, d, BREATH_LEN, 0.8)) spawnParticle(dim, b.particle, p);
  if (b.sound) playSound(dragon, b.sound, { volume: 1.4, pitch: 1.0 });
  // cone damage
  let victims;
  try {
    victims = dim.getEntities({ location: origin, maxDistance: BREATH_LEN });
  } catch (_) { return; }
  const ownerId = getOwnerId(dragon);
  for (const e of victims) {
    if (!e || e.id === dragon.id) continue;
    if (e.typeId === "minecraft:player" && e.id === ownerId) continue;
    if (getOwnerId(e) === ownerId && ownerId) continue;       // spare owner's pets
    const l = e.location;
    const v = normalize({ x: l.x - origin.x, y: l.y - origin.y, z: l.z - origin.z });
    if (v.x * d.x + v.y * d.y + v.z * d.z < CONE) continue;   // outside the cone
    try { e.applyDamage(b.dmg, { cause: "entityAttack", damagingEntity: dragon }); } catch (_) {}
    try { if (b.fire) e.setOnFire(4, true); } catch (_) {}
    try { if (b.poison) e.addEffect("poison", 100, { amplifier: 1 }); } catch (_) {}
    try { if (b.slow) e.addEffect("slowness", 80, { amplifier: 2 }); } catch (_) {}
    try { if (b.wither) e.addEffect("wither", 80, { amplifier: 1 }); } catch (_) {}
    try { if (b.kb) e.applyKnockback({ x: d.x, z: d.z }, 1.4); } catch (_) {}
  }
}

// ---- rider-aimed breath: right-click (use item) while riding a dragon ----
function onItemUse(player) {
  let mount;
  try { mount = player.getComponent("minecraft:riding")?.entityRidingOn; } catch (_) {}
  if (!mount) return;
  const element = DRAGON_ELEMENT[mount.typeId];
  if (!element) return;
  if (onCooldown(mount, RIDER_CD)) return;
  try { fireBreath(mount, player.getViewDirection(), element); } catch (_) {}
}

// ---- auto-defend: tamed, un-ridden dragons breathe at nearby hostiles ----
function defendTick() {
  const byDim = playersByDimension();
  for (const dimId of DIMS) {
    const players = byDim[dimId];
    if (!players) continue;
    let dim;
    try { dim = world.getDimension(dimId); } catch (_) { continue; }
    let dragons;
    try { dragons = dim.getEntities({ families: ["wf_dragon"] }); } catch (_) { continue; }
    for (const dragon of dragons) {
      const element = DRAGON_ELEMENT[dragon.typeId];
      if (!element) continue;
      if (!nearAnyPlayer(dragon.location, players)) continue;
      if (!dragon.getComponent("minecraft:is_tamed")) continue;
      let riders = [];
      try { riders = dragon.getComponent("minecraft:rideable")?.getRiders() ?? []; } catch (_) {}
      if (riders.length) continue;                       // rider is in control
      const ownerId = getOwnerId(dragon);
      const target = acquireTarget(dragon, { radius: DEFEND_RANGE, mode: "hostiles", ownerId });
      if (!target) continue;
      if (onCooldown(dragon, DEFEND_CD)) continue;
      const o = headLoc(dragon), l = target.location;
      fireBreath(dragon, { x: l.x - o.x, y: l.y - o.y, z: l.z - o.z }, element);
    }
  }
}

export function init() {
  for (const [eggId, dragonId] of Object.entries(EGG_MAP)) {
    registerEgg(eggId, dragonId, HATCH_TICKS, "wf:set_baby");
  }
  world.afterEvents.itemUse.subscribe((ev) => {
    try { onItemUse(ev.source); } catch (_) {}
  });
  system.runInterval(defendTick, 10);
}
