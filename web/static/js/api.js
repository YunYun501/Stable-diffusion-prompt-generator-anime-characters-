/**
 * api.js — All fetch() calls to the FastAPI backend.
 */

const BASE = "";

async function post(url, body) {
  const res = await fetch(BASE + url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  return res.json();
}

async function get(url) {
  const res = await fetch(BASE + url);
  return res.json();
}

/** Fetch slot definitions + section layout. */
export function fetchSlots() {
  return get("/api/slots");
}

/** Fetch palette list + individual colors. */
export function fetchPalettes() {
  return get("/api/palettes");
}

/** Randomize specific slots. */
export function randomizeSlots(slotNames, locked, paletteEnabled, paletteId, fullBodyMode, upperBodyMode, currentValues) {
  return post("/api/randomize", {
    slot_names: slotNames,
    locked,
    palette_enabled: paletteEnabled,
    palette_id: paletteId,
    full_body_mode: fullBodyMode,
    upper_body_mode: upperBodyMode,
    current_values: currentValues,
  });
}

/** Randomize all slots. */
export function randomizeAll(locked, paletteEnabled, paletteId, fullBodyMode, upperBodyMode) {
  return post("/api/randomize-all", {
    locked,
    palette_enabled: paletteEnabled,
    palette_id: paletteId,
    full_body_mode: fullBodyMode,
    upper_body_mode: upperBodyMode,
  });
}

/** Generate prompt string from slot state. */
export function generatePrompt(slots, fullBodyMode, upperBodyMode, outputLanguage) {
  return post("/api/generate-prompt", {
    slots,
    full_body_mode: fullBodyMode,
    upper_body_mode: upperBodyMode,
    output_language: outputLanguage,
  });
}

/** Apply palette colors and get new prompt. */
export function applyPalette(paletteId, slots, fullBodyMode, upperBodyMode, outputLanguage) {
  return post("/api/apply-palette", {
    palette_id: paletteId,
    slots,
    full_body_mode: fullBodyMode,
    upper_body_mode: upperBodyMode,
    output_language: outputLanguage,
  });
}

/** List saved configs. */
export function fetchConfigs() {
  return get("/api/configs");
}

/** Load a config by name. */
export function loadConfig(name) {
  return get(`/api/configs/${encodeURIComponent(name)}`);
}

/** Save a config. */
export function saveConfig(name, data) {
  return post(`/api/configs/${encodeURIComponent(name)}`, { name, data });
}
