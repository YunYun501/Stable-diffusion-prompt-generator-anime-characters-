# Eye Catalog JSON Structure Guide

This document explains the structure of the eye catalog JSON file and provides instructions for an AI agent to populate it.

- **Catalog file:** `eye_catalog.json`
- **Purpose:** Provide a structured catalog of anime-style eye colors and characteristics for random character generation.

---

## 1) Top-level Schema

```text
['schema_version', 'title', 'generated_utc', 'items', 'index_by_category', 'categories', 'meta']
```

---

## 2) Categories

The eye catalog is organized into **2 categories**:

| Category | Description | Example Values |
|----------|-------------|----------------|
| `color` | Eye color | blue eyes, green eyes, red eyes, golden eyes, heterochromia |
| `style` | Special eye characteristics | sparkling eyes, detailed eyes, empty eyes, glowing eyes |

---

## 3) Item Structure

Each item in the `items` array should have:

```json
{
  "id": "blue_eyes",
  "name": "blue eyes",
  "category": "color",
  "aliases": []
}
```

### Field Definitions

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique slug identifier (lowercase, underscores) |
| `name` | string | The exact term to use in SD prompts |
| `category` | string | One of: `color`, `style` |
| `aliases` | array | Alternative names (optional) |

---

## 4) Index Structure

```json
{
  "index_by_category": {
    "color": ["blue_eyes", "green_eyes", "red_eyes", ...],
    "style": ["sparkling_eyes", "detailed_eyes", ...]
  }
}
```

---

## 5) Instructions for AI Agent

**Task:** Populate the `eye_catalog.json` with comprehensive anime eye options.

### Requirements:

1. **Colors (30-50 items):**
   
   **Natural colors:**
   - blue eyes, green eyes, brown eyes, hazel eyes, grey eyes, black eyes
   - Light/dark variants: light blue eyes, dark blue eyes, light green eyes, dark brown eyes
   
   **Anime colors:**
   - red eyes, pink eyes, purple eyes, violet eyes, golden eyes, yellow eyes, orange eyes
   - silver eyes, white eyes, amber eyes, crimson eyes, scarlet eyes
   - aqua eyes, teal eyes, turquoise eyes, cyan eyes
   - lavender eyes, magenta eyes, rose eyes
   
   **Special:**
   - heterochromia (different colored eyes)
   - gradient eyes, multicolored eyes
   - red and blue eyes (specific heterochromia)
   - one blue eye one red eye

2. **Styles (15-25 items):**
   
   **Positive/beautiful:**
   - sparkling eyes, shiny eyes, detailed eyes, beautiful eyes
   - bright eyes, clear eyes, expressive eyes, gentle eyes
   
   **Anime-specific:**
   - tareme (drooping eyes - gentle look)
   - tsurime (upturned eyes - sharp look)
   - jitome (half-closed eyes)
   - sanpaku (whites visible below iris)
   
   **Special effects:**
   - glowing eyes, empty eyes, spiral eyes, heart-shaped pupils
   - star-shaped pupils, slit pupils, dilated pupils
   - symbol-shaped eyes, x-shaped eyes
   
   **Descriptive:**
   - half-closed eyes, closed eyes, one eye closed, winking
   - narrowed eyes, wide eyes

### Format Rules:
- Use lowercase for `id` and `name`
- Include "eyes" in the name (SD prompt convention)
- Use underscores in `id`, spaces in `name`
- Ensure all item IDs are added to `index_by_category`

### Example Items:

```json
{
  "id": "heterochromia",
  "name": "heterochromia",
  "category": "color",
  "aliases": ["odd eyes", "different colored eyes"]
}
```

```json
{
  "id": "sparkling_eyes",
  "name": "sparkling eyes",
  "category": "style",
  "aliases": ["shining eyes", "bright eyes"]
}
```

---

## 6) Validation Checklist

Before finalizing, verify:
- [ ] All items have unique `id` values
- [ ] All items have `category` set to `color` or `style`
- [ ] All item IDs appear in the corresponding `index_by_category` array
- [ ] `generated_utc` is set
- [ ] No duplicate entries
- [ ] Eye color items include "eyes" in the name where appropriate
