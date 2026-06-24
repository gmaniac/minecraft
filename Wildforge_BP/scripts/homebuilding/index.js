// homebuilding/index.js — place a prefab structure from its crafted placer item.
import { world, system, BlockPermutation } from "@minecraft/server";
import { PREFABS } from "./data.js";

const SLICE = 200;        // blocks placed per tick (keeps placement smooth)

// rotate a local (x,z) by r quarter-turns
function rot(x, z, r) {
  if (r === 1) return [-z, x];
  if (r === 2) return [-x, -z];
  if (r === 3) return [z, -x];
  return [x, z];
}

function facingRot(player) {
  const d = player.getViewDirection();
  if (Math.abs(d.x) > Math.abs(d.z)) return d.x > 0 ? 3 : 1;   // east / west
  return d.z > 0 ? 0 : 2;                                       // south / north
}

function placePrefab(player, def) {
  const r = facingRot(player);
  const dim = player.dimension;
  const d = player.getViewDirection();
  const ox = Math.floor(player.location.x + d.x * 3);
  const oy = Math.floor(player.location.y);
  const oz = Math.floor(player.location.z + d.z * 3);
  const blocks = def.blocks;
  // cache resolved permutations so we resolve each block type once
  const cache = {};
  let i = 0, placed = 0;
  const step = () => {
    let n = 0;
    while (i < blocks.length && n < SLICE) {
      const [x, y, z, b] = blocks[i++]; n++;
      let perm = cache[b];
      if (perm === undefined) {
        try { perm = BlockPermutation.resolve(b); } catch (_) { perm = null; }
        cache[b] = perm;
      }
      if (!perm) continue;
      const [rx, rz] = rot(x, z, r);
      try { dim.getBlock({ x: ox + rx, y: oy + y, z: oz + rz })?.setPermutation(perm); placed++; }
      catch (_) {}
    }
    if (i < blocks.length) system.runTimeout(step, 1);
    else { try { player.sendMessage(`§a${def.name} built — ${placed} blocks.`); } catch (_) {} }
  };
  step();
}

function onUse(player, itemId) {
  const def = PREFABS[itemId];
  if (!def) return;
  try { player.sendMessage(`§7Building ${def.name}…`); } catch (_) {}
  // consume one placer (skip in creative)
  try {
    if (!(player.getGameMode && player.getGameMode() === "creative")) {
      const eq = player.getComponent("minecraft:equippable");
      const it = eq?.getEquipment("Mainhand");
      if (it) {
        if (it.amount > 1) { it.amount -= 1; eq.setEquipment("Mainhand", it); }
        else eq.setEquipment("Mainhand", undefined);
      }
    }
  } catch (_) {}
  // defer out of the event so world mutation is always allowed
  system.run(() => placePrefab(player, def));
}

export function init() {
  world.afterEvents.itemUse.subscribe((ev) => {
    try { if (PREFABS[ev.itemStack?.typeId]) onUse(ev.source, ev.itemStack.typeId); } catch (_) {}
  });
}
