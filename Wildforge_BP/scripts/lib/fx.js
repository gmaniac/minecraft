// fx.js — particle / sound helpers for auras, breath beams and alarms.
import { system } from "@minecraft/server";

export function playSound(source, soundId, { volume = 1, pitch = 1 } = {}) {
  try {
    source.dimension.playSound(soundId, source.location, { volume, pitch });
  } catch (_) {}
}

export function spawnParticle(dimension, particleId, location, molangVars) {
  try {
    dimension.spawnParticle(particleId, location, molangVars);
  } catch (_) {}
}

// Sample points along a ray from `origin` in `dir` (normalized) up to `length`,
// used to draw breath/laser beams and to find what the beam hits.
export function* rayPoints(origin, dir, length, step = 0.6) {
  const n = Math.max(1, Math.floor(length / step));
  for (let i = 1; i <= n; i++) {
    yield {
      x: origin.x + dir.x * step * i,
      y: origin.y + dir.y * step * i,
      z: origin.z + dir.z * step * i,
    };
  }
}

export function normalize(v) {
  const m = Math.hypot(v.x, v.y, v.z) || 1;
  return { x: v.x / m, y: v.y / m, z: v.z / m };
}

// Run `fn` every `period` ticks; returns the runId so callers can clear it.
export function interval(fn, period) {
  return system.runInterval(fn, period);
}
