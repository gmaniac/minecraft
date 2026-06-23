// furniture/index.js — sit-able seats and script-backed storage for custom blocks.
import { world, system, ItemStack } from "@minecraft/server";
import { ActionFormData } from "@minecraft/server-ui";
import { SEAT_Y } from "./data.js";
import { getJson, setJson } from "../lib/persist.js";

const DIMS = ["overworld", "nether", "the_end"];

// ---- block custom components (must register at startup) ----
system.beforeEvents.startup.subscribe((ev) => {
  const reg = ev.blockComponentRegistry;
  try {
    reg.registerCustomComponent("wf:seat", {
      onPlayerInteract(e) { try { sit(e.player, e.block); } catch (_) {} },
    });
    reg.registerCustomComponent("wf:storage", {
      onPlayerInteract(e) { try { openStorage(e.player, e.block); } catch (_) {} },
    });
  } catch (_) {}
});

function seatCenter(block) {
  const off = SEAT_Y[block.typeId] ?? 0.4;
  return { x: block.x + 0.5, y: block.y + off, z: block.z + 0.5 };
}

function sit(player, block) {
  if (player.isSneaking) return;                 // sneak-interact reserved for future
  const loc = seatCenter(block);
  // don't double-seat the same block
  let near;
  try { near = block.dimension.getEntities({ type: "wf:seat", location: loc, maxDistance: 0.6 }); }
  catch (_) { near = []; }
  for (const s of near) {
    const r = s.getComponent("minecraft:rideable");
    if (r && r.getRiders().length) return;       // occupied
  }
  let seat = near[0];
  if (!seat) {
    try { seat = block.dimension.spawnEntity("wf:seat", loc); } catch (_) { return; }
  }
  try { seat.getComponent("minecraft:rideable")?.addRider(player); } catch (_) {}
}

function storeKey(block) {
  return `wf:store:${block.dimension.id}|${block.x},${block.y},${block.z}`;
}

async function openStorage(player, block) {
  const key = storeKey(block);
  const items = getJson(world, key, []);
  const form = new ActionFormData()
    .title("Storage")
    .body(items.length ? `${items.length} stack(s) stored` : "Empty — deposit your held item");
  for (const it of items) form.button(`Take ${pretty(it.typeId)} x${it.amount}`);
  form.button("§2Deposit held item");
  let res;
  try { res = await form.show(player); } catch (_) { return; }
  if (res.canceled) return;
  if (res.selection === items.length) {
    depositHeld(player, items);
  } else {
    withdraw(player, items, res.selection);
  }
  setJson(world, key, items);
}

function pretty(typeId) {
  return typeId.replace(/^.*:/, "").replace(/_/g, " ");
}

function depositHeld(player, items) {
  try {
    const eq = player.getComponent("minecraft:equippable");
    const held = eq?.getEquipment("Mainhand");
    if (!held) return;
    items.push({ typeId: held.typeId, amount: held.amount });
    eq.setEquipment("Mainhand", undefined);
  } catch (_) {}
}

function withdraw(player, items, idx) {
  const it = items[idx];
  if (!it) return;
  try {
    const inv = player.getComponent("minecraft:inventory")?.container;
    inv?.addItem(new ItemStack(it.typeId, it.amount));
    items.splice(idx, 1);
  } catch (_) {}
}

// remove empty seat entities so they don't accumulate
function cleanupSeats() {
  for (const dimId of DIMS) {
    let dim;
    try { dim = world.getDimension(dimId); } catch (_) { continue; }
    let seats;
    try { seats = dim.getEntities({ type: "wf:seat" }); } catch (_) { continue; }
    for (const s of seats) {
      const r = s.getComponent("minecraft:rideable");
      if (!r || r.getRiders().length === 0) { try { s.remove(); } catch (_) {} }
    }
  }
}

export function init() {
  system.runInterval(cleanupSeats, 20);
}
