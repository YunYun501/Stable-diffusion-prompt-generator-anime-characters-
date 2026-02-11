# UI Logic Reference

Complete specification of the prompt generator UI. Use this to replicate the interface in any framework.

---

## 1. Slot System

A **slot** is one aspect of the character (e.g., hair style, upper body clothing). Each slot has:

| Property | Type | Default | Description |
|---|---|---|---|
| enabled | bool | true | Whether this slot is included in the prompt |
| locked | bool | false | If true, Randomize All / Section Random skip this slot |
| value | string? | null | Currently selected item name (or null for none) |
| color | string? | null | Color modifier prefix (only for has_color slots) |
| weight | float | 1.0 | Prompt emphasis weight (range 0.1–2.0) |

### All 26 Slots

**Appearance** (6 slots):
| Slot | has_color | Data source |
|---|---|---|
| hair_style | no | hair/hair_catalog.json → index_by_category.style |
| hair_length | no | hair/hair_catalog.json → index_by_category.length |
| hair_color | no | hair/hair_catalog.json → index_by_category.color |
| hair_texture | no | hair/hair_catalog.json → index_by_category.texture |
| eye_color | no | eyes/eye_catalog.json → index_by_category.color |
| eye_style | no | eyes/eye_catalog.json → index_by_category.style |

**Body / Expression / Pose** (8 slots):
| Slot | has_color | Data source |
|---|---|---|
| body_type | no | body/body_features.json → index_by_category.body_type |
| height | no | body/body_features.json → index_by_category.height |
| skin | no | body/body_features.json → index_by_category.skin |
| age_appearance | no | body/body_features.json → index_by_category.age_appearance |
| special_features | no | body/body_features.json → index_by_category.special_features |
| expression | no | expressions/female_expressions.json → items |
| pose | no | poses/poses.json → items |
| gesture | no | poses/poses.json → index_by_category.gesture |

**Clothing & Background** (12 slots):
| Slot | has_color | Data source |
|---|---|---|
| head | yes | clothing/clothing_list.json → index_by_body_part.head |
| neck | yes | clothing/clothing_list.json → index_by_body_part.neck |
| upper_body | yes | clothing/clothing_list.json → index_by_body_part.upper_body |
| waist | yes | clothing/clothing_list.json → index_by_body_part.waist |
| lower_body | yes | clothing/clothing_list.json → index_by_body_part.lower_body |
| full_body | yes | clothing/clothing_list.json → index_by_body_part.full_body |
| outerwear | yes | clothing/clothing_list.json → index_by_body_part.outerwear |
| hands | yes | clothing/clothing_list.json → index_by_body_part.hands |
| legs | yes | clothing/clothing_list.json → index_by_body_part.legs |
| feet | yes | clothing/clothing_list.json → index_by_body_part.feet |
| accessory | yes | clothing/clothing_list.json → index_by_body_part.accessory |
| background | no | backgrounds/backgrounds.json → items |

---

## 2. Section Layout

Slots are grouped into 3 visual sections. Each section has: Random, All On, All Off buttons.

| Section | Title | Slots | Layout |
|---|---|---|---|
| appearance | Appearance | hair_style through eye_style (6) | Single column |
| body | Body / Expression / Pose | body_type through gesture (8) | Single column |
| clothing | Clothing & Background | head through background (12) | Two sub-columns: left=[head, neck, upper_body, waist, lower_body, full_body], right=[outerwear, hands, legs, feet, accessory, background] |

The 3 sections are displayed in a horizontal flex row that wraps on smaller screens.

---

## 3. Per-Slot UI Controls

Each slot row contains these controls in order:

```
[On/Off] [Lock] [Label] [Dropdown --------] [Random] [Color ▼] [Color Random] [Weight]
```

| Control | Behavior |
|---|---|
| **On/Off button** | Toggles `enabled`. Green="On", Red="Off". Disabled slots are dimmed and excluded from prompt. |
| **Lock button** | Toggles `locked`. Unlocked=🔓, Locked=🔒. Locked slots are skipped by Randomize All and Section Random. |
| **Label** | Display name (slot_name with underscores replaced by spaces, title-cased). |
| **Dropdown** | Select from slot options or "(None)". Options come from the JSON data catalogs. |
| **Random button** 🎲 | Randomize just this slot's value (and color if color mode is active). |
| **Color dropdown** | Only visible for `has_color` slots. Select a color or "(No Color)". Colors from `color_palettes.json → individual_colors`. |
| **Color Random button** 🎨 | Only visible for `has_color` slots. Randomize just this slot's color (from palette or random). |
| **Weight input** | Number input 0.1–2.0 step 0.1. Default 1.0. Affects prompt weight syntax. |

---

## 4. Global Controls

| Control | Behavior |
|---|---|
| **Generate Prompt** | Build prompt string from all enabled slots and display it. |
| **Randomize All** | Randomize every non-locked slot, then auto-generate the prompt. |
| **Copy** | Copy the prompt text to clipboard. |
| **Reset** | Clear all slot values, colors, weights to defaults. Clear prompt output. |

---

## 5. Settings

| Setting | Options | Behavior |
|---|---|---|
| **Full-body mode** | Checkbox (default: on) | When on and `full_body` slot has a value, `upper_body` and `lower_body` are cleared during randomization and excluded from prompt. |
| **Color mode** | None / Palette / Random | Controls how colors are assigned during randomization. None=no colors. Palette=from selected palette. Random=from individual_colors list. |
| **Palette selector** | Dropdown of palettes from color_palettes.json | On change: auto-switches to Palette mode, applies palette colors to all `has_color` slots that have a current value, and regenerates prompt immediately. |

---

## 6. Event Behaviors

### Randomize All
1. For each slot: skip if `locked`
2. Sample a random item from the slot's options
3. If `full_body_mode` is on and `full_body` got a value, clear `upper_body` and `lower_body`
4. If color mode is "palette", sample color from active palette for each `has_color` slot
5. If color mode is "random", sample from individual_colors
6. Update all dropdowns and color selectors
7. Auto-generate prompt

### Section Random
Same as Randomize All but only for slots within that section.

### Palette Auto-Apply
1. User selects a palette
2. Color mode switches to "palette"
3. For each slot where `has_color == true` AND the slot has a current value:
   - Sample a random color from the selected palette
   - Update the color dropdown
4. Regenerate prompt with new colors

### Full-Body Override
- Only during randomization (not manual selection)
- If `full_body` slot has a value AND `full_body_mode` is on:
  - `upper_body` value → null
  - `lower_body` value → null
- User can still manually set upper/lower body after randomization

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
pose, gesture,
background
```

### Rules
- Always starts with `1girl`
- Skip slots where `enabled == false` or `value == null`
- If full-body mode on and `full_body` has a value, skip `upper_body` and `lower_body`
- Color prefix: if color is set → `"{color} {value}"` (e.g., "blue skirt")
- Weight syntax: if weight != 1.0 → `"({part}:{weight})"` (e.g., "(blue skirt:1.3)")
- Join all parts with `, `

### Example Output
```
1girl, black hair, long hair, ponytail, blue eyes, slim, (red dress:1.3), white gloves, standing, park background
```

---

## 8. Save / Load System

### Save
- User enters a config name
- All slot states (enabled, locked, value, color, weight) are serialized to JSON
- Saved to `configs/{name}.json`

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
      "value": "ponytail",
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
Response: `{ slots: { [name]: { category, has_color, options: string[] } }, sections: { [key]: { label, icon, slots, columns? } } }`

### GET /api/palettes
Response: `{ palettes: [{ id, name, colors: string[] }], individual_colors: string[] }`

### POST /api/randomize
Body: `{ slot_names, locked, color_mode, palette_id, full_body_mode, current_values }`
Response: `{ results: { [name]: { value, color } } }`

### POST /api/randomize-all
Body: `{ locked, color_mode, palette_id, full_body_mode }`
Response: `{ results: { [name]: { value, color } } }`

### POST /api/generate-prompt
Body: `{ slots: { [name]: { enabled, value, color, weight } }, full_body_mode }`
Response: `{ prompt: string }`

### POST /api/apply-palette
Body: `{ palette_id, slots: { [name]: { enabled, value, color, weight } }, full_body_mode }`
Response: `{ colors: { [name]: string }, prompt: string }`

### GET /api/configs
Response: `{ configs: string[] }`

### GET /api/configs/{name}
Response: `{ name, data: { slots: { ... } } }`

### POST /api/configs/{name}
Body: `{ name, data: { slots: { ... } } }`
Response: `{ status: "ok", name }`
