// MotorCraft — script entry point.
// Each domain (dragons, pets, vehicles, furniture, homebuilding, security) exports
// an init() that wires its behavior. Domains are registered here as they land.
import { system } from "@minecraft/server";
import { startHatchSystem } from "./lib/hatch.js";

// Domain initializers are added milestone by milestone, e.g.:
//   import { init as initDragons } from "./dragons/index.js";
const DOMAINS = [
  // initDragons, initPets, initVehicles, initFurniture, initHomeBuilding, initSecurity
];

system.run(() => {
  for (const init of DOMAINS) {
    try { init(); } catch (e) { console.warn(`[MotorCraft] domain init failed: ${e}`); }
  }
  // Egg hatching is shared; domains register their eggs in their init().
  startHatchSystem();
});
