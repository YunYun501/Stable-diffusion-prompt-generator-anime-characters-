/**
 * components.js — DOM builder functions for slot rows and sections.
 */

import { state } from "./state.js";

/**
 * Create a single slot row element.
 * Returns { row, dropdown, colorSelect, weightInput, onoffBtn, lockBtn, randomBtn, colorRandomBtn }
 */
export function createSlotRow(slotName, slotDef) {
  const row = document.createElement("div");
  row.className = "slot-row enabled";
  row.dataset.slot = slotName;

  // On/Off button
  const onoffBtn = document.createElement("button");
  onoffBtn.className = "btn-onoff on";
  onoffBtn.textContent = "On";
  onoffBtn.title = "Toggle slot on/off";

  // Lock button
  const lockBtn = document.createElement("button");
  lockBtn.className = "btn-lock";
  lockBtn.textContent = "\uD83D\uDD13";
  lockBtn.title = "Lock (skip during randomize)";

  // Label
  const label = document.createElement("span");
  label.className = "slot-label";
  label.textContent = slotName.replace(/_/g, " ");

  // Dropdown
  const dropdown = document.createElement("select");
  dropdown.className = "slot-dropdown";
  const noneOpt = document.createElement("option");
  noneOpt.value = "";
  noneOpt.textContent = "(None)";
  dropdown.appendChild(noneOpt);
  for (const optName of (slotDef.options || [])) {
    const opt = document.createElement("option");
    opt.value = optName;
    opt.textContent = optName;
    dropdown.appendChild(opt);
  }

  // Random button
  const randomBtn = document.createElement("button");
  randomBtn.className = "btn-slot-random";
  randomBtn.textContent = "\uD83C\uDFB2";
  randomBtn.title = "Randomize this slot";

  // Color dropdown (hidden if no color support)
  const colorSelect = document.createElement("select");
  colorSelect.className = "slot-color" + (slotDef.has_color ? "" : " hidden");
  const noColorOpt = document.createElement("option");
  noColorOpt.value = "";
  noColorOpt.textContent = "(No Color)";
  colorSelect.appendChild(noColorOpt);
  for (const c of state.individualColors) {
    const opt = document.createElement("option");
    opt.value = c;
    opt.textContent = c;
    colorSelect.appendChild(opt);
  }

  // Color random button
  const colorRandomBtn = document.createElement("button");
  colorRandomBtn.className = "btn-color-random" + (slotDef.has_color ? "" : " hidden");
  colorRandomBtn.textContent = "\uD83C\uDFA8";
  colorRandomBtn.title = "Randomize color";

  // Weight input
  const weightInput = document.createElement("input");
  weightInput.type = "number";
  weightInput.className = "slot-weight";
  weightInput.value = "1.0";
  weightInput.min = "0.1";
  weightInput.max = "2.0";
  weightInput.step = "0.1";
  weightInput.title = "Prompt weight";

  // Assemble
  row.append(onoffBtn, lockBtn, label, dropdown, randomBtn, colorSelect, colorRandomBtn, weightInput);

  return { row, dropdown, colorSelect, weightInput, onoffBtn, lockBtn, randomBtn, colorRandomBtn };
}


/**
 * Create a section panel with header, section buttons, and slot rows.
 * Returns { element, slotComponents: {[slotName]: componentRefs} }
 */
export function createSection(sectionKey, sectionDef) {
  const section = document.createElement("div");
  section.className = "section";
  section.dataset.section = sectionKey;

  // Header
  const header = document.createElement("div");
  header.className = "section-header";

  const title = document.createElement("span");
  title.className = "section-title";
  title.textContent = `${sectionDef.icon} ${sectionDef.label}`;

  const buttons = document.createElement("div");
  buttons.className = "section-buttons";

  const randomBtn = document.createElement("button");
  randomBtn.className = "btn btn-sm section-random";
  randomBtn.textContent = "Random";

  const allOnBtn = document.createElement("button");
  allOnBtn.className = "btn btn-sm section-all-on";
  allOnBtn.textContent = "All On";

  const allOffBtn = document.createElement("button");
  allOffBtn.className = "btn btn-sm section-all-off";
  allOffBtn.textContent = "All Off";

  buttons.append(randomBtn, allOnBtn, allOffBtn);
  header.append(title, buttons);
  section.appendChild(header);

  // Slot rows
  const slotComponents = {};
  const slotNames = sectionDef.slots || [];

  if (sectionDef.columns) {
    // Multi-column layout (clothing)
    const columnsDiv = document.createElement("div");
    columnsDiv.className = "section-columns";
    for (const colSlots of sectionDef.columns) {
      const col = document.createElement("div");
      col.className = "section-column";
      for (const slotName of colSlots) {
        const def = state.slotDefs[slotName];
        if (!def) continue;
        const comps = createSlotRow(slotName, def);
        slotComponents[slotName] = comps;
        col.appendChild(comps.row);
      }
      columnsDiv.appendChild(col);
    }
    section.appendChild(columnsDiv);
  } else {
    // Single column
    const slotsDiv = document.createElement("div");
    slotsDiv.style.display = "flex";
    slotsDiv.style.flexDirection = "column";
    slotsDiv.style.gap = "var(--slot-gap)";
    for (const slotName of slotNames) {
      const def = state.slotDefs[slotName];
      if (!def) continue;
      const comps = createSlotRow(slotName, def);
      slotComponents[slotName] = comps;
      slotsDiv.appendChild(comps.row);
    }
    section.appendChild(slotsDiv);
  }

  return { element: section, slotComponents, randomBtn, allOnBtn, allOffBtn, slotNames };
}
