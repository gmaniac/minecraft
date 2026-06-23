// hatch.js — generalized owned-egg hatching, reused by Dragons and Pets.
// Register an egg->offspring map and a hatch timer; the system tags newly placed
// eggs with their owner and hatches them into a (tamed, owned) baby.
import { world, system } from "@minecraft/server";
import { nearestPlayer, setOwner, getOwnerId } from "./owner.js";
import { getNum, setNum } from "./persist.js";

const HATCH_KEY = "motor:hatch_left";
const STEP = 20; // ticks between checks
const DIMS = ["overworld", "nether", "the_end"];

// registry: { [eggTypeId]: { offspring, ticks, babyEvent } }
const registry = {};

export function registerEgg(eggTypeId, offspringTypeId, hatchTicks, babyEvent = "motor:set_baby") {
  registry[eggTypeId] = { offspring: offspringTypeId, ticks: hatchTicks, babyEvent };
}

let started = false;
export function startHatchSystem() {
  if (started) return;
  started = true;

  world.afterEvents.entitySpawn.subscribe(({ entity }) => {
    if (!entity || !registry[entity.typeId]) return;
    try {
      const p = nearestPlayer(entity);
      if (p) setOwner(entity, p.id);
      setNum(entity, HATCH_KEY, registry[entity.typeId].ticks);
    } catch (_) {}
  });

  system.runInterval(() => {
    for (const dimId of DIMS) {
      let dim;
      try { dim = world.getDimension(dimId); } catch (_) { continue; }
      for (const eggId of Object.keys(registry)) {
        let eggs;
        try { eggs = dim.getEntities({ type: eggId }); } catch (_) { continue; }
        for (const egg of eggs) {
          let left = getNum(egg, HATCH_KEY, registry[eggId].ticks) - STEP;
          if (left > 0) { setNum(egg, HATCH_KEY, left); continue; }
          hatch(egg, registry[eggId]);
        }
      }
    }
  }, STEP);
}

function hatch(egg, def) {
  const loc = egg.location;
  const dim = egg.dimension;
  const ownerId = getOwnerId(egg);
  try { egg.remove(); } catch (_) {}
  let baby;
  try { baby = dim.spawnEntity(def.offspring, loc); } catch (_) { return; }
  system.runTimeout(() => { try { baby.triggerEvent(def.babyEvent); } catch (_) {} }, 2);
  if (typeof ownerId === "string") {
    system.runTimeout(() => {
      try {
        const p = world.getAllPlayers().find((pl) => pl.id === ownerId);
        const tc = baby.getComponent("minecraft:tameable");
        if (p && tc) tc.tame(p);
      } catch (_) {}
    }, 8);
  }
}
