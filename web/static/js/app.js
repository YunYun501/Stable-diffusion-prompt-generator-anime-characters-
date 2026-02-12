/**
 * app.js - Entry point. Fetches data, builds UI, wires events and localization.
 */

import { state, initSlotState } from "./state.js";
import * as api from "./api.js";
import { createSection } from "./components.js";
import {
  setSlotComponents,
  wireSlotEvents,
  wireSectionEvents,
  wireGlobalEvents,
  wireSaveLoadEvents,
  refreshConfigList,
  refreshLocalizedDynamicUi,
  restoreFromHistory,
} from "./handlers.js";
import { wirePromptPrefixPreset, generateAndDisplay } from "./prompt.js";
import {
  SUPPORTED_LOCALES,
  getPromptLocale,
  getUiLocale,
  initI18n,
  onPromptLocaleChange,
  onUiLocaleChange,
  setPromptLocale,
  setUiLocale,
  t,
} from "./i18n.js";
import {
  getHistory,
  removeFromHistory,
  clearHistory,
  onHistoryChange,
  formatTimestamp,
  downloadExport,
  triggerImport,
} from "./history.js";

function populateLocaleSelector(selectEl, selected) {
  if (!selectEl) return;
  selectEl.innerHTML = "";
  for (const code of SUPPORTED_LOCALES) {
    const opt = document.createElement("option");
    opt.value = code;
    opt.textContent = t(`lang_option_${code}`);
    selectEl.appendChild(opt);
  }
  selectEl.value = selected;
}

function applyStaticTranslations() {
  document.documentElement.lang = state.uiLocale;
  document.title = t("page_title");

  const setText = (id, key) => {
    const el = document.getElementById(id);
    if (el) el.textContent = t(key);
  };

  setText("page-heading", "page_heading");
  setText("ui-lang-label", "ui_lang_selector_label");
  setText("prompt-lang-label", "prompt_lang_selector_label");
  setText("prompt-prefix-label", "prefix_label");
  setText("prefix-preset-label", "prefix_preset_label");
  setText("prefix-preset-none", "prefix_preset_none");
  setText("prefix-preset-sd", "prefix_preset_sd_quality");
  setText("colorize-label", "colorize_label");
  setText("btn-generate", "btn_generate");
  setText("btn-randomize-all", "btn_randomize_all");
  setText("btn-copy", "btn_copy");
  setText("btn-reset", "btn_reset");
  setText("setting-full-body", "setting_full_body");
  setText("setting-upper-body", "setting_upper_body");
  setText("setting-palette", "setting_palette");
  setText("palette-label", "palette_label");
  setText("btn-palette-random", "btn_palette_random");
  setText("save-load-summary", "save_load_summary");
  setText("btn-save", "btn_save");
  setText("btn-load", "btn_load");
  setText("btn-refresh-configs", "btn_refresh");
  setText("btn-export", "btn_export");
  setText("btn-import", "btn_import");
  setText("btn-clear-history", "history_clear_all");

  // Update history summary with count
  const historySummary = document.getElementById("history-summary");
  if (historySummary) {
    const count = getHistory().length;
    historySummary.childNodes[0].textContent = t("history_summary") + " (";
  }

  const prefixInput = document.getElementById("prompt-prefix");
  if (prefixInput) prefixInput.placeholder = t("prefix_placeholder");

  const configName = document.getElementById("config-name");
  if (configName) configName.placeholder = t("config_name_placeholder");

  const output = document.getElementById("prompt-output");
  if (output) output.setAttribute("data-placeholder", t("prompt_placeholder"));

  const paletteRandom = document.getElementById("btn-palette-random");
  if (paletteRandom) paletteRandom.title = t("btn_palette_random_title");

  const uiLangSelect = document.getElementById("ui-lang-select");
  const promptLangSelect = document.getElementById("prompt-lang-select");
  populateLocaleSelector(uiLangSelect, state.uiLocale);
  populateLocaleSelector(promptLangSelect, state.promptLocale);
}

function buildSections() {
  const container = document.getElementById("sections-container");
  container.innerHTML = "";

  const allComponents = {};
  for (const [key, sectionDef] of Object.entries(state.sections)) {
    const sectionData = createSection(key, sectionDef);
    container.appendChild(sectionData.element);

    Object.assign(allComponents, sectionData.slotComponents);
    wireSectionEvents(sectionData);
  }

  setSlotComponents(allComponents);
  for (const [slotName, comps] of Object.entries(allComponents)) {
    wireSlotEvents(slotName, comps);
  }
}

function wireLocaleSelectors() {
  const uiLangSelect = document.getElementById("ui-lang-select");
  const promptLangSelect = document.getElementById("prompt-lang-select");

  if (uiLangSelect) {
    uiLangSelect.addEventListener("change", async (e) => {
      await setUiLocale(e.target.value);
    });
  }
  if (promptLangSelect) {
    promptLangSelect.addEventListener("change", (e) => {
      setPromptLocale(e.target.value);
    });
  }

  onUiLocaleChange(async (locale) => {
    state.uiLocale = locale;
    applyStaticTranslations();
    buildSections();
    refreshLocalizedDynamicUi();
    renderHistoryList();
    await refreshConfigList();
  });

  onPromptLocaleChange((locale) => {
    state.promptLocale = locale;
    generateAndDisplay();
  });
}

function renderHistoryList() {
  const listEl = document.getElementById("history-list");
  const countEl = document.getElementById("history-count");
  if (!listEl) return;

  const history = getHistory();
  countEl.textContent = history.length;

  listEl.innerHTML = "";

  if (history.length === 0) {
    const emptyMsg = document.createElement("div");
    emptyMsg.className = "history-empty";
    emptyMsg.textContent = t("history_empty");
    listEl.appendChild(emptyMsg);
    return;
  }

  for (const entry of history) {
    const item = document.createElement("div");
    item.className = "history-item";
    item.dataset.id = entry.id;

    const header = document.createElement("div");
    header.className = "history-item-header";

    const timeSpan = document.createElement("span");
    timeSpan.className = "history-time";
    timeSpan.textContent = formatTimestamp(entry.timestamp);

    const promptPreview = document.createElement("span");
    promptPreview.className = "history-prompt-preview";
    promptPreview.textContent = entry.prompt.length > 60
      ? entry.prompt.slice(0, 60) + "..."
      : entry.prompt;

    const actions = document.createElement("span");
    actions.className = "history-actions";

    const expandBtn = document.createElement("button");
    expandBtn.className = "btn btn-xs";
    expandBtn.textContent = "▼";
    expandBtn.title = t("history_expand");
    expandBtn.addEventListener("click", () => {
      const isExpanded = item.classList.toggle("expanded");
      expandBtn.textContent = isExpanded ? "▲" : "▼";
      expandBtn.title = isExpanded ? t("history_collapse") : t("history_expand");
    });

    const copyBtn = document.createElement("button");
    copyBtn.className = "btn btn-xs";
    copyBtn.textContent = t("history_copy");
    copyBtn.addEventListener("click", () => {
      navigator.clipboard.writeText(entry.prompt);
    });

    const restoreBtn = document.createElement("button");
    restoreBtn.className = "btn btn-xs";
    restoreBtn.textContent = t("history_restore");
    restoreBtn.addEventListener("click", () => {
      restoreFromHistory(entry);
    });

    const deleteBtn = document.createElement("button");
    deleteBtn.className = "btn btn-xs btn-danger";
    deleteBtn.textContent = "×";
    deleteBtn.title = t("history_delete");
    deleteBtn.addEventListener("click", () => {
      removeFromHistory(entry.id);
    });

    actions.append(expandBtn, copyBtn, restoreBtn, deleteBtn);
    header.append(timeSpan, promptPreview, actions);

    const fullPrompt = document.createElement("div");
    fullPrompt.className = "history-prompt-full";
    fullPrompt.textContent = entry.prompt;

    item.append(header, fullPrompt);
    listEl.appendChild(item);
  }
}

function wireHistoryEvents() {
  const clearBtn = document.getElementById("btn-clear-history");
  if (clearBtn) {
    clearBtn.addEventListener("click", () => {
      if (confirm(t("history_clear_confirm"))) {
        clearHistory();
      }
    });
  }

  // Export/Import buttons
  const exportBtn = document.getElementById("btn-export");
  const importBtn = document.getElementById("btn-import");

  if (exportBtn) {
    exportBtn.addEventListener("click", () => {
      downloadExport();
    });
  }

  if (importBtn) {
    importBtn.addEventListener("click", () => {
      triggerImport((result) => {
        const statusEl = document.getElementById("save-status");
        if (result.success) {
          if (statusEl) statusEl.textContent = t("import_success", { count: result.count });
          renderHistoryList();
        } else {
          if (statusEl) statusEl.textContent = t("import_failed");
        }
      });
    });
  }

  // Listen for history changes
  onHistoryChange(() => {
    renderHistoryList();
  });
}

async function init() {
  await initI18n();
  state.uiLocale = getUiLocale();
  state.promptLocale = getPromptLocale();

  const [slotsData, palettesData] = await Promise.all([
    api.fetchSlots(),
    api.fetchPalettes(),
  ]);

  state.sections = slotsData.sections;
  state.lowerBodyCoversLegsById = slotsData.lower_body_covers_legs_by_id || {};
  state.poseUsesHandsById = slotsData.pose_uses_hands_by_id || {};
  state.individualColors = palettesData.individual_colors || [];
  state.individualColorsI18n = palettesData.individual_colors_i18n || {};
  state.palettes = palettesData.palettes || [];
  initSlotState(slotsData.slots);

  wireLocaleSelectors();
  applyStaticTranslations();

  buildSections();
  wireGlobalEvents();
  wireSaveLoadEvents();
  wireHistoryEvents();
  wirePromptPrefixPreset();
  refreshLocalizedDynamicUi();
  renderHistoryList();
  await refreshConfigList();
}

init();
