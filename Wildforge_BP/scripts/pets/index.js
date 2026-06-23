// pets/index.js — commands, tricks, dual-path leveling, carry/ride/teleport-follow.
import { world, system } from "@minecraft/server";
import { PET_SIZE, PET_COMBAT, PET_FOOD, PET_NAME, MAXLVL } from "./data.js";
import { getOwnerId, setOwner, isOwner } from "../lib/owner.js";
import { getNum, setNum, getBool, setBool, getStr, setStr } from "../lib/persist.js";
import { actionMenu } from "../lib/menu.js";
import { playSound, spawnParticle } from "../lib/fx.js";

const XP_KEY = "wf:xp", LVL_KEY = "wf:level", BASE_KEY = "wf:basename";
const CARRY_KEY = "wf:carried", STAY_KEY = "wf:stay", MODE_KEY = "wf:mode", CARE_CD = "wf:care_cd";
const TP_DIST = 26, CARE_COOLDOWN = 60, DIMS = ["overworld", "nether", "the_end"];

const xpForLevel = (lvl) => lvl * 120;          // xp needed to reach lvl+1
const isPet = (e) => !!PET_SIZE[e?.typeId];

function levelFromXp(xp) {
  let lvl = 1;
  while (lvl < MAXLVL && xp >= xpForLevel(lvl)) { xp -= xpForLevel(lvl); lvl++; }
  return lvl;
}

function refreshName(pet) {
  let base = getStr(pet, BASE_KEY);
  if (!base) { base = PET_NAME[pet.typeId] || "Pet"; setStr(pet, BASE_KEY, base); }
  const lvl = getNum(pet, LVL_KEY, 1);
  try { pet.nameTag = `${base} §7Lv.${lvl}`; } catch (_) {}
}

function addXp(pet, amount) {
  const xp = getNum(pet, XP_KEY, 0) + amount;
  setNum(pet, XP_KEY, xp);
  const lvl = levelFromXp(xp);
  if (lvl !== getNum(pet, LVL_KEY, 1)) {
    setNum(pet, LVL_KEY, lvl);
    try { pet.triggerEvent(`wf:setlvl_${lvl}`); } catch (_) {}
    try { pet.dimension.spawnParticle("minecraft:totem_particle", pet.location); } catch (_) {}
    playSound(pet, "random.levelup", { volume: 0.6 });
  }
  refreshName(pet);
}

function heal(pet, amount) {
  try {
    const h = pet.getComponent("minecraft:health");
    if (h) h.setCurrentValue(Math.min(h.effectiveMax, h.currentValue + amount));
  } catch (_) {}
}

// ---- interaction: feed / command menu / carry ----
function onInteract(player, pet) {
  if (!isPet(pet)) return;
  const item = (() => {
    try { return player.getComponent("minecraft:equippable")?.getEquipment("Mainhand"); }
    catch (_) { return undefined; }
  })();
  const food = PET_FOOD[pet.typeId] || [];
  const holdingFood = item && food.includes(item.typeId);

  if (holdingFood) {
    if (!getOwnerId(pet)) setOwner(pet, player.id);    // claim by feeding
    if (isOwner(pet, player)) {
      if (system.currentTick - getNum(pet, CARE_CD, -999) >= CARE_COOLDOWN) {
        setNum(pet, CARE_CD, system.currentTick);
        addXp(pet, 12);                                  // care XP
        heal(pet, 4);
        spawnParticle(pet.dimension, "minecraft:heart_particle", pet.location);
      }
    }
    return;                                              // let vanilla tame/breed proceed
  }
  if (!isOwner(pet, player)) return;
  if (player.isSneaking) { openMenu(player, pet); return; }
  if (PET_SIZE[pet.typeId] === "small") toggleCarry(pet);
  // large pets: vanilla rideable mounts on plain interact
}

async function openMenu(player, pet) {
  const small = PET_SIZE[pet.typeId] === "small";
  const combat = PET_COMBAT[pet.typeId];
  const staying = getBool(pet, STAY_KEY);
  const defending = getStr(pet, MODE_KEY, "defend") === "defend";
  const carried = getBool(pet, CARRY_KEY);
  const opts = [
    { text: staying ? "Follow me" : "Stay here" },
    { text: "Do a trick" },
  ];
  if (combat) opts.push({ text: defending ? "Mode: Defend → Passive" : "Mode: Passive → Defend" });
  if (small) opts.push({ text: carried ? "Put down" : "Pick up" });
  const sel = await actionMenu(player, getStr(pet, BASE_KEY) || PET_NAME[pet.typeId],
    `Lv.${getNum(pet, LVL_KEY, 1)}  •  XP ${getNum(pet, XP_KEY, 0)}`, opts);
  if (sel === undefined) return;
  const label = opts[sel].text;
  if (label.startsWith("Follow")) { setBool(pet, STAY_KEY, false); safeTrigger(pet, "wf:follow"); }
  else if (label.startsWith("Stay")) { setBool(pet, STAY_KEY, true); safeTrigger(pet, "wf:stay"); }
  else if (label === "Do a trick") doTrick(pet);
  else if (label.startsWith("Mode")) {
    const nowDefend = !defending;
    setStr(pet, MODE_KEY, nowDefend ? "defend" : "passive");
    safeTrigger(pet, nowDefend ? "wf:mode_defend" : "wf:mode_passive");
  } else if (label === "Pick up" || label === "Put down") toggleCarry(pet);
}

function safeTrigger(pet, ev) { try { pet.triggerEvent(ev); } catch (_) {} }

function doTrick(pet) {
  try { pet.applyKnockback({ x: 0, z: 0 }, 0, 0.5); } catch (_) {
    try { pet.applyImpulse({ x: 0, y: 0.45, z: 0 }); } catch (_) {}
  }
  spawnParticle(pet.dimension, "minecraft:heart_particle", pet.location);
  playSound(pet, "random.orb", { volume: 0.5 });
  addXp(pet, 6);                                          // tricks count as care
}

function toggleCarry(pet) {
  const now = !getBool(pet, CARRY_KEY);
  setBool(pet, CARRY_KEY, now);
  safeTrigger(pet, now ? "wf:carry_on" : "wf:carry_off");
}

// ---- per-tick upkeep: carry positioning + teleport-follow ----
function upkeep() {
  for (const dimId of DIMS) {
    let dim;
    try { dim = world.getDimension(dimId); } catch (_) { continue; }
    let pets;
    try { pets = dim.getEntities({ families: ["wf_pet"] }); } catch (_) { continue; }
    for (const pet of pets) {
      const ownerId = getOwnerId(pet);
      if (!ownerId) continue;
      const owner = world.getAllPlayers().find((p) => p.id === ownerId);
      if (!owner) continue;
      if (getBool(pet, CARRY_KEY)) {
        const l = owner.location, d = owner.getViewDirection();
        try {
          pet.teleport({ x: l.x - d.x * 0.4, y: l.y + 1.1, z: l.z - d.z * 0.4 },
            { dimension: owner.dimension });
        } catch (_) {}
        continue;
      }
      if (getBool(pet, STAY_KEY)) continue;
      if (owner.dimension.id !== pet.dimension.id) { tpNear(pet, owner); continue; }
      const a = pet.location, b = owner.location;
      const dist = Math.hypot(a.x - b.x, a.y - b.y, a.z - b.z);
      if (dist > TP_DIST) tpNear(pet, owner);
    }
  }
}

function tpNear(pet, owner) {
  const l = owner.location;
  try { pet.teleport({ x: l.x + 1, y: l.y, z: l.z + 1 }, { dimension: owner.dimension }); }
  catch (_) {}
}

export function init() {
  try {
    world.afterEvents.playerInteractWithEntity.subscribe((ev) => {
      try { onInteract(ev.player, ev.target); } catch (_) {}
    });
  } catch (_) {}

  // combat XP: pet lands the killing blow
  world.afterEvents.entityDie.subscribe((ev) => {
    try {
      const killer = ev.damageSource?.damagingEntity;
      if (killer && isPet(killer) && PET_COMBAT[killer.typeId]) addXp(killer, 30);
    } catch (_) {}
  });

  // name tags for already-tamed pets coming into range
  world.afterEvents.entitySpawn.subscribe(({ entity }) => {
    try { if (isPet(entity) && getOwnerId(entity)) refreshName(entity); } catch (_) {}
  });

  system.runInterval(upkeep, 8);
}
