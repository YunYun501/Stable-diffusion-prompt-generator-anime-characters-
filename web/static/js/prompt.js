/**
 * prompt.js - Prompt generation and display helpers.
 */

import { state, getSlotStateForAPI } from "./state.js";
import * as api from "./api.js";

const PREFIX_PRESET_VALUE = "sd_quality_v1";
const PREFIX_PRESET_TEXT = "(masterpiece),(best quality),(ultra-detailed),(best illustration),(absurdres),(very aesthetic),(newest),detailed eyes, detailed face";
const PROMPT_SLOT_ORDER = [
  "hair_color", "hair_length", "hair_style", "hair_texture",
  "eye_color", "eye_style",
  "body_type", "height", "skin", "age_appearance", "special_features",
  "expression",
  "full_body", "head", "neck", "upper_body", "waist", "lower_body",
  "outerwear", "hands", "legs", "feet", "accessory",
  "pose", "gesture",
  "background",
];

const outputColorCache = new Map();
let lastGeneratedPromptCore = "";

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

  const fullBody = state.slots.full_body;
  const fullBodyValue = fullBody && fullBody.enabled && fullBody.value ? fullBody.value : null;

  let lowerBodyCoversLegs = false;
  const lowerBody = state.slots.lower_body;
  if (lowerBody && lowerBody.enabled && lowerBody.value) {
    lowerBodyCoversLegs = !!state.lowerBodyCoversLegsByName[lowerBody.value];
  }
  if (state.fullBodyMode && fullBodyValue) {
    lowerBodyCoversLegs = false;
  }

  for (const slotName of PROMPT_SLOT_ORDER) {
    const slot = state.slots[slotName];
    if (!slot || !slot.enabled || !slot.value) continue;

    if (state.fullBodyMode && fullBodyValue && (slotName === "upper_body" || slotName === "lower_body")) {
      continue;
    }
    if (slotName === "legs" && lowerBodyCoversLegs) {
      continue;
    }

    let part = slot.color ? `${slot.color} ${slot.value}` : slot.value;
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

    const color = colorMap.get(token);
    if (!color) {
      outputEl.appendChild(document.createTextNode(token));
      return;
    }

    const span = document.createElement("span");
    span.className = "prompt-colored-part";
    span.style.color = colorTokenToCss(color);
    span.textContent = token;
    outputEl.appendChild(span);
  });
}

export function getPromptOutputText() {
  return combinePrompt(getPromptPrefix(), lastGeneratedPromptCore);
}

export function setPromptOutput(generatedPrompt) {
  lastGeneratedPromptCore = (generatedPrompt || "").trim();
  renderPromptOutput(lastGeneratedPromptCore);
}

export function clearPromptOutput() {
  lastGeneratedPromptCore = "";
  const outputEl = document.getElementById("prompt-output");
  if (outputEl) outputEl.innerHTML = "";
}

export async function generateAndDisplay() {
  const slotsForAPI = getSlotStateForAPI();
  const data = await api.generatePrompt(slotsForAPI, state.fullBodyMode, state.upperBodyMode);
  setPromptOutput(data.prompt || "");
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
    renderPromptOutput(lastGeneratedPromptCore);
  });
}
