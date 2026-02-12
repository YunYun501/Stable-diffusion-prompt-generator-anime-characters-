/**
 * state.js - Central state store and localization-aware helpers.
 */

export const state = {
  /** @type {Object<string, {enabled: boolean, locked: boolean, value_id: string|null, color: string|null, weight: number}>} */
  slots: {},

  paletteEnabled: true,
  activePaletteId: null,
  paletteLocked: false,
  fullBodyMode: false,
  upperBodyMode: false,

  /** Slot definitions from API. */
  slotDefs: {},

  /** Section layout from API. */
  sections: {},

  /** lower_body item id -> covers_legs bool */
  lowerBodyCoversLegsById: {},

  /** pose item id -> uses_hands bool */
  poseUsesHandsById: {},

  /** Palette list from API */
  palettes: [],

  /** Canonical color tokens */
  individualColors: [],

  /** color token -> {en, zh} */
  individualColorsI18n: {},

  /** UI language (labels, selectors, slot bars) */
  uiLocale: "en",

  /** Prompt language (output text only) */
  promptLocale: "en",
};

/** Slots that should start disabled on first load. */
const DEFAULT_DISABLED_SLOTS = new Set([
  "special_features",
  "full_body",
  "eye_style",
  "hands",
]);

export function normalizeLocale(locale) {
  const code = (locale || "en").toLowerCase();
  return code.startsWith("zh") ? "zh" : "en";
}

function localizeFromMap(i18nMap, locale, fallback) {
  const lang = normalizeLocale(locale);
  if (i18nMap && typeof i18nMap === "object") {
    const exact = i18nMap[lang];
    if (typeof exact === "string" && exact) return exact;
    const en = i18nMap.en;
    if (typeof en === "string" && en) return en;
  }
  return fallback ?? "";
}

/** Public version of localizeFromMap for direct use in components. */
export function localizeFromI18nMap(i18nMap, locale, fallback) {
  return localizeFromMap(i18nMap, locale, fallback);
}

/** Initialize slot state for all known slots. */
export function initSlotState(slotDefs) {
  state.slotDefs = slotDefs;
  state.slots = {};
  for (const name of Object.keys(slotDefs)) {
    state.slots[name] = {
      enabled: !DEFAULT_DISABLED_SLOTS.has(name),
      locked: false,
      value_id: null,
      color: null,
      weight: 1.0,
    };
  }
}

/** Resolve option metadata by slot + value id. */
export function getSlotOptionById(slotName, valueId) {
  if (!slotName || !valueId) return null;
  const slotDef = state.slotDefs[slotName];
  const options = slotDef?.options || [];
  return options.find((opt) => opt.id === valueId) || null;
}

/** Get localized option text for a slot value id. */
export function getSlotOptionLabel(slotName, valueId, locale) {
  const option = getSlotOptionById(slotName, valueId);
  if (!option) return "";
  return localizeFromMap(option.name_i18n, locale, option.name || option.id || "");
}

/** Convert legacy saved display text to canonical item id for a slot. */
export function resolveLegacyValueToId(slotName, legacyValue) {
  if (!legacyValue) return null;
  const needle = String(legacyValue).trim().toLowerCase();
  const slotDef = state.slotDefs[slotName];
  if (!slotDef) return null;

  for (const opt of slotDef.options || []) {
    const candidates = [
      opt.id,
      opt.name,
      opt.name_i18n?.en,
      opt.name_i18n?.zh,
    ];
    for (const candidate of candidates) {
      if (typeof candidate === "string" && candidate.trim().toLowerCase() === needle) {
        return opt.id;
      }
    }
  }
  return null;
}

/** Localized label for color token. */
export function getColorLabel(colorToken, locale) {
  if (!colorToken) return "";
  const i18nMap = state.individualColorsI18n[colorToken];
  return localizeFromMap(i18nMap, locale, colorToken);
}

/** Localized label for palette id. */
export function getPaletteLabel(paletteId, locale) {
  const palette = (state.palettes || []).find((p) => p.id === paletteId);
  if (!palette) return "";
  return localizeFromMap(palette.name_i18n, locale, palette.name || palette.id || "");
}

/** Get current slot state formatted for API requests. */
export function getSlotStateForAPI() {
  const out = {};
  for (const [name, s] of Object.entries(state.slots)) {
    out[name] = {
      enabled: s.enabled,
      value_id: s.value_id,
      color: s.color,
      weight: s.weight,
    };
  }
  return out;
}

/** Get current selected value ids for randomization context. */
export function getCurrentValueIds() {
  const out = {};
  for (const [name, s] of Object.entries(state.slots)) {
    if (s.enabled && s.value_id) out[name] = s.value_id;
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
