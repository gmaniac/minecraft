// security/index.js — sensors, tripwires, turrets, lethal lasers, cameras,
// owner doors, keypads, sirens and a control hub. Owner-configurable targeting.
import { world, system, MolangVariableMap } from "@minecraft/server";
import { ActionFormData, ModalFormData } from "@minecraft/server-ui";
import { ACTIVE_KIND, DEVICE_ITEM, BLOCK_COMPONENTS, SEC_BLOCKS, CAMERA_ID, KEYCARD,
  DYE_INDEX, HEX } from "./data.js";
import { nearestPlayer, setOwner, getOwnerId } from "../lib/owner.js";
import { acquireTarget, isHostile } from "../lib/targeting.js";
import { getStr, setStr, getBool, setBool, getNum, setNum, getJson, setJson } from "../lib/persist.js";
import { spawnParticle, playSound, rayPoints, normalize } from "../lib/fx.js";

const DIMS = ["overworld", "nether", "the_end"];
const R = { sensor: 10, turret: 16 };
const CD = { sensor: 40, turret: 25, tripalarm: 30 };
const DMG = { turret: 6, laser: 4, tripwire: 3 };
const BEAM_LEN = 24, BEAM_STEP = 0.1, BEAM_RADIUS = 1.0;
const MODE_KEY = "wf:mode", ARM_KEY = "wf:armed", CD_KEY = "wf:cd";
const BVX = "wf:bvx", BVZ = "wf:bvz", LCOLOR = "wf:lcolor", DEFAULT_COLOR = 14;  // red

function hexRgb(hex) {
  const h = hex.replace("#", "");
  return { red: parseInt(h.slice(0, 2), 16) / 255, green: parseInt(h.slice(2, 4), 16) / 255,
           blue: parseInt(h.slice(4, 6), 16) / 255 };
}

// ---------- ownership / allowlist ----------
const bKey = (b) => `wf:bowner:${b.dimension.id}|${b.x},${b.y},${b.z}`;
const blockOwner = (b) => getStr(world, bKey(b));
const setBlockOwner = (b, id) => setStr(world, bKey(b), id);

function allowList(ownerId) { return getJson(world, `wf:allow:${ownerId}`, []); }
function isAllowed(ownerId, playerId) {
  return playerId === ownerId || allowList(ownerId).includes(playerId);
}

function validTarget(dev, ownerId, mode) {
  const t = acquireTarget(dev, { radius: R[ACTIVE_KIND[dev.typeId]] || 12, mode, ownerId });
  if (!t) return undefined;
  if (t.typeId === "minecraft:player" && isAllowed(ownerId, t.id)) return undefined;
  return t;
}

function onCd(dev, ticks) {
  if (system.currentTick - (dev.getDynamicProperty(CD_KEY) ?? 0) < ticks) return true;
  try { dev.setDynamicProperty(CD_KEY, system.currentTick); } catch (_) {}
  return false;
}

function devOrigin(dev) {
  const l = dev.location;
  return { x: l.x, y: l.y + 0.6, z: l.z };
}

// tracer beam toward a target (turret)
function beam(dev, target, particle) {
  const o = devOrigin(dev), l = target.location;
  const dir = normalize({ x: l.x - o.x, y: l.y + 1 - o.y, z: l.z - o.z });
  const len = Math.min(20, Math.hypot(l.x - o.x, l.y - o.y, l.z - o.z));
  for (const p of rayPoints(o, dir, len, 0.7)) spawnParticle(dev.dimension, particle, p);
}

// device's beam direction (set from the placer's facing) and color
function beamDir(dev) {
  return normalize({ x: getNum(dev, BVX, 0), y: 0, z: getNum(dev, BVZ, 1) });
}
function devColor(dev) {
  return hexRgb(HEX[getNum(dev, LCOLOR, DEFAULT_COLOR)] || HEX[DEFAULT_COLOR]);
}

// length until the beam meets a solid block (capped)
function beamLength(dim, o, dir) {
  try {
    const hit = dim.getBlockFromRay(o, dir, { maxDistance: BEAM_LEN, includePassableBlocks: false });
    if (hit?.block) {
      const b = hit.block;
      return Math.min(BEAM_LEN, Math.hypot(b.x + 0.5 - o.x, b.y + 0.5 - o.y, b.z + 0.5 - o.z));
    }
  } catch (_) {}
  return BEAM_LEN;
}

// draw the continuous beam: white-hot core layered over a colored glow halo
function drawBeam(dim, o, dir, len, rgb) {
  const m = new MolangVariableMap();
  try { m.setColorRGB("variable.color", rgb); } catch (_) {}
  const n = Math.max(1, Math.floor(len / BEAM_STEP));
  for (let i = 1; i <= n; i++) {
    const p = { x: o.x + dir.x * BEAM_STEP * i, y: o.y + dir.y * BEAM_STEP * i,
                z: o.z + dir.z * BEAM_STEP * i };
    try { dim.spawnParticle("wf:laser_glow", p, m); } catch (_) {}   // colored halo
    try { dim.spawnParticle("wf:laser_core", p); } catch (_) {}      // bright white centre
  }
}

function isBeamTarget(e, ownerId, mode) {
  if (e.typeId === "minecraft:player") {
    if (e.id === ownerId || isAllowed(ownerId, e.id)) return false;
    return mode === "intruders";
  }
  if (ownerId && getOwnerId(e) === ownerId) return false;   // owner's pets
  return isHostile(e);
}

// entities crossing the beam segment
function beamHits(dev, o, dir, len, ownerId, mode) {
  let cands;
  try { cands = dev.dimension.getEntities({ location: o, maxDistance: len + 1 }); }
  catch (_) { return []; }
  const hits = [];
  for (const e of cands) {
    if (!e || e.id === dev.id || !isBeamTarget(e, ownerId, mode)) continue;
    const l = e.location;
    const vx = l.x - o.x, vy = l.y + 0.9 - o.y, vz = l.z - o.z;
    const t = vx * dir.x + vy * dir.y + vz * dir.z;
    if (t < 0 || t > len) continue;
    if (Math.hypot(vx - dir.x * t, vy - dir.y * t, vz - dir.z * t) < BEAM_RADIUS) hits.push(e);
  }
  return hits;
}

function alarm(dev, ownerId, msg) {
  playSound(dev, "mob.wolf.bark", { volume: 1.6, pitch: 0.6 });
  spawnParticle(dev.dimension, "minecraft:villager_angry", { ...dev.location, y: dev.location.y + 1.5 });
  const owner = world.getAllPlayers().find((p) => p.id === ownerId);
  if (owner) try { owner.sendMessage(msg); } catch (_) {}
}

// ---------- active device tick ----------
function tick() {
  for (const dimId of DIMS) {
    let dim;
    try { dim = world.getDimension(dimId); } catch (_) { continue; }
    let devs;
    try { devs = dim.getEntities({ families: ["wf_security_active"] }); } catch (_) { continue; }
    for (const dev of devs) {
      const kind = ACTIVE_KIND[dev.typeId];
      if (!kind) continue;
      if (!getBool(dev, ARM_KEY, true)) continue;
      const ownerId = getOwnerId(dev);
      const mode = getStr(dev, MODE_KEY, "hostiles");
      if (kind === "sensor") {
        const t = validTarget(dev, ownerId, mode);
        if (t && !onCd(dev, CD.sensor)) {
          const l = t.location;
          alarm(dev, ownerId, `§c⚠ Intruder detected near §f${Math.round(l.x)}, ${Math.round(l.y)}, ${Math.round(l.z)}`);
        }
      } else if (kind === "turret") {
        const t = validTarget(dev, ownerId, mode);
        if (t && !onCd(dev, CD.turret)) {
          beam(dev, t, "minecraft:basic_crit_particle");
          hurt(dev, t, DMG.turret);
          playSound(dev, "random.bow", { volume: 1.2 });
        }
      } else if (kind === "tripwire" || kind === "laser") {
        // continuous, always-visible colored beam in the device's facing direction
        const o = devOrigin(dev), dir = beamDir(dev);
        const len = beamLength(dev.dimension, o, dir);
        drawBeam(dev.dimension, o, dir, len, devColor(dev));
        const hits = beamHits(dev, o, dir, len, ownerId, mode);
        if (kind === "laser") {
          for (const h of hits) hurt(dev, h, DMG.laser);        // continuous lethal damage
        } else if (hits.length) {                               // tripwire: alarm + light zap
          for (const h of hits) hurt(dev, h, DMG.tripwire);
          if (!onCd(dev, CD.tripalarm)) alarm(dev, ownerId, "§c⚠ Laser tripwire crossed!");
        }
      }
    }
  }
}

function hurt(dev, target, dmg) {
  try { target.applyDamage(dmg, { cause: "entityAttack", damagingEntity: dev }); } catch (_) {}
}

// ---------- device items spawn the entity ----------
function spawnDevice(player, itemId) {
  const entId = DEVICE_ITEM[itemId];
  if (!entId) return;
  const l = player.location, d = player.getViewDirection();
  let dev;
  try { dev = player.dimension.spawnEntity(entId, { x: l.x + d.x * 2, y: l.y, z: l.z + d.z * 2 }); }
  catch (_) { return; }
  setOwner(dev, player.id);
  setBool(dev, ARM_KEY, true);
  setStr(dev, MODE_KEY, "hostiles");
  // beam points where the placer was looking (horizontal); default color red
  const h = normalize({ x: d.x, y: 0, z: d.z });
  setNum(dev, BVX, h.x);
  setNum(dev, BVZ, h.z);
  setNum(dev, LCOLOR, DEFAULT_COLOR);
  consumeHeld(player);
}

// hold a dye and interact a laser/tripwire to set its beam colour
function recolorBeam(player, dev) {
  let item;
  try { item = player.getComponent("minecraft:equippable")?.getEquipment("Mainhand"); }
  catch (_) { return false; }
  const idx = DYE_INDEX[item?.typeId];
  if (idx === undefined) return false;
  setNum(dev, LCOLOR, idx);
  playSound(player, "random.orb", { volume: 0.5 });
  try { player.sendMessage("§aBeam colour set."); } catch (_) {}
  return true;
}

function consumeHeld(player) {
  try {
    if (player.getGameMode && player.getGameMode() === "creative") return;
    const eq = player.getComponent("minecraft:equippable");
    const it = eq?.getEquipment("Mainhand");
    if (!it) return;
    if (it.amount > 1) { it.amount -= 1; eq.setEquipment("Mainhand", it); }
    else eq.setEquipment("Mainhand", undefined);
  } catch (_) {}
}

// ---------- cameras ----------
function cameras() { return getJson(world, "wf:cameras", []); }
function saveCameras(list) { setJson(world, "wf:cameras", list); }

function registerCamera(block, ownerId) {
  const list = cameras();
  list.push({ dim: block.dimension.id, x: block.x, y: block.y, z: block.z,
    name: `Camera ${list.length + 1}`, owner: ownerId });
  saveCameras(list);
}
function unregisterCamera(block) {
  saveCameras(cameras().filter((c) =>
    !(c.dim === block.dimension.id && c.x === block.x && c.y === block.y && c.z === block.z)));
}

async function openMonitor(player) {
  const mine = cameras().filter((c) => c.owner === player.id);
  const form = new ActionFormData().title("Security Monitor")
    .body(mine.length ? "Select a camera to view:" : "No cameras placed yet.");
  for (const c of mine) form.button(c.name);
  form.button("§cExit view");
  let res;
  try { res = await form.show(player); } catch (_) { return; }
  if (res.canceled) return;
  if (res.selection === mine.length) { clearView(player); return; }
  const c = mine[res.selection];
  try {
    player.camera.setCamera("minecraft:free", {
      location: { x: c.x + 0.5, y: c.y + 0.5, z: c.z + 0.5 }, rotation: { x: 10, y: 0 } });
    setBool(player, "wf:viewing", true);
    player.sendMessage("§7Sneak to exit camera view.");
  } catch (_) {}
}
function clearView(player) {
  try { player.camera.clear(); } catch (_) {}
  setBool(player, "wf:viewing", false);
}

// ---------- doors / keypad / siren / hub ----------
function toggleDoor(player, block) {
  const ownerId = blockOwner(block);
  const held = heldItem(player);
  const ok = !ownerId || isAllowed(ownerId, player.id) || held === KEYCARD;
  if (!ok) { playSound(player, "note.bass", { pitch: 0.6 }); player.sendMessage("§c🔒 Locked"); return; }
  try {
    const open = block.permutation.getState("wf:open");
    block.setPermutation(block.permutation.withState("wf:open", !open));
    playSound(player, "open.iron_door");
  } catch (_) {}
}

function heldItem(player) {
  try { return player.getComponent("minecraft:equippable")?.getEquipment("Mainhand")?.typeId; }
  catch (_) { return undefined; }
}

const codeKey = (b) => `wf:code:${b.dimension.id}|${b.x},${b.y},${b.z}`;

async function keypad(player, block) {
  const ownerId = blockOwner(block);
  const stored = getStr(world, codeKey(block));
  const isOwner = !ownerId || ownerId === player.id;
  const form = new ModalFormData().title("Keypad")
    .textField(stored ? "Enter code" : "Set a new code", "1234");
  let res;
  try { res = await form.show(player); } catch (_) { return; }
  if (res.canceled) return;
  const code = res.formValues?.[0];
  if (!stored) {
    if (isOwner) { setStr(world, codeKey(block), code); player.sendMessage("§aCode set."); }
    return;
  }
  if (code === stored) { openNearestDoor(block); playSound(player, "random.orb"); }
  else { player.sendMessage("§cWrong code"); playSound(player, "note.bass", { pitch: 0.5 }); }
}

function openNearestDoor(block) {
  for (let dx = -4; dx <= 4; dx++) for (let dy = -2; dy <= 2; dy++) for (let dz = -4; dz <= 4; dz++) {
    let b;
    try { b = block.dimension.getBlock({ x: block.x + dx, y: block.y + dy, z: block.z + dz }); }
    catch (_) { continue; }
    if (b?.typeId === "wf:owner_door") {
      try { b.setPermutation(b.permutation.withState("wf:open", true)); } catch (_) {}
      return;
    }
  }
}

function siren(player, block) {
  let n = 0;
  const id = system.runInterval(() => {
    playSound(player, "mob.wolf.bark", { volume: 2.0, pitch: 0.5 });
    spawnParticle(block.dimension, "minecraft:villager_angry",
      { x: block.x + 0.5, y: block.y + 1.2, z: block.z + 0.5 });
    if (++n >= 6) system.clearRun(id);
  }, 10);
}

async function hub(player, block) {
  let ownerId = blockOwner(block);
  if (!ownerId) { setBlockOwner(block, player.id); ownerId = player.id; }
  if (ownerId !== player.id) { player.sendMessage("§cNot your hub."); return; }
  const sel = await new ActionFormData().title("Control Hub").body("Manage your security network")
    .button("Arm all devices").button("Disarm all devices")
    .button("Targeting: Hostiles only").button("Targeting: + Intruders")
    .button("Add nearby players to allowlist").show(player).then((r) => r.canceled ? -1 : r.selection)
    .catch(() => -1);
  if (sel < 0) return;
  if (sel === 0 || sel === 1) setAll(player.id, ARM_KEY, sel === 0);
  else if (sel === 2 || sel === 3) setAllMode(player.id, sel === 2 ? "hostiles" : "intruders");
  else if (sel === 4) addNearbyAllow(player);
  player.sendMessage("§aHub updated.");
}

function eachOwnedDevice(ownerId, fn) {
  for (const dimId of DIMS) {
    let dim;
    try { dim = world.getDimension(dimId); } catch (_) { continue; }
    let devs;
    try { devs = dim.getEntities({ families: ["wf_security_active"] }); } catch (_) { continue; }
    for (const d of devs) if (getOwnerId(d) === ownerId) fn(d);
  }
}
function setAll(ownerId, key, val) { eachOwnedDevice(ownerId, (d) => setBool(d, key, val)); }
function setAllMode(ownerId, mode) { eachOwnedDevice(ownerId, (d) => setStr(d, MODE_KEY, mode)); }

function addNearbyAllow(player) {
  const list = allowList(player.id);
  for (const p of world.getAllPlayers()) {
    if (p.id === player.id) continue;
    const a = p.location, b = player.location;
    if (Math.hypot(a.x - b.x, a.y - b.y, a.z - b.z) <= 12 && !list.includes(p.id)) list.push(p.id);
  }
  setJson(world, `wf:allow:${player.id}`, list);
}

// ---------- registration ----------
system.beforeEvents.startup.subscribe((ev) => {
  const reg = ev.blockComponentRegistry;
  const handlers = {
    "wf:camera": () => {},                                         // passive; registry on place
    "wf:monitor": (e) => openMonitor(e.player),
    "wf:door": (e) => toggleDoor(e.player, e.block),
    "wf:keypad": (e) => keypad(e.player, e.block),
    "wf:siren": (e) => siren(e.player, e.block),
    "wf:hub": (e) => hub(e.player, e.block),
  };
  for (const name of BLOCK_COMPONENTS) {
    try {
      reg.registerCustomComponent(name, {
        onPlayerInteract(e) { try { handlers[name]?.(e); } catch (_) {} },
      });
    } catch (_) {}
  }
});

export function init() {
  // owner attribution on device spawn (covers spawn eggs too)
  world.afterEvents.entitySpawn.subscribe(({ entity }) => {
    try {
      if (ACTIVE_KIND[entity?.typeId] && !getOwnerId(entity)) {
        const p = nearestPlayer(entity, 8);
        if (p) setOwner(entity, p.id);
        setBool(entity, ARM_KEY, true);
        setStr(entity, MODE_KEY, "hostiles");
      }
    } catch (_) {}
  });

  // device items
  world.afterEvents.itemUse.subscribe((ev) => {
    try { if (DEVICE_ITEM[ev.itemStack?.typeId]) spawnDevice(ev.source, ev.itemStack.typeId); }
    catch (_) {}
  });

  // dye + interact a laser/tripwire -> recolour its beam
  world.afterEvents.playerInteractWithEntity.subscribe((ev) => {
    try {
      const k = ACTIVE_KIND[ev.target?.typeId];
      if (k === "laser" || k === "tripwire") recolorBeam(ev.player, ev.target);
    } catch (_) {}
  });

  // block ownership + camera registry
  world.afterEvents.playerPlaceBlock.subscribe((ev) => {
    try {
      if (!SEC_BLOCKS.includes(ev.block.typeId)) return;
      setBlockOwner(ev.block, ev.player.id);
      if (ev.block.typeId === CAMERA_ID) registerCamera(ev.block, ev.player.id);
    } catch (_) {}
  });
  world.afterEvents.playerBreakBlock.subscribe((ev) => {
    try { if (ev.brokenBlockPermutation?.type?.id === CAMERA_ID) unregisterCamera(ev.block); }
    catch (_) {}
  });

  // exit camera view on sneak
  system.runInterval(() => {
    for (const p of world.getAllPlayers()) {
      if (getBool(p, "wf:viewing") && p.isSneaking) clearView(p);
    }
  }, 5);

  system.runInterval(tick, 5);
}
