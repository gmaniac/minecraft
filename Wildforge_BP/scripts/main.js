// Wildforge — script entry point.
// Each domain (dragons, pets, vehicles, furniture, homebuilding, security) exports
// an init() that wires its behavior. Domains are registered here as they land.
import { system } from "@minecraft/server";
import { startHatchSystem } from "./lib/hatch.js";
import { init as initDragons } from "./dragons/index.js";
import { init as initPets } from "./pets/index.js";
import { init as initVehicles } from "./vehicles/index.js";

// Domain initializers are added milestone by milestone.
const DOMAINS = [
  initDragons,
  initPets,
  initVehicles,
  // initFurniture, initHomeBuilding, initSecurity
];

system.run(() => {
  for (const init of DOMAINS) {
    try { init(); } catch (e) { console.warn(`[Wildforge] domain init failed: ${e}`); }
  }
  // Egg hatching is shared; domains register their eggs in their init().
  startHatchSystem();
});
