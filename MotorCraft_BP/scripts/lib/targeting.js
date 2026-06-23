// targeting.js — shared target acquisition for dragon breath auto-defend,
// combat pets and security turrets/lasers.
import { getOwnerId } from "./owner.js";

// Vanilla hostile family members worth defending against. Kept as a family check
// so modded-but-hostile mobs that adopt the "monster" family are covered too.
const HOSTILE_FAMILIES = [
  "monster", "zombie", "skeleton", "creeper", "spider", "pillager",
  "illager", "blaze", "ghast", "slime", "witch", "undead",
];

export function isHostile(entity) {
  try {
    const fam = entity.getComponent("minecraft:type_family");
    if (!fam) return false;
    return HOSTILE_FAMILIES.some((f) => fam.hasTypeFamily(f));
  } catch (_) {
    return false;
  }
}

export function isPlayer(entity) {
  return entity?.typeId === "minecraft:player";
}

// Entities owned by `ownerId` (so a turret/dragon never hits its master's pets).
function isFriendlyTo(entity, ownerId) {
  if (!ownerId) return false;
  try {
    return getOwnerId(entity) === ownerId;
  } catch (_) {
    return false;
  }
}

/**
 * Acquire the nearest valid target around `from`.
 * mode: "hostiles" | "intruders"
 *   hostiles  -> hostile mobs only
 *   intruders -> hostile mobs AND non-owner players
 * Never returns the owner, owner's pets, or the source entity itself.
 */
export function acquireTarget(from, { radius = 16, mode = "hostiles", ownerId } = {}) {
  let candidates;
  try {
    candidates = from.dimension.getEntities({
      location: from.location,
      maxDistance: radius,
    });
  } catch (_) {
    return undefined;
  }
  let best;
  let bestSq = Infinity;
  const o = from.location;
  for (const e of candidates) {
    if (!e || e.id === from.id) continue;
    if (isFriendlyTo(e, ownerId)) continue;
    let valid = false;
    if (isHostile(e)) valid = true;
    else if (mode === "intruders" && isPlayer(e) && e.id !== ownerId) valid = true;
    if (!valid) continue;
    const l = e.location;
    const dx = l.x - o.x, dy = l.y - o.y, dz = l.z - o.z;
    const sq = dx * dx + dy * dy + dz * dz;
    if (sq < bestSq) { bestSq = sq; best = e; }
  }
  return best;
}
