# Developer Map — Where to Change Things

Quick-reference for finding the right file for any edit.

## Backend (Python)

| What to change | File | Notes |
|---|---|---|
| Slot definitions (add/remove slots, categories) | `generator/prompt_generator.py` | `SLOT_DEFINITIONS` dict |
| Slot order in prompt output | `web/routes/prompt.py` | `SLOT_ORDER` list |
| Prompt building logic (weight syntax, color prefix) | `web/routes/prompt.py` | `generate_prompt()` |
| Randomization logic | `web/routes/slots.py` | `randomize_slots()`, `randomize_all()` |
| Full-body override behavior | `web/routes/slots.py` | Bottom of `randomize_all()` |
| Palette auto-apply logic | `web/routes/prompt.py` | `apply_palette()` |
| Section layout (which slots in which section) | `web/routes/slots.py` | `SECTION_LAYOUT` dict |
| Save/Load config format | `web/routes/configs.py` | `save_config()`, `load_config()` |
| API server setup, static mount | `web/server.py` | FastAPI app + router includes |
| Catalog loading (JSON data files) | `generator/prompt_generator.py` | `_load_catalogs()` |
| Color palette sampling | `generator/prompt_generator.py` | `sample_color_from_palette()` |

## Frontend (HTML/CSS/JS)

| What to change | File | Notes |
|---|---|---|
| Page structure / HTML skeleton | `web/static/index.html` | Prompt area, settings bar, save/load |
| Theme colors, fonts, spacing | `web/static/css/variables.css` | CSS custom properties |
| Page grid, section columns, responsive | `web/static/css/layout.css` | Flexbox rules |
| Slot row appearance (sizes, borders) | `web/static/css/slots.css` | `.slot-row`, `.slot-dropdown`, etc. |
| Button styles, inputs, toggles | `web/static/css/controls.css` | `.btn`, `.btn-onoff`, `.btn-lock` |
| Slot row DOM creation | `web/static/js/components.js` | `createSlotRow()` |
| Section DOM creation | `web/static/js/components.js` | `createSection()` |
| On/Off toggle, Lock toggle | `web/static/js/handlers.js` | `wireSlotEvents()` |
| Randomize All, Reset, Copy | `web/static/js/handlers.js` | `wireGlobalEvents()` |
| Section Random/All On/All Off | `web/static/js/handlers.js` | `wireSectionEvents()` |
| Palette auto-apply on select | `web/static/js/handlers.js` | Inside `wireGlobalEvents()` palette listener |
| Save/Load config UI | `web/static/js/handlers.js` | `wireSaveLoadEvents()` |
| Prompt generation display | `web/static/js/prompt.js` | `generateAndDisplay()` |
| All API fetch calls | `web/static/js/api.js` | One function per endpoint |
| State shape, init, getters | `web/static/js/state.js` | `state` object, `initSlotState()` |
| Init flow, wiring order | `web/static/js/app.js` | `init()` — orchestrator |

## Data (JSON catalogs)

| What to change | File |
|---|---|
| Hair options | `hair/hair_catalog.json` |
| Eye options | `eyes/eye_catalog.json` |
| Body features | `body/body_features.json` |
| Expressions | `expressions/female_expressions.json` |
| Clothing items | `clothing/clothing_list.json` |
| Poses | `poses/poses.json` |
| Backgrounds | `backgrounds/backgrounds.json` |
| Color palettes + individual colors | `colors/color_palettes.json` |
| Saved character presets | `configs/*.json` |

## Entry Points

| Script | What it launches |
|---|---|
| `python run_Fastapi.py` | FastAPI + vanilla HTML/JS UI (new) |
| `python run_gradio.py` | Gradio UI (legacy fallback) |
