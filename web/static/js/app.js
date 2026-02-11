/**
 * app.js — Entry point. Fetches data, builds UI, wires all events.
 */

import { state, initSlotState } from "./state.js";
import * as api from "./api.js";
import { createSection } from "./components.js";
import { setSlotComponents, wireSlotEvents, wireSectionEvents, wireGlobalEvents, wireSaveLoadEvents, refreshConfigList } from "./handlers.js";

async function init() {
  // 1. Fetch slot definitions + palettes in parallel
  const [slotsData, palettesData] = await Promise.all([
    api.fetchSlots(),
    api.fetchPalettes(),
  ]);

  // 2. Store data in state
  state.sections = slotsData.sections;
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

  // 8. Load saved configs list
  refreshConfigList();
}

init();
