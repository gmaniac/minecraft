// persist.js — safe dynamic-property helpers.
// All access is wrapped so a malformed/absent property never throws into game logic.

export function getNum(holder, key, fallback = 0) {
  try {
    const v = holder.getDynamicProperty(key);
    return typeof v === "number" ? v : fallback;
  } catch (_) {
    return fallback;
  }
}

export function setNum(holder, key, value) {
  try {
    holder.setDynamicProperty(key, value);
  } catch (_) {}
}

export function getStr(holder, key, fallback = undefined) {
  try {
    const v = holder.getDynamicProperty(key);
    return typeof v === "string" ? v : fallback;
  } catch (_) {
    return fallback;
  }
}

export function setStr(holder, key, value) {
  try {
    holder.setDynamicProperty(key, value);
  } catch (_) {}
}

export function getJson(holder, key, fallback) {
  const raw = getStr(holder, key);
  if (typeof raw !== "string") return fallback;
  try {
    return JSON.parse(raw);
  } catch (_) {
    return fallback;
  }
}

export function setJson(holder, key, value) {
  try {
    setStr(holder, key, JSON.stringify(value));
  } catch (_) {}
}

export function getBool(holder, key, fallback = false) {
  try {
    const v = holder.getDynamicProperty(key);
    return typeof v === "boolean" ? v : fallback;
  } catch (_) {
    return fallback;
  }
}

export function setBool(holder, key, value) {
  try {
    holder.setDynamicProperty(key, !!value);
  } catch (_) {}
}
