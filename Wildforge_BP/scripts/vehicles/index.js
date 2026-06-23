// vehicles/index.js — spawn a vehicle from its crafted item.
// Driving itself is data-driven (rideable + input_air_controlled groups toggled by
// the wf:drive / wf:park ride events), so the script only handles item spawning.
import { world } from "@minecraft/server";
import { VEHICLE_ITEM, DYE_INDEX } from "./data.js";

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

function recolor(player, vehicle) {
  let item;
  try { item = player.getComponent("minecraft:equippable")?.getEquipment("Mainhand"); }
  catch (_) { return; }
  const idx = DYE_INDEX[item?.typeId];
  if (idx === undefined) return;
  try { vehicle.setProperty("wf:color", idx); } catch (_) { return; }
  try {
    if (!(player.getGameMode && player.getGameMode() === "creative")) {
      const eq = player.getComponent("minecraft:equippable");
      if (item.amount > 1) { item.amount -= 1; eq.setEquipment("Mainhand", item); }
      else eq.setEquipment("Mainhand", undefined);
    }
  } catch (_) {}
}

export function init() {
  world.afterEvents.itemUse.subscribe((ev) => {
    try {
      if (VEHICLE_ITEM[ev.itemStack?.typeId]) spawnFromItem(ev.source, ev.itemStack.typeId);
    } catch (_) {}
  });
  // sneak + dye on a vehicle = paint its body
  world.afterEvents.playerInteractWithEntity.subscribe((ev) => {
    try {
      const t = ev.target;
      if (ev.player?.isSneaking && t?.getComponent("minecraft:type_family")?.hasTypeFamily("wf_vehicle")) {
        recolor(ev.player, t);
      }
    } catch (_) {}
  });
}
