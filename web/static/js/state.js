/**
 * state.js — Central state store for all slot values and settings.
 *
 * The frontend owns all UI state. The backend is stateless.
 */

export const state = {
  /** @type {Object<string, {enabled: boolean, locked: boolean, value: string|null, color: string|null, weight: number}>} */
  slots: {},

  /** @type {"none"|"palette"|"random"} */
  colorMode: "none",

  /** @type {string|null} */
  activePaletteId: null,

  /** @type {boolean} */
  fullBodyMode: true,

  /** Slot definitions from API (options, has_color, category) */
  slotDefs: {},

  /** Section layout from API */
  sections: {},

  /** Palette list from API */
  palettes: [],

  /** Individual colors from API */
  individualColors: [],
};

/** Initialize slot state for all known slots. */
export function initSlotState(slotDefs) {
  state.slotDefs = slotDefs;
  for (const name of Object.keys(slotDefs)) {
    state.slots[name] = {
      enabled: true,
      locked: false,
      value: null,
      color: null,
      weight: 1.0,
    };
  }
}

/** Get current slot state formatted for API requests. */
export function getSlotStateForAPI() {
  const out = {};
  for (const [name, s] of Object.entries(state.slots)) {
    out[name] = {
      enabled: s.enabled,
      value: s.value,
      color: s.color,
      weight: s.weight,
    };
  }
  return out;
}

/** Get locked map for API requests. */
export function getLockedMap() {
  const out = {};
  for (const [name, s] of Object.entries(state.slots)) {
    if (s.locked) out[name] = true;
  }
  return out;
}
