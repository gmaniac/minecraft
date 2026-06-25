// perf.js — cheap entity culling for the per-tick loops.
// Skip dimensions with no players, and skip entities far outside any player's view
// range, so dormant dragons/devices don't cost updates when nobody's around.
import { world } from "@minecraft/server";

export const ACTIVE_RANGE = 80;        // blocks; beyond this an entity isn't ticked

export function playersByDimension() {
  const map = {};
  for (const p of world.getAllPlayers()) {
    (map[p.dimension.id] ??= []).push(p);
  }
  return map;
}

export function nearAnyPlayer(location, players, range = ACTIVE_RANGE) {
  const r2 = range * range;
  for (const p of players) {
    const d = p.location;
    const dx = d.x - location.x, dy = d.y - location.y, dz = d.z - location.z;
    if (dx * dx + dy * dy + dz * dz <= r2) return true;
  }
  return false;
}
