/**
 * app.js - Entry point. Fetches data, builds UI, wires all events.
 *
 * Change log (2026-02-11):
 * - Added default-off settings and default-disabled slot behavior
 *   (`full_body_mode`, `special_features`, `full_body`, `eye_style`, `hands`).
 * - Added constant prompt prefix support in output generation.
 * - Changed upper-body mode to a one-shot disable action for `waist`, `lower_body`, `full_body`, `legs`, `feet`.
 * - Added lower-body `covers_legs` constraints and backend/frontend enforcement.
 * - Changed "Always Include" prefix to default empty and added selectable legacy SD preset.
 * - Added toggleable colorized prompt output (default on) with high-contrast output styling.
 */
import { state, initSlotState } from "./state.js";
import * as api from "./api.js";
import { createSection } from "./components.js";
import { setSlotComponents, wireSlotEvents, wireSectionEvents, wireGlobalEvents, wireSaveLoadEvents, refreshConfigList } from "./handlers.js";
import { wirePromptPrefixPreset } from "./prompt.js";

async function init() {
  // 1. Fetch slot definitions + palettes in parallel
  const [slotsData, palettesData] = await Promise.all([
    api.fetchSlots(),
    api.fetchPalettes(),
  ]);

  // 2. Store data in state
  state.sections = slotsData.sections;
  state.lowerBodyCoversLegsByName = slotsData.lower_body_covers_legs_by_name || {};
  state.individualColors = palettesData.individual_colors || [];
  state.palettes = palettesData.palettes || [];
  initSlotState(slotsData.slots);

  // 3. Populate palette dropdown
  const paletteSelect = document.getElementById("palette-select");
  for (const p of state.palettes) {
    const opt = document.createElement("option");
    opt.value = p.id;
    opt.textContent = p.name;
    paletteSelect.appendChild(opt);
  }

  // 4. Build sections
  const container = document.getElementById("sections-container");
  const allComponents = {};

  for (const [key, sectionDef] of Object.entries(state.sections)) {
    const sectionData = createSection(key, sectionDef);
    container.appendChild(sectionData.element);

    // Collect slot components
    Object.assign(allComponents, sectionData.slotComponents);

    // Wire section buttons
    wireSectionEvents(sectionData);
  }

  // 5. Store all components for handler access
  setSlotComponents(allComponents);

  // 6. Wire per-slot events
  for (const [slotName, comps] of Object.entries(allComponents)) {
    wireSlotEvents(slotName, comps);
  }

  // 7. Wire global + save/load events
  wireGlobalEvents();
  wireSaveLoadEvents();
  wirePromptPrefixPreset();

  // 8. Load saved configs list
  refreshConfigList();
}

init();

