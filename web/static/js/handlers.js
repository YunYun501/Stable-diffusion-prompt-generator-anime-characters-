/**
 * handlers.js — Event handler wiring for all UI interactions.
 */

import { state, getSlotStateForAPI, getLockedMap } from "./state.js";
import * as api from "./api.js";
import { generateAndDisplay } from "./prompt.js";

/** Reference to all slot DOM components, keyed by slot name. */
let allSlotComponents = {};

/** Store component refs so handlers can update the DOM. */
export function setSlotComponents(comps) {
  allSlotComponents = comps;
}

// ─── Slot-level handlers ───

export function wireSlotEvents(slotName, comps) {
  const { onoffBtn, lockBtn, randomBtn, colorRandomBtn, dropdown, colorSelect, weightInput } = comps;

  // On/Off toggle
  onoffBtn.addEventListener("click", () => {
    const s = state.slots[slotName];
    s.enabled = !s.enabled;
    onoffBtn.textContent = s.enabled ? "On" : "Off";
    onoffBtn.className = "btn-onoff " + (s.enabled ? "on" : "off");
    comps.row.className = "slot-row " + (s.enabled ? "enabled" : "disabled") + (s.locked ? " locked" : "");
  });

  // Lock toggle
  lockBtn.addEventListener("click", () => {
    const s = state.slots[slotName];
    s.locked = !s.locked;
    lockBtn.textContent = s.locked ? "\uD83D\uDD12" : "\uD83D\uDD13";
    lockBtn.className = "btn-lock" + (s.locked ? " locked" : "");
    comps.row.classList.toggle("locked", s.locked);
  });

  // Per-slot randomize
  randomBtn.addEventListener("click", async () => {
    const currentValues = {};
    for (const [n, sl] of Object.entries(state.slots)) {
      if (sl.value) currentValues[n] = sl.value;
    }
    const data = await api.randomizeSlots(
      [slotName], getLockedMap(), state.colorMode, state.activePaletteId,
      state.fullBodyMode, currentValues
    );
    applyResults(data.results);
  });

  // Per-slot color randomize
  colorRandomBtn.addEventListener("click", async () => {
    const def = state.slotDefs[slotName];
    if (!def || !def.has_color) return;

    // Randomize just this slot's color via the randomize endpoint
    const data = await api.randomizeSlots(
      [slotName], {}, state.colorMode, state.activePaletteId,
      state.fullBodyMode, {}
    );
    // Only apply the color, keep current value
    if (data.results[slotName]) {
      const color = data.results[slotName].color;
      state.slots[slotName].color = color;
      colorSelect.value = color || "";
    }
  });

  // Dropdown change
  dropdown.addEventListener("change", () => {
    state.slots[slotName].value = dropdown.value || null;
  });

  // Color change
  colorSelect.addEventListener("change", () => {
    state.slots[slotName].color = colorSelect.value || null;
  });

  // Weight change
  weightInput.addEventListener("change", () => {
    state.slots[slotName].weight = parseFloat(weightInput.value) || 1.0;
  });
}

// ─── Section-level handlers ───

export function wireSectionEvents(sectionData) {
  const { randomBtn, allOnBtn, allOffBtn, slotNames } = sectionData;

  // Section randomize
  randomBtn.addEventListener("click", async () => {
    const currentValues = {};
    for (const [n, sl] of Object.entries(state.slots)) {
      if (sl.value) currentValues[n] = sl.value;
    }
    const data = await api.randomizeSlots(
      slotNames, getLockedMap(), state.colorMode, state.activePaletteId,
      state.fullBodyMode, currentValues
    );
    applyResults(data.results);
    generateAndDisplay();
  });

  // All On
  allOnBtn.addEventListener("click", () => {
    for (const name of slotNames) {
      state.slots[name].enabled = true;
      const c = allSlotComponents[name];
      if (c) {
        c.onoffBtn.textContent = "On";
        c.onoffBtn.className = "btn-onoff on";
        c.row.className = "slot-row enabled" + (state.slots[name].locked ? " locked" : "");
      }
    }
  });

  // All Off
  allOffBtn.addEventListener("click", () => {
    for (const name of slotNames) {
      state.slots[name].enabled = false;
      const c = allSlotComponents[name];
      if (c) {
        c.onoffBtn.textContent = "Off";
        c.onoffBtn.className = "btn-onoff off";
        c.row.className = "slot-row disabled" + (state.slots[name].locked ? " locked" : "");
      }
    }
  });
}

// ─── Global handlers ───

export function wireGlobalEvents() {
  // Randomize All
  document.getElementById("btn-randomize-all").addEventListener("click", async () => {
    const data = await api.randomizeAll(
      getLockedMap(), state.colorMode, state.activePaletteId, state.fullBodyMode
    );
    applyResults(data.results);
    generateAndDisplay();
  });

  // Generate Prompt
  document.getElementById("btn-generate").addEventListener("click", () => {
    generateAndDisplay();
  });

  // Reset
  document.getElementById("btn-reset").addEventListener("click", () => {
    for (const [name, s] of Object.entries(state.slots)) {
      s.value = null;
      s.color = null;
      s.weight = 1.0;
      const c = allSlotComponents[name];
      if (c) {
        c.dropdown.value = "";
        c.colorSelect.value = "";
        c.weightInput.value = "1.0";
      }
    }
    document.getElementById("prompt-output").value = "";
  });

  // Copy
  document.getElementById("btn-copy").addEventListener("click", () => {
    const text = document.getElementById("prompt-output").value;
    navigator.clipboard.writeText(text);
  });

  // Full-body mode
  document.getElementById("full-body-mode").addEventListener("change", (e) => {
    state.fullBodyMode = e.target.checked;
  });

  // Color mode radios
  document.querySelectorAll('input[name="color-mode"]').forEach((radio) => {
    radio.addEventListener("change", (e) => {
      state.colorMode = e.target.value;
    });
  });

  // Palette select — auto-apply colors + regenerate prompt
  document.getElementById("palette-select").addEventListener("change", async (e) => {
    const paletteId = e.target.value;
    state.activePaletteId = paletteId || null;
    if (!paletteId) return;

    // Switch color mode to palette
    state.colorMode = "palette";
    document.querySelector('input[name="color-mode"][value="palette"]').checked = true;

    // Apply palette colors to all has_color slots with a value
    const slotsForAPI = getSlotStateForAPI();
    const data = await api.applyPalette(paletteId, slotsForAPI, state.fullBodyMode);

    // Update colors in state + DOM
    for (const [name, color] of Object.entries(data.colors || {})) {
      state.slots[name].color = color;
      const c = allSlotComponents[name];
      if (c) c.colorSelect.value = color || "";
    }

    // Update prompt
    if (data.prompt) {
      document.getElementById("prompt-output").value = data.prompt;
    }
  });
}

// ─── Save / Load handlers ───

export function wireSaveLoadEvents() {
  document.getElementById("btn-save").addEventListener("click", async () => {
    const name = document.getElementById("config-name").value.trim();
    if (!name) {
      setStatus("Please enter a config name");
      return;
    }
    const data = { slots: {} };
    for (const [slotName, s] of Object.entries(state.slots)) {
      data.slots[slotName] = {
        enabled: s.enabled, locked: s.locked,
        value: s.value, color: s.color, weight: s.weight,
      };
    }
    await api.saveConfig(name, data);
    setStatus(`Saved: ${name}`);
    refreshConfigList();
  });

  document.getElementById("btn-load").addEventListener("click", async () => {
    const name = document.getElementById("config-select").value;
    if (!name) {
      setStatus("Select a config first");
      return;
    }
    const res = await api.loadConfig(name);
    const slots = res.data?.slots || {};
    for (const [slotName, saved] of Object.entries(slots)) {
      if (!state.slots[slotName]) continue;
      Object.assign(state.slots[slotName], saved);
      const c = allSlotComponents[slotName];
      if (c) {
        c.dropdown.value = saved.value || "";
        c.colorSelect.value = saved.color || "";
        c.weightInput.value = saved.weight ?? 1.0;
        c.onoffBtn.textContent = saved.enabled ? "On" : "Off";
        c.onoffBtn.className = "btn-onoff " + (saved.enabled ? "on" : "off");
        c.lockBtn.textContent = saved.locked ? "\uD83D\uDD12" : "\uD83D\uDD13";
        c.lockBtn.className = "btn-lock" + (saved.locked ? " locked" : "");
        c.row.className = "slot-row " + (saved.enabled ? "enabled" : "disabled") + (saved.locked ? " locked" : "");
      }
    }
    setStatus(`Loaded: ${name}`);
    generateAndDisplay();
  });

  document.getElementById("btn-refresh-configs").addEventListener("click", refreshConfigList);
}

async function refreshConfigList() {
  const data = await api.fetchConfigs();
  const select = document.getElementById("config-select");
  select.innerHTML = '<option value="">(Select config)</option>';
  for (const name of data.configs || []) {
    const opt = document.createElement("option");
    opt.value = name;
    opt.textContent = name;
    select.appendChild(opt);
  }
}

/** Called on init to populate the config dropdown. */
export { refreshConfigList };

function setStatus(msg) {
  document.getElementById("save-status").textContent = msg;
}

// ─── Helpers ───

/** Apply randomization results to state + DOM. */
function applyResults(results) {
  for (const [name, res] of Object.entries(results)) {
    state.slots[name].value = res.value;
    state.slots[name].color = res.color;
    const c = allSlotComponents[name];
    if (c) {
      c.dropdown.value = res.value || "";
      c.colorSelect.value = res.color || "";
    }
  }
}
