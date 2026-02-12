/**
 * handlers.js - Event handler wiring for UI interactions.
 */

import {
  state,
  getSlotStateForAPI,
  getLockedMap,
  getCurrentValueIds,
  resolveLegacyValueToId,
  getPaletteLabel,
} from "./state.js";
import * as api from "./api.js";
import { clearPromptOutput, generateAndDisplay, getPromptOutputText, setPromptOutput } from "./prompt.js";
import { t } from "./i18n.js";

const LOCKED_ICON = "\uD83D\uDD12";
const UNLOCKED_ICON = "\uD83D\uDD13";

/** Reference to all slot DOM components, keyed by slot name. */
let allSlotComponents = {};

/** Slots toggled OFF once when full-body specific outfit is enabled. */
const FULL_BODY_MODE_ONE_SHOT_DISABLE_SLOTS = ["upper_body", "waist", "lower_body", "hands", "legs"];
const fullBodyModeAutoDisabledSlots = new Set();

/** Slots toggled OFF once when upper-body mode is enabled. */
const UPPER_BODY_MODE_ONE_SHOT_DISABLE_SLOTS = ["waist", "lower_body", "full_body", "legs", "feet"];
const upperBodyModeAutoDisabledSlots = new Set();

/** Cache for deterministic swatch color conversion. */
const paletteColorCache = new Map();

/** Store component refs so handlers can update the DOM. */
export function setSlotComponents(comps) {
  allSlotComponents = comps;
}

export function wireSlotEvents(slotName, comps) {
  const { onoffBtn, lockBtn, randomBtn, colorRandomBtn, dropdown, colorSelect, weightInput } = comps;

  onoffBtn.addEventListener("click", () => {
    const s = state.slots[slotName];
    s.enabled = !s.enabled;
    renderSlotEnabledState(slotName, comps);

    if (slotName === "lower_body") {
      maybeDisableLegsForLowerBodyCoverage();
    } else if (slotName === "pose") {
      maybeDisableHandActionsForPoseUsage();
    }
    generateAndDisplay();
  });

  lockBtn.addEventListener("click", () => {
    const s = state.slots[slotName];
    s.locked = !s.locked;
    lockBtn.textContent = s.locked ? LOCKED_ICON : UNLOCKED_ICON;
    lockBtn.className = "btn-lock" + (s.locked ? " locked" : "");
    comps.row.classList.toggle("locked", s.locked);
  });

  randomBtn.addEventListener("click", async () => {
    const data = await api.randomizeSlots(
      [slotName],
      getLockedMap(),
      state.paletteEnabled,
      state.activePaletteId,
      state.fullBodyMode,
      state.upperBodyMode,
      getCurrentValueIds(),
    );
    applyResults(data.results);
    generateAndDisplay();
  });

  colorRandomBtn.addEventListener("click", async () => {
    const def = state.slotDefs[slotName];
    if (!def || !def.has_color) return;
    if (!state.paletteEnabled || !state.activePaletteId) return;

    const data = await api.randomizeSlots(
      [slotName],
      {},
      state.paletteEnabled,
      state.activePaletteId,
      state.fullBodyMode,
      state.upperBodyMode,
      {},
    );

    if (data.results[slotName]) {
      const color = data.results[slotName].color;
      state.slots[slotName].color = color;
      colorSelect.value = color || "";
      generateAndDisplay();
    }
  });

  dropdown.addEventListener("change", () => {
    state.slots[slotName].value_id = dropdown.value || null;
    if (slotName === "lower_body") {
      maybeDisableLegsForLowerBodyCoverage();
    } else if (slotName === "pose") {
      maybeDisableHandActionsForPoseUsage();
    }
    generateAndDisplay();
  });

  colorSelect.addEventListener("change", () => {
    state.slots[slotName].color = colorSelect.value || null;
    generateAndDisplay();
  });

  weightInput.addEventListener("change", () => {
    state.slots[slotName].weight = parseFloat(weightInput.value) || 1.0;
    generateAndDisplay();
  });
}

export function wireSectionEvents(sectionData) {
  const { randomBtn, allOnBtn, allOffBtn, slotNames } = sectionData;

  randomBtn.addEventListener("click", async () => {
    const data = await api.randomizeSlots(
      slotNames,
      getLockedMap(),
      state.paletteEnabled,
      state.activePaletteId,
      state.fullBodyMode,
      state.upperBodyMode,
      getCurrentValueIds(),
    );
    applyResults(data.results);
    generateAndDisplay();
  });

  allOnBtn.addEventListener("click", () => {
    for (const name of slotNames) {
      state.slots[name].enabled = true;
      const c = allSlotComponents[name];
      if (c) renderSlotEnabledState(name, c);
    }
    applySlotConstraints();
    generateAndDisplay();
  });

  allOffBtn.addEventListener("click", () => {
    for (const name of slotNames) {
      state.slots[name].enabled = false;
      const c = allSlotComponents[name];
      if (c) renderSlotEnabledState(name, c);
    }
    applySlotConstraints();
    generateAndDisplay();
  });
}

export function wireGlobalEvents() {
  document.getElementById("full-body-mode").checked = state.fullBodyMode;
  document.getElementById("upper-body-mode").checked = state.upperBodyMode;
  document.getElementById("palette-enabled").checked = state.paletteEnabled;
  initPalettePicker();
  applySlotConstraints();

  document.getElementById("btn-randomize-all").addEventListener("click", async () => {
    maybeRandomizePaletteForRandomizeAll();
    const data = await api.randomizeAll(
      getLockedMap(),
      state.paletteEnabled,
      state.activePaletteId,
      state.fullBodyMode,
      state.upperBodyMode,
    );
    applyResults(data.results);
    generateAndDisplay();
  });

  document.getElementById("btn-generate").addEventListener("click", () => {
    generateAndDisplay();
  });

  document.getElementById("btn-reset").addEventListener("click", () => {
    for (const [name, s] of Object.entries(state.slots)) {
      s.value_id = null;
      s.color = null;
      s.weight = 1.0;

      const c = allSlotComponents[name];
      if (!c) continue;
      c.dropdown.value = "";
      c.colorSelect.value = "";
      c.weightInput.value = "1.0";
    }
    applySlotConstraints();
    clearPromptOutput();
  });

  document.getElementById("btn-copy").addEventListener("click", () => {
    const text = getPromptOutputText();
    navigator.clipboard.writeText(text);
  });

  document.getElementById("full-body-mode").addEventListener("change", (e) => {
    const wasEnabled = state.fullBodyMode;
    state.fullBodyMode = e.target.checked;
    if (!wasEnabled && state.fullBodyMode) {
      applyFullBodyModeOneShotDisable();
    } else if (wasEnabled && !state.fullBodyMode) {
      restoreFullBodyModeOneShotDisabledSlots();
    }
    applySlotConstraints();
    generateAndDisplay();
  });

  document.getElementById("upper-body-mode").addEventListener("change", (e) => {
    const wasEnabled = state.upperBodyMode;
    state.upperBodyMode = e.target.checked;
    if (!wasEnabled && state.upperBodyMode) {
      applyUpperBodyModeOneShotDisable();
    } else if (wasEnabled && !state.upperBodyMode) {
      restoreUpperBodyModeOneShotDisabledSlots();
    }
    applySlotConstraints();
    generateAndDisplay();
  });

  document.getElementById("palette-enabled").addEventListener("change", async (e) => {
    state.paletteEnabled = e.target.checked;
    if (state.paletteEnabled && state.activePaletteId) {
      await applyActivePaletteToCurrentSlots(state.activePaletteId);
      return;
    }
    generateAndDisplay();
  });
}

export function wireSaveLoadEvents() {
  document.getElementById("btn-save").addEventListener("click", async () => {
    const name = document.getElementById("config-name").value.trim();
    if (!name) {
      setStatus(t("status_enter_name"));
      return;
    }

    const data = { slots: {} };
    for (const [slotName, s] of Object.entries(state.slots)) {
      data.slots[slotName] = {
        enabled: s.enabled,
        locked: s.locked,
        value_id: s.value_id,
        color: s.color,
        weight: s.weight,
      };
    }
    await api.saveConfig(name, data);
    setStatus(t("status_saved", { name }));
    await refreshConfigList();
  });

  document.getElementById("btn-load").addEventListener("click", async () => {
    const name = document.getElementById("config-select").value;
    if (!name) {
      setStatus(t("status_select_config"));
      return;
    }

    const res = await api.loadConfig(name);
    const slots = res.data?.slots || {};
    for (const [slotName, saved] of Object.entries(slots)) {
      if (!state.slots[slotName]) continue;

      const nextValueId = saved.value_id || resolveLegacyValueToId(slotName, saved.value);

      state.slots[slotName].enabled = saved.enabled ?? state.slots[slotName].enabled;
      state.slots[slotName].locked = !!saved.locked;
      state.slots[slotName].value_id = nextValueId || null;
      state.slots[slotName].color = saved.color || null;
      state.slots[slotName].weight = saved.weight ?? 1.0;

      const c = allSlotComponents[slotName];
      if (!c) continue;
      c.dropdown.value = state.slots[slotName].value_id || "";
      c.colorSelect.value = state.slots[slotName].color || "";
      c.weightInput.value = String(state.slots[slotName].weight ?? 1.0);
      c.lockBtn.textContent = state.slots[slotName].locked ? LOCKED_ICON : UNLOCKED_ICON;
      c.lockBtn.className = "btn-lock" + (state.slots[slotName].locked ? " locked" : "");
      renderSlotEnabledState(slotName, c);
    }

    setStatus(t("status_loaded", { name }));
    maybeDisableLegsForLowerBodyCoverage();
    maybeDisableHandActionsForPoseUsage();
    applySlotConstraints();
    generateAndDisplay();
  });

  document.getElementById("btn-refresh-configs").addEventListener("click", refreshConfigList);
}

async function refreshConfigList() {
  const data = await api.fetchConfigs();
  const select = document.getElementById("config-select");
  select.innerHTML = "";

  const defaultOpt = document.createElement("option");
  defaultOpt.value = "";
  defaultOpt.textContent = t("config_select_default");
  select.appendChild(defaultOpt);

  for (const name of data.configs || []) {
    const opt = document.createElement("option");
    opt.value = name;
    opt.textContent = name;
    select.appendChild(opt);
  }
}

/** Called on init to populate the config dropdown. */
export { refreshConfigList };

export function refreshLocalizedDynamicUi() {
  renderNativePaletteOptions();
  renderPaletteMenu();
  setPaletteSelection(state.activePaletteId);
  renderPaletteLockButton();

  const saveStatus = document.getElementById("save-status");
  if (saveStatus) saveStatus.textContent = "";
}

function setStatus(msg) {
  document.getElementById("save-status").textContent = msg;
}

function applyResults(results) {
  for (const [name, res] of Object.entries(results)) {
    const resolvedId = res.value_id || resolveLegacyValueToId(name, res.value);
    state.slots[name].value_id = resolvedId || null;
    state.slots[name].color = res.color;

    const c = allSlotComponents[name];
    if (!c) continue;
    c.dropdown.value = state.slots[name].value_id || "";
    c.colorSelect.value = res.color || "";
  }
  if (Object.prototype.hasOwnProperty.call(results, "lower_body")) {
    maybeDisableLegsForLowerBodyCoverage();
  }
  if (Object.prototype.hasOwnProperty.call(results, "pose")) {
    maybeDisableHandActionsForPoseUsage();
  }
  applySlotConstraints();
}

function renderSlotEnabledState(slotName, comps) {
  const s = state.slots[slotName];
  comps.onoffBtn.textContent = s.enabled ? t("slot_on") : t("slot_off");
  comps.onoffBtn.className = "btn-onoff " + (s.enabled ? "on" : "off");
  comps.row.className = "slot-row " + (s.enabled ? "enabled" : "disabled") + (s.locked ? " locked" : "");
}

function isLowerBodyCoveringLegs() {
  const lower = state.slots.lower_body;
  if (!lower || !lower.enabled || !lower.value_id) return false;
  return !!state.lowerBodyCoversLegsById[lower.value_id];
}

function maybeDisableLegsForLowerBodyCoverage() {
  if (!isLowerBodyCoveringLegs()) return;

  const legsState = state.slots.legs;
  const legsComps = allSlotComponents.legs;
  if (!legsState || !legsComps) return;
  if (!legsState.enabled) return;

  legsState.enabled = false;
  renderSlotEnabledState("legs", legsComps);
}

function isPoseUsingHands() {
  const pose = state.slots.pose;
  if (!pose || !pose.enabled || !pose.value_id) return false;
  return !!state.poseUsesHandsById[pose.value_id];
}

function maybeDisableHandActionsForPoseUsage() {
  if (!isPoseUsingHands()) return;

  const handActionsState = state.slots.gesture;
  const handActionsComps = allSlotComponents.gesture;
  if (!handActionsState || !handActionsComps) return;
  if (!handActionsState.enabled) return;

  handActionsState.enabled = false;
  renderSlotEnabledState("gesture", handActionsComps);
}

function applyFullBodyModeOneShotDisable() {
  fullBodyModeAutoDisabledSlots.clear();
  for (const slotName of FULL_BODY_MODE_ONE_SHOT_DISABLE_SLOTS) {
    const slotState = state.slots[slotName];
    const c = allSlotComponents[slotName];
    if (!slotState || !c) continue;
    if (slotState.enabled) {
      fullBodyModeAutoDisabledSlots.add(slotName);
    }
    slotState.enabled = false;
    renderSlotEnabledState(slotName, c);
  }

  const fbState = state.slots.full_body;
  const fbComps = allSlotComponents.full_body;
  if (fbState && fbComps && !fbState.enabled) {
    fbState.enabled = true;
    renderSlotEnabledState("full_body", fbComps);
  }
}

function restoreFullBodyModeOneShotDisabledSlots() {
  for (const slotName of fullBodyModeAutoDisabledSlots) {
    const slotState = state.slots[slotName];
    const c = allSlotComponents[slotName];
    if (!slotState || !c) continue;
    slotState.enabled = true;
    renderSlotEnabledState(slotName, c);
  }
  fullBodyModeAutoDisabledSlots.clear();

  const fbState = state.slots.full_body;
  const fbComps = allSlotComponents.full_body;
  if (fbState && fbComps && fbState.enabled) {
    fbState.enabled = false;
    renderSlotEnabledState("full_body", fbComps);
  }
}

function applyUpperBodyModeOneShotDisable() {
  upperBodyModeAutoDisabledSlots.clear();
  for (const slotName of UPPER_BODY_MODE_ONE_SHOT_DISABLE_SLOTS) {
    const slotState = state.slots[slotName];
    const c = allSlotComponents[slotName];
    if (!slotState || !c) continue;
    if (slotState.enabled) {
      upperBodyModeAutoDisabledSlots.add(slotName);
    }
    slotState.enabled = false;
    renderSlotEnabledState(slotName, c);
  }
}

function restoreUpperBodyModeOneShotDisabledSlots() {
  for (const slotName of upperBodyModeAutoDisabledSlots) {
    const slotState = state.slots[slotName];
    const c = allSlotComponents[slotName];
    if (!slotState || !c) continue;
    slotState.enabled = true;
    renderSlotEnabledState(slotName, c);
  }
  upperBodyModeAutoDisabledSlots.clear();
}

function applySlotConstraints() {
  // No persistent force-disable constraints currently.
}

function initPalettePicker() {
  const pickerBtn = document.getElementById("palette-picker-btn");
  const pickerMenu = document.getElementById("palette-picker-menu");
  const pickerWrap = document.getElementById("palette-picker");
  const randomBtn = document.getElementById("btn-palette-random");
  const lockBtn = document.getElementById("btn-palette-lock");
  const nativeSelect = document.getElementById("palette-select");
  if (!pickerBtn || !pickerMenu || !pickerWrap || !lockBtn || !nativeSelect) return;

  renderNativePaletteOptions();
  renderPaletteMenu();
  setPaletteSelection(state.activePaletteId);
  renderPaletteLockButton();

  pickerBtn.addEventListener("click", (e) => {
    e.stopPropagation();
    togglePaletteMenu(!pickerMenu.classList.contains("open"));
  });

  if (randomBtn) {
    randomBtn.addEventListener("click", async () => {
      await randomizeActivePalette(true);
    });
  }

  lockBtn.addEventListener("click", () => {
    state.paletteLocked = !state.paletteLocked;
    renderPaletteLockButton();
  });

  nativeSelect.addEventListener("change", async (e) => {
    await onPaletteSelected(e.target.value || null, true);
  });

  document.addEventListener("click", (e) => {
    if (!pickerWrap.contains(e.target)) {
      togglePaletteMenu(false);
    }
  });

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      togglePaletteMenu(false);
    }
  });
}

function togglePaletteMenu(open) {
  const pickerBtn = document.getElementById("palette-picker-btn");
  const pickerMenu = document.getElementById("palette-picker-menu");
  if (!pickerBtn || !pickerMenu) return;
  pickerMenu.classList.toggle("open", !!open);
  pickerBtn.setAttribute("aria-expanded", open ? "true" : "false");
}

function renderNativePaletteOptions() {
  const nativeSelect = document.getElementById("palette-select");
  if (!nativeSelect) return;

  nativeSelect.innerHTML = "";
  const none = document.createElement("option");
  none.value = "";
  none.textContent = t("palette_none");
  nativeSelect.appendChild(none);

  for (const p of state.palettes || []) {
    const opt = document.createElement("option");
    opt.value = p.id;
    opt.textContent = getPaletteLabel(p.id, state.uiLocale);
    nativeSelect.appendChild(opt);
  }
}

function renderPaletteMenu() {
  const pickerMenu = document.getElementById("palette-picker-menu");
  if (!pickerMenu) return;

  pickerMenu.innerHTML = "";
  pickerMenu.appendChild(createPaletteOptionButton("", t("palette_none"), []));
  for (const p of state.palettes || []) {
    pickerMenu.appendChild(createPaletteOptionButton(p.id, getPaletteLabel(p.id, state.uiLocale), p.colors || []));
  }
}

function createPaletteOptionButton(paletteId, label, colors) {
  const btn = document.createElement("button");
  btn.type = "button";
  btn.className = "palette-option";
  btn.dataset.paletteId = paletteId;

  const labelSpan = document.createElement("span");
  labelSpan.textContent = label;

  const swatches = document.createElement("span");
  swatches.className = "palette-swatches";
  renderPaletteSwatches(swatches, colors, 4);

  btn.append(labelSpan, swatches);
  btn.addEventListener("click", async () => {
    await onPaletteSelected(paletteId || null, true);
    togglePaletteMenu(false);
  });

  return btn;
}

async function onPaletteSelected(paletteId, applyPaletteColors) {
  setPaletteSelection(paletteId);
  if (!paletteId || !applyPaletteColors || !state.paletteEnabled) return;
  await applyActivePaletteToCurrentSlots(paletteId);
}

async function applyActivePaletteToCurrentSlots(paletteId) {
  if (!paletteId) return;

  const slotsForAPI = getSlotStateForAPI();
  // Capture locale for consistency
  const promptLocale = state.promptLocale;
  const data = await api.applyPalette(
    paletteId,
    slotsForAPI,
    state.fullBodyMode,
    state.upperBodyMode,
    promptLocale,
  );

  for (const [name, color] of Object.entries(data.colors || {})) {
    state.slots[name].color = color;
    const c = allSlotComponents[name];
    if (c) c.colorSelect.value = color || "";
  }

  if (data.prompt) {
    setPromptOutput(data.prompt, promptLocale);
  } else {
    generateAndDisplay();
  }
}

function setPaletteSelection(paletteId) {
  state.activePaletteId = paletteId || null;

  const nativeSelect = document.getElementById("palette-select");
  if (nativeSelect) {
    nativeSelect.value = state.activePaletteId || "";
  }

  const nameEl = document.getElementById("palette-picker-name");
  const swatchesEl = document.getElementById("palette-picker-swatches");
  if (nameEl) {
    nameEl.textContent = state.activePaletteId
      ? getPaletteLabel(state.activePaletteId, state.uiLocale)
      : t("palette_none");
  }

  const palette = getPaletteById(state.activePaletteId);
  if (swatchesEl) renderPaletteSwatches(swatchesEl, palette?.colors || [], 5);

  const pickerMenu = document.getElementById("palette-picker-menu");
  if (pickerMenu) {
    for (const btn of pickerMenu.querySelectorAll(".palette-option")) {
      btn.classList.toggle("active", btn.dataset.paletteId === (state.activePaletteId || ""));
    }
  }
}

function renderPaletteLockButton() {
  const btn = document.getElementById("btn-palette-lock");
  if (!btn) return;
  btn.textContent = state.paletteLocked ? LOCKED_ICON : UNLOCKED_ICON;
  btn.className = "btn-lock" + (state.paletteLocked ? " locked" : "");
  btn.title = state.paletteLocked ? t("palette_locked_title") : t("palette_lock_title");
}

function maybeRandomizePaletteForRandomizeAll() {
  if (!state.paletteEnabled || state.paletteLocked) return;
  const paletteId = pickRandomPaletteId(state.activePaletteId);
  if (!paletteId) return;
  setPaletteSelection(paletteId);
}

async function randomizeActivePalette(applyPaletteColors) {
  const paletteId = pickRandomPaletteId(state.activePaletteId);
  if (!paletteId) return;
  await onPaletteSelected(paletteId, applyPaletteColors);
}

function pickRandomPaletteId(currentId) {
  const palettes = state.palettes || [];
  if (!palettes.length) return null;
  if (palettes.length === 1) return palettes[0].id;

  let pool = palettes;
  if (currentId) {
    const filtered = palettes.filter((p) => p.id !== currentId);
    if (filtered.length) pool = filtered;
  }
  const idx = Math.floor(Math.random() * pool.length);
  return pool[idx].id;
}

function getPaletteById(paletteId) {
  if (!paletteId) return null;
  return (state.palettes || []).find((p) => p.id === paletteId) || null;
}

function renderPaletteSwatches(container, colors, maxCount) {
  container.innerHTML = "";
  const useColors = (colors || []).slice(0, maxCount);
  for (const colorName of useColors) {
    const sw = document.createElement("span");
    sw.className = "palette-swatch";
    sw.title = colorName;
    sw.style.backgroundColor = colorTokenToCss(colorName);
    container.appendChild(sw);
  }
}

function colorTokenToCss(token) {
  const key = (token || "").trim().toLowerCase();
  if (!key) return "#666";
  const cached = paletteColorCache.get(key);
  if (cached) return cached;

  if (typeof CSS !== "undefined" && CSS.supports("color", key)) {
    paletteColorCache.set(key, key);
    return key;
  }

  const compact = key.replace(/[\s_-]+/g, "");
  if (typeof CSS !== "undefined" && CSS.supports("color", compact)) {
    paletteColorCache.set(key, compact);
    return compact;
  }

  let hash = 0;
  for (let i = 0; i < key.length; i += 1) {
    hash = (hash * 31 + key.charCodeAt(i)) % 360;
  }
  const fallback = `hsl(${Math.abs(hash)} 55% 55%)`;
  paletteColorCache.set(key, fallback);
  return fallback;
}
