/**
 * prompt.js - Prompt generation and display helpers.
 */

import { state, getColorLabel, getSlotOptionLabel, getSlotStateForAPI } from "./state.js";
import * as api from "./api.js";
import { addToHistory } from "./history.js";

const PREFIX_PRESET_VALUE = "sd_quality_v1";
const PREFIX_PRESET_TEXT = "(masterpiece),(best quality),(ultra-detailed),(best illustration),(absurdres),(very aesthetic),(newest),detailed eyes, detailed face";
const PROMPT_SLOT_ORDER = [
  "hair_color", "hair_length", "hair_style", "hair_texture",
  "eye_color", "eye_expression_quality", "eye_shape", "eye_pupil_state",
  "eye_state", "eye_accessories",
  "body_type", "height", "skin", "age_appearance", "special_features",
  "expression",
  "full_body", "head", "neck", "upper_body", "waist", "lower_body",
  "outerwear", "hands", "legs", "feet", "accessory",
  "view_angle", "pose", "gesture",
  "background",
];

const outputColorCache = new Map();
let lastGeneratedPromptCore = "";
let lastGeneratedLocale = "en";
let generateRequestSeq = 0;
let generateTimer = null;
const GENERATE_DEBOUNCE_MS = 150;

/** Set of unmatched tokens from last parse (used for highlighting). */
let parsedUnmatchedTokens = new Set();
let isParsedHighlightActive = false;

function getPromptPrefix() {
  const el = document.getElementById("prompt-prefix");
  return (el?.value || "").trim();
}

export function combinePrompt(prefix, generatedPrompt) {
  const p = (prefix || "").trim();
  const g = (generatedPrompt || "").trim();
  if (!p) return g;
  if (!g) return p;
  if (p.endsWith(", ")) return p + g;
  if (p.endsWith(",")) return `${p} ${g}`;
  if (p.endsWith(" ")) return p + g;
  return `${p}, ${g}`;
}

function shouldColorizePromptOutput() {
  const toggle = document.getElementById("prompt-colorize-toggle");
  return toggle ? !!toggle.checked : true;
}

function buildGeneratedPartColorMap() {
  const map = new Map();
  // Use the locale that was used to generate the prompt, not the current state
  const locale = lastGeneratedLocale;

  const fullBody = state.slots.full_body;
  const fullBodyValueId = fullBody && fullBody.enabled && fullBody.value_id ? fullBody.value_id : null;

  let lowerBodyCoversLegs = false;
  const lowerBody = state.slots.lower_body;
  if (lowerBody && lowerBody.enabled && lowerBody.value_id) {
    lowerBodyCoversLegs = !!state.lowerBodyCoversLegsById[lowerBody.value_id];
  }
  if (state.fullBodyMode && fullBodyValueId) {
    lowerBodyCoversLegs = false;
  }

  for (const slotName of PROMPT_SLOT_ORDER) {
    const slot = state.slots[slotName];
    if (!slot || !slot.enabled || !slot.value_id) continue;

    if (state.fullBodyMode && fullBodyValueId && (slotName === "upper_body" || slotName === "lower_body")) {
      continue;
    }
    if (slotName === "legs" && lowerBodyCoversLegs) {
      continue;
    }

    const valueLabel = getSlotOptionLabel(slotName, slot.value_id, locale);
    if (!valueLabel) continue;

    let part;
    if (slot.color) {
      part = `${getColorLabel(slot.color, locale)} ${valueLabel}`;
    } else {
      part = valueLabel;
    }

    const weight = Number(slot.weight);
    if (Number.isFinite(weight) && Math.abs(weight - 1.0) > 1e-9) {
      part = `(${part}:${weight.toFixed(1)})`;
    }

    if (slot.color) {
      map.set(part, slot.color);
    }
  }
  return map;
}

function colorTokenToCss(token) {
  const key = (token || "").trim().toLowerCase();
  if (!key) return "#999";
  const cached = outputColorCache.get(key);
  if (cached) return cached;

  if (typeof CSS !== "undefined" && CSS.supports("color", key)) {
    outputColorCache.set(key, key);
    return key;
  }

  const compact = key.replace(/[\s_-]+/g, "");
  if (typeof CSS !== "undefined" && CSS.supports("color", compact)) {
    outputColorCache.set(key, compact);
    return compact;
  }

  let hash = 0;
  for (let i = 0; i < key.length; i += 1) {
    hash = (hash * 31 + key.charCodeAt(i)) % 360;
  }
  const fallback = `hsl(${Math.abs(hash)} 55% 45%)`;
  outputColorCache.set(key, fallback);
  return fallback;
}

function renderPromptOutput(generatedPromptCore) {
  const outputEl = document.getElementById("prompt-output");
  if (!outputEl) return;

  const prefix = getPromptPrefix();
  const generated = (generatedPromptCore || "").trim();
  const combined = combinePrompt(prefix, generated);

  outputEl.innerHTML = "";
  if (!combined) return;

  if (!shouldColorizePromptOutput()) {
    outputEl.textContent = combined;
    return;
  }

  if (prefix) {
    outputEl.appendChild(document.createTextNode(prefix));
    if (generated) {
      outputEl.appendChild(document.createTextNode(", "));
    }
  }
  if (!generated) return;

  const colorMap = buildGeneratedPartColorMap();
  const tokens = generated
    .split(",")
    .map((t) => t.trim())
    .filter((t) => t.length > 0);

  tokens.forEach((token, index) => {
    if (index > 0) {
      outputEl.appendChild(document.createTextNode(", "));
    }

    const colorToken = colorMap.get(token);
    if (!colorToken) {
      outputEl.appendChild(document.createTextNode(token));
      return;
    }

    const span = document.createElement("span");
    span.className = "prompt-colored-part";
    span.style.color = colorTokenToCss(colorToken);
    span.textContent = token;
    outputEl.appendChild(span);
  });
}

export function getPromptOutputText() {
  // Read directly from DOM to support user edits/pastes
  const outputEl = document.getElementById("prompt-output");
  if (outputEl) {
    return outputEl.textContent.trim();
  }
  return combinePrompt(getPromptPrefix(), lastGeneratedPromptCore);
}

export function setPromptOutput(generatedPrompt, locale) {
  lastGeneratedPromptCore = (generatedPrompt || "").trim();
  if (locale) {
    lastGeneratedLocale = locale;
  }
  renderPromptOutput(lastGeneratedPromptCore);
}

export function commitGeneratedPrompt(generatedPrompt, locale, skipHistory = false) {
  const normalized = (generatedPrompt || "").trim();
  const prefix = getPromptPrefix();
  setPromptOutput(normalized, locale);
  if (!skipHistory && normalized) {
    addToHistory(combinePrompt(prefix, normalized), prefix);
  }
}

export function clearPromptOutput() {
  lastGeneratedPromptCore = "";
  clearParsedPromptHighlight();
  const outputEl = document.getElementById("prompt-output");
  if (outputEl) outputEl.innerHTML = "";
}

/**
 * Normalize a token for comparison (lowercase, trim, remove weight syntax).
 */
function normalizeTokenForMatch(token) {
  let t = (token || "").trim().toLowerCase();
  // Remove weight syntax like (xxx:1.2)
  const weightMatch = t.match(/^\((.+):[\d.]+\)$/);
  if (weightMatch) {
    t = weightMatch[1];
  }
  return t;
}

/**
 * Render prompt output with parsed token highlighting.
 * Matched tokens (not in unmatched list) are shown in orange.
 */
function renderParsedPromptOutput(promptText, unmatchedList) {
  const outputEl = document.getElementById("prompt-output");
  if (!outputEl) return;

  outputEl.innerHTML = "";
  if (!promptText || !promptText.trim()) return;

  // Build set of normalized unmatched tokens
  const unmatchedSet = new Set(
    unmatchedList.map((t) => normalizeTokenForMatch(t))
  );

  const tokens = promptText
    .split(",")
    .map((t) => t.trim())
    .filter((t) => t.length > 0);

  tokens.forEach((token, index) => {
    if (index > 0) {
      outputEl.appendChild(document.createTextNode(", "));
    }

    const normalized = normalizeTokenForMatch(token);
    const isMatched = !unmatchedSet.has(normalized);

    if (isMatched) {
      const span = document.createElement("span");
      span.className = "prompt-parsed-match";
      span.style.color = "#f59e0b";
      span.style.fontWeight = "600";
      span.textContent = token;
      outputEl.appendChild(span);
    } else {
      outputEl.appendChild(document.createTextNode(token));
    }
  });
}

/**
 * Activate parsed prompt highlighting with the given unmatched tokens.
 */
export function setParsedPromptHighlight(promptText, unmatchedList) {
  parsedUnmatchedTokens = new Set(unmatchedList || []);
  isParsedHighlightActive = true;
  renderParsedPromptOutput(promptText, unmatchedList || []);
}

/**
 * Clear parsed prompt highlighting state.
 */
export function clearParsedPromptHighlight() {
  parsedUnmatchedTokens.clear();
  isParsedHighlightActive = false;
}

async function generateAndDisplayNow(skipHistory = false) {
  const requestSeq = ++generateRequestSeq;
  const slotsForAPI = getSlotStateForAPI();
  // Capture locale and prefix at call time for consistency
  const promptLocale = state.promptLocale;
  const data = await api.generatePrompt(
    slotsForAPI,
    state.fullBodyMode,
    state.upperBodyMode,
    promptLocale,
  );
  if (requestSeq !== generateRequestSeq) return;
  commitGeneratedPrompt(data.prompt || "", promptLocale, skipHistory);
}

export function generateAndDisplay(skipHistory = false, options = {}) {
  const immediate = !!options.immediate;
  if (immediate) {
    if (generateTimer) {
      clearTimeout(generateTimer);
      generateTimer = null;
    }
    return generateAndDisplayNow(skipHistory);
  }
  if (generateTimer) {
    clearTimeout(generateTimer);
  }
  generateTimer = setTimeout(() => {
    generateTimer = null;
    void generateAndDisplayNow(skipHistory);
  }, GENERATE_DEBOUNCE_MS);
  return Promise.resolve();
}

export function wirePromptPrefixPreset() {
  const presetSelect = document.getElementById("prompt-prefix-preset");
  const prefixInput = document.getElementById("prompt-prefix");
  const colorizeToggle = document.getElementById("prompt-colorize-toggle");
  if (!presetSelect || !prefixInput || !colorizeToggle) return;

  presetSelect.value = "";
  prefixInput.value = "";
  colorizeToggle.checked = true;

  presetSelect.addEventListener("change", () => {
    if (presetSelect.value === PREFIX_PRESET_VALUE) {
      prefixInput.value = PREFIX_PRESET_TEXT;
    } else {
      prefixInput.value = "";
    }
    renderPromptOutput(lastGeneratedPromptCore);
  });

  prefixInput.addEventListener("input", () => {
    renderPromptOutput(lastGeneratedPromptCore);
  });

  colorizeToggle.addEventListener("change", () => {
    // Preserve user-edited content when toggling colorize
    const outputEl = document.getElementById("prompt-output");
    if (outputEl) {
      const currentText = outputEl.textContent.trim();
      // Remove prefix from the beginning if present to get just the core prompt
      const prefix = getPromptPrefix();
      let coreText = currentText;
      if (prefix && currentText.startsWith(prefix)) {
        coreText = currentText.slice(prefix.length).replace(/^,\s*/, "").trim();
      }
      lastGeneratedPromptCore = coreText;
    }
    renderPromptOutput(lastGeneratedPromptCore);
  });
}
