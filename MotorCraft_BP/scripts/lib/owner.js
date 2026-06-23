// owner.js — ownership attribution shared by dragons, pets and security devices.
import { world } from "@minecraft/server";
import { getStr, setStr } from "./persist.js";

export const OWNER_KEY = "motor:owner";

// Nearest player within `radius` of an entity, same dimension. Used to attribute
// freshly-spawned owned entities (eggs, baby mobs) to whoever was standing there.
export function nearestPlayer(entity, radius = 6) {
  let best;
  let bestSq = radius * radius + 0.001;
  const { x, y, z } = entity.location;
  for (const p of world.getAllPlayers()) {
    if (p.dimension.id !== entity.dimension.id) continue;
    const d = p.location;
    const dx = d.x - x, dy = d.y - y, dz = d.z - z;
    const sq = dx * dx + dy * dy + dz * dz;
    if (sq <= bestSq) { bestSq = sq; best = p; }
  }
  return best;
}

export function setOwner(entity, playerId) {
  setStr(entity, OWNER_KEY, playerId);
}

export function getOwnerId(entity) {
  return getStr(entity, OWNER_KEY);
}

export function getOwnerPlayer(entity) {
  const id = getOwnerId(entity);
  if (typeof id !== "string") return undefined;
  return world.getAllPlayers().find((p) => p.id === id);
}

export function isOwner(entity, player) {
  return !!player && getOwnerId(entity) === player.id;
}
