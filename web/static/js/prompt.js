/**
 * prompt.js — Prompt generation and clipboard utilities.
 */

import { state, getSlotStateForAPI } from "./state.js";
import * as api from "./api.js";

/** Generate prompt from current state and display in the textarea. */
export async function generateAndDisplay() {
  const slotsForAPI = getSlotStateForAPI();
  const data = await api.generatePrompt(slotsForAPI, state.fullBodyMode);
  document.getElementById("prompt-output").value = data.prompt || "";
}
