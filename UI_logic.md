# UI Logic Reference

Complete specification of the prompt generator UI. Use this to replicate the interface in any framework.

---

## 1. Slot System

A **slot** is one aspect of the character (e.g., hair style, upper body clothing). Each slot has:

| Property | Type | Default | Description |
|---|---|---|---|
| enabled | bool | true | Whether this slot is included in the prompt |
| locked | bool | false | If true, Randomize All / Section Random skip this slot |
| value_id | string? | null | Currently selected item ID (stable canonical value) |
| value | string? | null | Legacy compatibility field; display text may be provided by older saved configs |
| color | string? | null | Color token (canonical value from `individual_colors`) |
| weight | float | 1.0 | Prompt emphasis weight (range 0.1-2.0) |

### Localization Model

- Two independent language controllers exist:
  - **UI Language**: controls section labels, slot labels, dropdown option text, palette names, and all interface copy.
  - **Prompt Language**: controls generated prompt output text only.
- Catalog items now carry multilingual names in JSON via:
  - `name` (English canonical display)
  - `name_i18n.en`
  - `name_i18n.zh`
- Slot state stores IDs (`value_id`) so UI language can change without changing the selected value.

### All 26 Slots

**Appearance** (6 slots):
| Slot | has_color | Data source |
|---|---|---|
| hair_style | no | prompt data/hair/hair_catalog.json -> index_by_category.style |
| hair_length | no | prompt data/hair/hair_catalog.json -> index_by_category.length |
| hair_color | no | prompt data/hair/hair_catalog.json -> index_by_category.color |
| hair_texture | no | prompt data/hair/hair_catalog.json -> index_by_category.texture |
| eye_color | no | prompt data/eyes/eye_catalog.json -> index_by_category.color |
| eye_style | no | prompt data/eyes/eye_catalog.json -> index_by_category.style |

**Body / Expression / Pose** (8 slots):
| Slot | has_color | Data source |
|---|---|---|
| body_type | no | prompt data/body/body_features.json -> index_by_category.body_type |
| height | no | prompt data/body/body_features.json -> index_by_category.height |
| skin | no | prompt data/body/body_features.json -> index_by_category.skin |
| age_appearance | no | prompt data/body/body_features.json -> index_by_category.age_appearance |
| special_features | no | prompt data/body/body_features.json -> index_by_category.special_features |
| expression | no | prompt data/expressions/female_expressions.json -> items |
| pose | no | prompt data/poses/poses.json -> items |
| gesture (label: hand actions) | no | prompt data/poses/poses.json -> index_by_category.gesture |

**Clothing & Background** (12 slots):
| Slot | has_color | Data source |
|---|---|---|
| head | yes | prompt data/clothing/clothing_list.json -> index_by_body_part.head |
| neck | yes | prompt data/clothing/clothing_list.json -> index_by_body_part.neck |
| upper_body | yes | prompt data/clothing/clothing_list.json -> index_by_body_part.upper_body |
| waist | yes | prompt data/clothing/clothing_list.json -> index_by_body_part.waist |
| lower_body | yes | prompt data/clothing/clothing_list.json -> index_by_body_part.lower_body |
| full_body | yes | prompt data/clothing/clothing_list.json -> index_by_body_part.full_body (curated one-piece/suit entries only) |
| outerwear | yes | prompt data/clothing/clothing_list.json -> index_by_body_part.outerwear |
| hands | yes | prompt data/clothing/clothing_list.json -> index_by_body_part.hands |
| legs | yes | prompt data/clothing/clothing_list.json -> index_by_body_part.legs |
| feet | yes | prompt data/clothing/clothing_list.json -> index_by_body_part.feet |
| accessory | yes | prompt data/clothing/clothing_list.json -> index_by_body_part.accessory |
| background | no | prompt data/backgrounds/backgrounds.json -> items |

`upper_body` includes additional occupational/feminine top variants such as `nurse top`, `police top`, `office lady blouse`, `waitress top`, and `idol stage top`.

---

## 2. Section Layout

Slots are grouped into 3 visual sections. Each section has: Random, All On, All Off buttons.

| Section | Title | Slots | Layout |
|---|---|---|---|
| appearance | Appearance | hair_style through eye_style (6) | Single column |
| body | Body / Expression / Pose | body_type through gesture (8) | Single column |
| clothing | Clothing & Background | head through background (12) | Two sub-columns: left=[head, neck, upper_body, waist, lower_body, full_body], right=[outerwear, hands, legs, feet, accessory, background] |

The 3 sections are displayed in a horizontal flex row that wraps on smaller screens.
Section titles are localized from UI i18n keys (`section_appearance`, `section_body`, `section_clothing`).

### Full-Body Catalog Policy

- `full_body` is reserved for non-decomposable one-piece or suit-like outfits (for example: `eva suit`, `mecha pilot suit`, `power armor / exosuit`, `tactical bodysuit`).
- Decomposable garments (for example dresses, robes, kimono/yukata style entries) are intentionally excluded from `full_body`.
- Those decomposable outfits should be represented via `upper_body` + `lower_body` combinations.

---

## 3. Per-Slot UI Controls
Each slot row contains these controls in order:

```
[On/Off] [Lock] [Label] [Dropdown --------] [Random] [Color v] [Color Random] [Weight]
```

| Control | Behavior |
|---|---|
| **On/Off button** | Toggles `enabled`. Green="On", Red="Off". Disabled slots are dimmed and excluded from prompt. |
| **Lock button** | Toggles `locked`. Unlocked icon = open lock, Locked icon = closed lock. Locked slots are skipped by Randomize All and Section Random. |
| **Label** | Localized slot label from UI i18n (`slot_label_*`). `gesture` is represented as localized `hand actions`. |
| **Dropdown** | Shows localized option names from `name_i18n` in UI language; selected value stored as `value_id`. |
| **Random button** | Randomize just this slot's value (and color if palette coloring is enabled). |
| **Color dropdown** | Only visible for `has_color` slots. Select a color or "(No Color)". Stored value is canonical color token; label is localized from `individual_colors_i18n`. |
| **Color Random button** | Only visible for `has_color` slots. Randomize just this slot's color from the active palette (when palette coloring is enabled). |
| **Weight input** | Number input 0.1-2.0 step 0.1. Default 1.0. Affects prompt weight syntax. |

---

## 4. Global Controls

| Control | Behavior |
|---|---|
| **Generate Prompt** | Build prompt string from all enabled slots and display it. |
| **Live Prompt Sync** | Prompt auto-refreshes on slot on/off, dropdown selection, color change, weight change, and per-slot randomize. |
| **Randomize All** | Randomize every non-locked slot, then auto-generate the prompt. |
| **Copy** | Copy the prompt text to clipboard. |
| **Reset** | Clear all slot values, colors, weights to defaults. Clear prompt output. |
| **Always Include Prefix** | Free-text optional prefix prepended to generated prompt. Default is empty. |
| **Prefix Preset** | Selectable preset that fills the previous SD quality string: `(masterpiece),(best quality),(ultra-detailed),(best illustration),(absurdres),(very aesthetic),(newest),detailed eyes, detailed face`. |
| **Colorize Prompt Output** | Toggle (default: on). Applies colored rendering directly in the single prompt output field. When off, the same field shows plain text. |
| **UI Language selector** | Controls all interface language (labels, slot bars, dropdown text, section titles, palette labels). |
| **Prompt Language selector** | Controls generated prompt output language only (can differ from UI Language). |

---

## 5. Settings

| Setting | Options | Behavior |
|---|---|---|
| **Full-body specific outfit** | Checkbox (default: off) | One-shot helper: when turned on, it toggles `upper_body`, `waist`, `lower_body`, `hands`, `legs` to Off once. When turned off, slots that were auto-disabled by that toggle cycle are turned back On. User can still manually change any slot at any time. Also during randomization: if `full_body` slot has a value, `upper_body` and `lower_body` values are cleared. |
| **Upper-body mode** | Checkbox (default: off) | One-shot helper: when turned on, it toggles `waist`, `lower_body`, `full_body`, `legs`, and `feet` to Off once. When turned off, slots that were auto-disabled by that toggle cycle are turned back On. User can still manually change any slot at any time. |
| **Use Palette Colors** | Checkbox (default: on) | When on, randomization assigns colors from the active palette. When off, randomization does not auto-assign colors. |
| **Palette selector** | Dropdown of palettes from color_palettes.json | Selects the active palette. Display text is localized by UI language. If **Use Palette Colors** is on, changing palette applies it to current colored slots and regenerates prompt immediately. |

---

## 6. Event Behaviors

### Randomize All
1. For each slot: skip if `locked`
2. Sample a random item from the slot's options
3. Save sampled item as `value_id` (plus optional compatibility `value` text)
4. If `full_body_mode` is on and `full_body` got a value, clear `upper_body` and `lower_body`
5. If **Use Palette Colors** is on, sample color from active palette for each `has_color` slot
6. If **Use Palette Colors** is off, do not auto-assign colors
7. Update all dropdowns and color selectors
8. Auto-generate prompt

### Section Random
Same as Randomize All but only for slots within that section.

### Palette Auto-Apply
1. User selects a palette
2. If **Use Palette Colors** is on
3. For each slot where `has_color == true` AND the slot has a current value:
   - Sample a random color from the selected palette
   - Update the color dropdown
4. Regenerate prompt with new colors

### Full-Body Specific Outfit One-Shot Disable
- Trigger: when user turns on **Full-body specific outfit**
- Action performed once at toggle time:
  - Set `upper_body`, `waist`, `lower_body`, `hands`, `legs` to `enabled = false`
- Trigger: when user turns off **Full-body specific outfit**
- Restore action:
  - Re-enable only the slots that were auto-disabled by the most recent enable action
- No persistent lock:
  - Those slots can still be toggled on/off manually at any time
  - Prompt generation and randomization follow the current on/off state only

### Full-Body Randomization Override
- Only during randomization (not manual selection)
- If `full_body` slot has a value AND `full_body_mode` is on:
  - `upper_body` value -> null
  - `lower_body` value -> null
- User can still manually set upper/lower body after randomization

### Upper-Body One-Shot Disable
- Trigger: when user turns on **Upper-body mode**
- Action performed once at toggle time:
  - Set `waist`, `lower_body`, `full_body`, `legs`, `feet` to `enabled = false`
- Trigger: when user turns off **Upper-body mode**
- Restore action:
  - Re-enable only the slots that were auto-disabled by the most recent Upper-body mode enable action
- No persistent lock:
  - Those slots can still be toggled on/off manually at any time
  - Prompt generation and randomization follow the current on/off state only

### Lower-Body Leg Coverage Rule
- `lower_body` items include `covers_legs` metadata in `prompt data/clothing/clothing_list.json`
- If selected lower-body item has `covers_legs == true`:
  - `legs` slot is toggled Off once
  - user can manually toggle `legs` back On immediately (no lock)
- Prompt generation follows the current `legs.enabled` state only.

### Pose Hand-Usage Rule
- `prompt data/poses/poses.json` items include `uses_hands` metadata.
- If selected `pose` item has `uses_hands == true`:
  - `gesture` slot (shown as `hand actions`) is toggled Off once
  - user can manually toggle `gesture` back On immediately (no lock)
- Prompt generation follows the current `gesture.enabled` state only.

---

## 7. Prompt Building

### Format
```
1girl, [slot values in order], ...
```

### Slot Order in Prompt
```
hair_color, hair_length, hair_style, hair_texture,
eye_color, eye_style,
body_type, height, skin, age_appearance, special_features,
expression,
full_body, head, neck, upper_body, waist, lower_body,
outerwear, hands, legs, feet, accessory,
view_angle, pose, gesture,
background
```

### Rules
- Always starts with `1girl`
- Skip slots where `enabled == false` or `value_id == null` (or unresolved legacy value)
- If full-body mode on and `full_body` has a value, skip `upper_body` and `lower_body`
- `full_body` values are intentionally limited to one-piece/suit-style options; decomposable outfits should come from `upper_body` + `lower_body`
- Slot text is localized to **Prompt Language** from `name_i18n`
- Color prefix text is localized to **Prompt Language** from `individual_colors_i18n`
- Color prefix format: if color is set -> `"{color} {value}"` (e.g., "blue skirt")
- Weight syntax: if weight != 1.0 -> `"({part}:{weight})"` (e.g., "(blue skirt:1.3)")
- Join all parts with `, `

### Example Output
```
1girl, black hair, long hair, ponytail, blue eyes, slim, (white tactical bodysuit:1.3), white gloves, standing, park background
```

---

## 8. Save / Load System
### Save
- User enters a config name
- All slot states (enabled, locked, value_id, color, weight) are serialized to JSON
- Saved to `prompt data/configs/{name}.json`

### Load
- User selects from saved configs dropdown
- All slot states are restored from the JSON file
- UI updates (dropdowns, colors, weights, on/off, lock states)
- Prompt regenerates

### Config JSON Structure
```json
{
  "name": "my_character",
  "created_at": "2026-02-11T12:00:00",
  "slots": {
    "hair_style": {
      "enabled": true,
      "locked": false,
      "value_id": "ponytail",
      "color": null,
      "weight": 1.0
    },
    ...
  }
}
```

---

## 9. API Contract

### GET /api/slots
Response: `{ slots: { [name]: { category, has_color, options: [{ id, name, name_i18n, localized_name }] } }, sections: { [key]: { label, label_key, icon, slots, columns? } }, lower_body_covers_legs_by_id: { [lower_body_id]: boolean }, pose_uses_hands_by_id: { [pose_id]: boolean } }`

### GET /api/palettes
Response: `{ palettes: [{ id, name, name_i18n, description_i18n, colors: string[] }], individual_colors: string[], individual_colors_i18n: { [color_token]: { en, zh } } }`

### POST /api/randomize
Body: `{ slot_names, locked, palette_enabled, palette_id, full_body_mode, upper_body_mode, current_values }`
Note: `upper_body_mode` is accepted for compatibility but not used as a backend hard-disable.
Response: `{ results: { [name]: { value_id, value, color } } }`

### POST /api/randomize-all
Body: `{ locked, palette_enabled, palette_id, full_body_mode, upper_body_mode }`
Note: `upper_body_mode` is accepted for compatibility but not used as a backend hard-disable.
Response: `{ results: { [name]: { value_id, value, color } } }`

### POST /api/generate-prompt
Body: `{ slots: { [name]: { enabled, value_id, color, weight } }, full_body_mode, upper_body_mode, output_language }`
Note: `upper_body_mode` is accepted for compatibility but prompt output is driven by slot `enabled` state.
Response: `{ prompt: string }`

### POST /api/apply-palette
Body: `{ palette_id, slots: { [name]: { enabled, value_id, color, weight } }, full_body_mode, upper_body_mode, output_language }`
Note: `upper_body_mode` is accepted for compatibility but not used as a backend hard-disable.
Response: `{ colors: { [name]: string }, prompt: string }`

### GET /api/configs
Response: `{ configs: string[] }`

### GET /api/configs/{name}
Response: `{ name, data: { slots: { ... } } }`

### POST /api/configs/{name}
Body: `{ name, data: { slots: { ... } } }`
Response: `{ status: "ok", name }`

