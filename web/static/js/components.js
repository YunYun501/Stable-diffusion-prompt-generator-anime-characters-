/**
 * components.js - DOM builder functions for slot rows and sections.
 */

import { state, localizeFromI18nMap } from "./state.js";
import { t } from "./i18n.js";

const LOCKED_ICON = "\uD83D\uDD12";
const UNLOCKED_ICON = "\uD83D\uDD13";
const GROUP_DISPLAY_ORDER = [
  "uniform_service",
  "japanese_traditional",
  "modern_everyday",
  "formal_fashion",
  "sports_stage",
  "armor_fantasy",
  "swimwear",
  "cute_themed",
  "props_tech",
];

function getSlotLabel(slotName) {
  return t(`slot_label_${slotName}`);
}

function createSlotOptionElement(opt) {
  const el = document.createElement("option");
  el.value = opt.id;
  el.textContent = localizeFromI18nMap(opt.name_i18n, state.uiLocale, opt.name || opt.id || "");
  return el;
}

function getOptionGroupKey(opt) {
  if (!opt || typeof opt.group !== "string") return "";
  return opt.group.trim();
}

function getOptionGroupLabel(opt) {
  const key = getOptionGroupKey(opt);
  if (!key) return "";

  // Prefer UI bundle keys so group headers always follow UI language toggle.
  const i18nKey = `group_${key}`;
  const fromUiBundle = t(i18nKey);
  if (fromUiBundle !== i18nKey) {
    return fromUiBundle;
  }

  return localizeFromI18nMap(opt.group_i18n, state.uiLocale, key);
}

function getGroupDisplayRank(groupKey) {
  const idx = GROUP_DISPLAY_ORDER.indexOf(groupKey);
  return idx >= 0 ? idx : Number.MAX_SAFE_INTEGER;
}

function populateSlotDropdown(slotName, dropdown, selectedValueId) {
  dropdown.innerHTML = "";

  const noneOpt = document.createElement("option");
  noneOpt.value = "";
  noneOpt.textContent = t("slot_none");
  dropdown.appendChild(noneOpt);

  const slotDef = state.slotDefs[slotName];
  const options = slotDef?.options || [];
  const hasGroups = options.some((opt) => getOptionGroupKey(opt));

  if (!hasGroups) {
    for (const opt of options) {
      dropdown.appendChild(createSlotOptionElement(opt));
    }
    dropdown.value = selectedValueId || "";
    return;
  }

  const grouped = new Map();
  const ungrouped = [];

  for (const opt of options) {
    const groupKey = getOptionGroupKey(opt);
    if (!groupKey) {
      ungrouped.push(opt);
      continue;
    }
    if (!grouped.has(groupKey)) {
      grouped.set(groupKey, {
        label: getOptionGroupLabel(opt),
        options: [],
      });
    }
    grouped.get(groupKey).options.push(opt);
  }

  const sortedGroups = Array.from(grouped.entries()).sort((a, b) => {
    const [aKey, aData] = a;
    const [bKey, bData] = b;
    const rankDelta = getGroupDisplayRank(aKey) - getGroupDisplayRank(bKey);
    if (rankDelta !== 0) return rankDelta;
    return aData.label.localeCompare(bData.label);
  });

  for (const [, groupData] of sortedGroups) {
    const groupEl = document.createElement("optgroup");
    groupEl.label = groupData.label;
    for (const opt of groupData.options) {
      groupEl.appendChild(createSlotOptionElement(opt));
    }
    dropdown.appendChild(groupEl);
  }

  for (const opt of ungrouped) {
    dropdown.appendChild(createSlotOptionElement(opt));
  }

  dropdown.value = selectedValueId || "";
}

function populateColorDropdown(colorSelect, selectedColor) {
  colorSelect.innerHTML = "";

  const noColorOpt = document.createElement("option");
  noColorOpt.value = "";
  noColorOpt.textContent = t("slot_no_color");
  colorSelect.appendChild(noColorOpt);

  for (const colorToken of state.individualColors) {
    const opt = document.createElement("option");
    opt.value = colorToken;
    // Use i18n map directly for better locale handling
    const i18nMap = state.individualColorsI18n[colorToken];
    opt.textContent = localizeFromI18nMap(i18nMap, state.uiLocale, colorToken);
    colorSelect.appendChild(opt);
  }

  colorSelect.value = selectedColor || "";
}

/**
 * Create a single slot row element.
 * Returns row refs used by handlers.
 */
export function createSlotRow(slotName, slotDef) {
  const slotState = state.slots[slotName] || { enabled: true, locked: false };
  const row = document.createElement("div");
  row.className = "slot-row " + (slotState.enabled ? "enabled" : "disabled") + (slotState.locked ? " locked" : "");
  row.dataset.slot = slotName;

  const onoffBtn = document.createElement("button");
  onoffBtn.className = "btn-onoff " + (slotState.enabled ? "on" : "off");
  onoffBtn.textContent = slotState.enabled ? t("slot_on") : t("slot_off");
  onoffBtn.title = t("slot_toggle_title");

  const lockBtn = document.createElement("button");
  lockBtn.className = "btn-lock" + (slotState.locked ? " locked" : "");
  lockBtn.textContent = slotState.locked ? LOCKED_ICON : UNLOCKED_ICON;
  lockBtn.title = t("slot_lock_title");

  const label = document.createElement("span");
  label.className = "slot-label";
  label.textContent = getSlotLabel(slotName);

  const dropdown = document.createElement("select");
  dropdown.className = "slot-dropdown";
  populateSlotDropdown(slotName, dropdown, slotState.value_id);

  const randomBtn = document.createElement("button");
  randomBtn.className = "btn-slot-random";
  randomBtn.textContent = "\uD83C\uDFB2";
  randomBtn.title = t("slot_randomize_title");

  const colorSelect = document.createElement("select");
  colorSelect.className = "slot-color" + (slotDef.has_color ? "" : " hidden");
  populateColorDropdown(colorSelect, slotState.color);

  const colorRandomBtn = document.createElement("button");
  colorRandomBtn.className = "btn-color-random" + (slotDef.has_color ? "" : " hidden");
  colorRandomBtn.textContent = "\uD83C\uDFA8";
  colorRandomBtn.title = t("slot_color_random_title");

  const weightInput = document.createElement("input");
  weightInput.type = "number";
  weightInput.className = "slot-weight";
  weightInput.value = String(slotState.weight ?? 1.0);
  weightInput.min = "0.1";
  weightInput.max = "2.0";
  weightInput.step = "0.1";
  weightInput.title = t("slot_weight_title");

  row.append(onoffBtn, lockBtn, label, dropdown, randomBtn, colorSelect, colorRandomBtn, weightInput);

  return {
    row,
    label,
    dropdown,
    colorSelect,
    weightInput,
    onoffBtn,
    lockBtn,
    randomBtn,
    colorRandomBtn,
  };
}

/**
 * Create a section panel with header, section buttons, and slot rows.
 * Returns section refs used by handlers.
 */
export function createSection(sectionKey, sectionDef) {
  const section = document.createElement("div");
  section.className = "section";
  section.dataset.section = sectionKey;

  const header = document.createElement("div");
  header.className = "section-header";

  const title = document.createElement("span");
  title.className = "section-title";
  title.textContent = `${sectionDef.icon} ${t(sectionDef.label_key || `section_${sectionKey}`)}`;

  const buttons = document.createElement("div");
  buttons.className = "section-buttons";

  const randomBtn = document.createElement("button");
  randomBtn.className = "btn btn-sm section-random";
  randomBtn.textContent = t("section_random");

  const allOnBtn = document.createElement("button");
  allOnBtn.className = "btn btn-sm section-all-on";
  allOnBtn.textContent = t("section_all_on");

  const allOffBtn = document.createElement("button");
  allOffBtn.className = "btn btn-sm section-all-off";
  allOffBtn.textContent = t("section_all_off");

  buttons.append(randomBtn, allOnBtn, allOffBtn);
  header.append(title, buttons);
  section.appendChild(header);

  const slotComponents = {};
  const slotNames = sectionDef.slots || [];

  if (sectionDef.columns) {
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
