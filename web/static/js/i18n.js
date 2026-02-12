/**
 * i18n.js - UI localization and locale state (UI vs prompt output).
 */

export const SUPPORTED_LOCALES = ["en", "zh"];
const DEFAULT_LOCALE = "en";
const UI_STORAGE_KEY = "ui_locale";
const PROMPT_STORAGE_KEY = "prompt_locale";

let currentUiLocale = DEFAULT_LOCALE;
let currentPromptLocale = DEFAULT_LOCALE;
let uiStrings = {};

const uiLocaleListeners = [];
const promptLocaleListeners = [];

async function loadUiStrings(locale) {
  const res = await fetch(`/static/i18n/${locale}.json`);
  uiStrings = await res.json();
}

function normalizeLocale(code) {
  const raw = (code || DEFAULT_LOCALE).toLowerCase();
  if (raw.startsWith("zh")) return "zh";
  return "en";
}

/** Look up a UI string by key. Supports {param} replacement. */
export function t(key, params) {
  let str = (key in uiStrings) ? uiStrings[key] : key;
  if (params) {
    for (const [k, v] of Object.entries(params)) {
      str = str.replace(`{${k}}`, v);
    }
  }
  return str;
}

export function getUiLocale() {
  return currentUiLocale;
}

export function getPromptLocale() {
  return currentPromptLocale;
}

export async function setUiLocale(code) {
  const locale = normalizeLocale(code);
  if (!SUPPORTED_LOCALES.includes(locale)) return;
  currentUiLocale = locale;
  localStorage.setItem(UI_STORAGE_KEY, locale);
  await loadUiStrings(locale);
  for (const fn of uiLocaleListeners) fn(locale);
}

export function setPromptLocale(code) {
  const locale = normalizeLocale(code);
  if (!SUPPORTED_LOCALES.includes(locale)) return;
  currentPromptLocale = locale;
  localStorage.setItem(PROMPT_STORAGE_KEY, locale);
  for (const fn of promptLocaleListeners) fn(locale);
}

export function onUiLocaleChange(fn) {
  uiLocaleListeners.push(fn);
}

export function onPromptLocaleChange(fn) {
  promptLocaleListeners.push(fn);
}

/** Initialize locale settings and UI bundle. */
export async function initI18n() {
  const savedUi = localStorage.getItem(UI_STORAGE_KEY);
  const savedPrompt = localStorage.getItem(PROMPT_STORAGE_KEY);

  currentUiLocale = SUPPORTED_LOCALES.includes(savedUi) ? savedUi : DEFAULT_LOCALE;
  currentPromptLocale = SUPPORTED_LOCALES.includes(savedPrompt) ? savedPrompt : currentUiLocale;

  await loadUiStrings(currentUiLocale);
}
