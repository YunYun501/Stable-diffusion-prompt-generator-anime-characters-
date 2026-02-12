# Developer Map - Where to Change Things

Quick-reference for finding the right file for any edit.

## Backend (Python)

| What to change | File | Notes |
|---|---|---|
| Slot definitions (add/remove slots, categories) | `generator/prompt_generator.py` | `SLOT_DEFINITIONS` dict |
| Slot order in prompt output | `web/routes/prompt.py` | `SLOT_ORDER` list |
| Prompt building logic (weight syntax, color prefix, output locale) | `web/routes/prompt.py` | `generate_prompt()` |
| Randomization logic | `web/routes/slots.py` | `randomize_slots()`, `randomize_all()` |
| Full-body specific outfit one-shot disable/restore | `web/static/js/handlers.js` | `applyFullBodyModeOneShotDisable()`, `restoreFullBodyModeOneShotDisabledSlots()` |
| Full-body randomization override behavior | `web/routes/slots.py` | Bottom of `randomize_all()` |
| Lower-body coverage -> legs one-shot off behavior | `web/static/js/handlers.js` | `maybeDisableLegsForLowerBodyCoverage()` using `covers_legs` metadata |
| Pose hand-usage -> hand actions one-shot off behavior | `web/static/js/handlers.js` | `maybeDisableHandActionsForPoseUsage()` using `uses_hands` metadata |
| Palette auto-apply logic | `web/routes/prompt.py` | `apply_palette()` |
| Section layout (which slots in which section) | `web/routes/slots.py` | `SECTION_LAYOUT` dict |
| Save/Load config format | `web/routes/configs.py` | `save_config()`, `load_config()` |
| API server setup, static mount | `web/server.py` | FastAPI app + router includes |
| Catalog loading (JSON data files) | `generator/prompt_generator.py` | `_load_catalogs()` |
| Lower-body `covers_legs` metadata lookup | `generator/prompt_generator.py` | `get_lower_body_covers_legs_by_id()` |
| Pose `uses_hands` metadata lookup | `generator/prompt_generator.py` | `get_pose_uses_hands_by_id()` |
| Color palette sampling | `generator/prompt_generator.py` | `sample_color_from_palette()` |
| Item localization and id/name resolution | `generator/prompt_generator.py` | `get_slot_options_localized()`, `resolve_slot_item()`, `resolve_slot_value_name()` |

## Frontend (HTML/CSS/JS)

| What to change | File | Notes |
|---|---|---|
| Page structure / HTML skeleton | `web/static/index.html` | Prompt area, settings bar, save/load |
| UI language + prompt language selectors | `web/static/index.html`, `web/static/js/app.js`, `web/static/js/i18n.js` | Independent language control for UI labels vs prompt output text |
| Theme colors, fonts, spacing | `web/static/css/variables.css` | CSS custom properties |
| Page grid, section columns, responsive | `web/static/css/layout.css` | Flexbox rules |
| Slot row appearance (sizes, borders) | `web/static/css/slots.css` | `.slot-row`, `.slot-dropdown`, etc. |
| Button styles, inputs, toggles | `web/static/css/controls.css` | `.btn`, `.btn-onoff`, `.btn-lock` |
| Slot row DOM creation | `web/static/js/components.js` | `createSlotRow()` |
| Grouped dropdown rendering (optgroup by catalog group metadata) | `web/static/js/components.js` | `populateSlotDropdown()` |
| Section DOM creation | `web/static/js/components.js` | `createSection()` |
| On/Off toggle, Lock toggle | `web/static/js/handlers.js` | `wireSlotEvents()` |
| Randomize All, Reset, Copy | `web/static/js/handlers.js` | `wireGlobalEvents()` |
| Section Random/All On/All Off | `web/static/js/handlers.js` | `wireSectionEvents()` |
| Palette auto-apply on select | `web/static/js/handlers.js` | Inside `wireGlobalEvents()` palette listener |
| Slot one-shot disable helpers | `web/static/js/handlers.js` | `applyUpperBodyModeOneShotDisable()`, `maybeDisableLegsForLowerBodyCoverage()`, `maybeDisableHandActionsForPoseUsage()` |
| Save/Load config UI | `web/static/js/handlers.js` | `wireSaveLoadEvents()` |
| Prompt generation display | `web/static/js/prompt.js` | `generateAndDisplay()` |
| Colorized prompt output rendering | `web/static/js/prompt.js`, `web/static/index.html` | `setPromptOutput()`, `renderPromptOutput()` |
| Always-include prefix preset behavior | `web/static/js/prompt.js`, `web/static/index.html` | `wirePromptPrefixPreset()` |
| All API fetch calls | `web/static/js/api.js` | One function per endpoint; includes `output_language` for prompt APIs |
| State shape, init, getters | `web/static/js/state.js` | `state` object, `value_id` model, localization helpers |
| Init flow, wiring order | `web/static/js/app.js` | `init()` - orchestrator + locale listeners |
| History UI rendering | `web/static/js/app.js` | `renderHistoryList()`, `wireHistoryEvents()` |
| History state management | `web/static/js/history.js` | `addToHistory()`, `getHistory()`, `removeFromHistory()`, `clearHistory()` |
| History export/import | `web/static/js/history.js` | `exportUserData()`, `importUserData()`, `downloadExport()`, `triggerImport()` |
| History restoration | `web/static/js/handlers.js` | `restoreFromHistory()` - restores full slot state from history entry |
| UI translation bundles | `web/static/i18n/en.json`, `web/static/i18n/zh.json` | UI copy, slot labels, section labels, history strings |

## Data (JSON catalogs)

| What to change | File |
|---|---|
| Hair options | `prompt data/hair/hair_catalog.json` |
| Eye options | `prompt data/eyes/eye_catalog.json` |
| Body features | `prompt data/body/body_features.json` |
| Expressions | `prompt data/expressions/female_expressions.json` |
| Clothing items | `prompt data/clothing/clothing_list.json` |
| Clothing style grouping metadata | `prompt data/clothing/clothing_list.json` | item-level `style_group` + catalog-level `style_groups_i18n` |
| Lower-body leg-coverage flags | `prompt data/clothing/clothing_list.json` | `covers_legs` on `body_part == lower_body` items |
| Poses | `prompt data/poses/poses.json` |
| Pose `uses_hands` metadata | `prompt data/poses/poses.json` | item-level flag for pose->hand-actions one-shot disable |
| Backgrounds | `prompt data/backgrounds/backgrounds.json` |
| Color palettes + individual colors | `prompt data/colors/color_palettes.json` |
| Multilingual item names (`name_i18n`) | `prompt data/*/*.json` catalogs | per-item `name_i18n.en` / `name_i18n.zh` |
| Multilingual palette/color labels | `prompt data/colors/color_palettes.json` | `name_i18n`, `description_i18n`, `individual_colors_i18n` |
| Saved character presets | `prompt data/configs/*.json` |

## Entry Points

| Script | What it launches |
|---|---|
| `python run_Fastapi.py` | FastAPI + vanilla HTML/JS UI (new) |
