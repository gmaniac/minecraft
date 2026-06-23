// vehicles/index.js — spawn a vehicle from its crafted item.
// Driving itself is data-driven (rideable + input_air_controlled groups toggled by
// the wf:drive / wf:park ride events), so the script only handles item spawning.
import { world } from "@minecraft/server";
import { VEHICLE_ITEM } from "./data.js";

function spawnFromItem(player, itemId) {
  const entityId = VEHICLE_ITEM[itemId];
  if (!entityId) return;
  const l = player.location;
  const d = player.getViewDirection();
  const at = { x: l.x + d.x * 2.5, y: l.y + 0.5, z: l.z + d.z * 2.5 };
  let ok = false;
  try { player.dimension.spawnEntity(entityId, at); ok = true; } catch (_) {}
  if (!ok) return;
  // consume one item (skip in creative)
  try {
    if (player.getGameMode && player.getGameMode() === "creative") return;
    const eq = player.getComponent("minecraft:equippable");
    const item = eq?.getEquipment("Mainhand");
    if (!item) return;
    if (item.amount > 1) { item.amount -= 1; eq.setEquipment("Mainhand", item); }
    else eq.setEquipment("Mainhand", undefined);
  } catch (_) {}
}

export function init() {
  world.afterEvents.itemUse.subscribe((ev) => {
    try {
      if (VEHICLE_ITEM[ev.itemStack?.typeId]) spawnFromItem(ev.source, ev.itemStack.typeId);
    } catch (_) {}
  });
}
