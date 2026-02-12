# Hair Catalog JSON Structure Guide

This document explains the structure of the hair catalog JSON file and provides instructions for an AI agent to populate it.

- **Catalog file:** `hair_catalog.json`
- **Purpose:** Provide a structured catalog of anime-style hair attributes for random character generation.

---

## 1) Top-level Schema

```text
['schema_version', 'title', 'generated_utc', 'items', 'index_by_category', 'categories', 'meta']
```

---

## 2) Categories

The hair catalog is organized into **4 categories**:

| Category | Description | Example Values |
|----------|-------------|----------------|
| `style` | Hair arrangement/cut | ponytail, twintails, bob, hime cut, braid, bun, side ponytail, drill hair, ahoge |
| `length` | Hair length | short hair, medium hair, long hair, very long hair |
| `color` | Hair color (natural + anime) | blonde, black, brown, red, pink, blue, silver, white, green, purple, gradient hair, multicolored hair |
| `texture` | Hair texture/quality | straight hair, wavy hair, curly hair, messy hair, fluffy hair |

---

## 3) Item Structure

Each item in the `items` array should have:

```json
{
  "id": "twintails",
  "name": "twintails",
  "category": "style",
  "aliases": ["twin tails", "pigtails"]
}
```

### Field Definitions

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique slug identifier (lowercase, underscores) |
| `name` | string | The exact term to use in SD prompts |
| `category` | string | One of: `style`, `length`, `color`, `texture` |
| `aliases` | array | Alternative names (optional, for matching) |

---

## 4) Index Structure

The `index_by_category` object maps category → list of item IDs:

```json
{
  "index_by_category": {
    "style": ["ponytail", "twintails", "bob", "braid", ...],
    "length": ["short_hair", "medium_hair", "long_hair", ...],
    "color": ["blonde", "black", "pink", "blue", ...],
    "texture": ["straight_hair", "wavy_hair", "curly_hair", ...]
  }
}
```

---

## 5) Instructions for AI Agent

**Task:** Populate the `hair_catalog.json` with comprehensive anime hair options.

### Requirements:

1. **Styles (aim for 25-40 items):**
   - Common anime styles: ponytail, twintails, braid, bun, bob, hime cut, side ponytail, drill hair
   - Include modifiers: low ponytail, high ponytail, single braid, twin braids, side braid
   - Anime-specific: ahoge, antenna hair, hair over one eye, hair between eyes
   - Elaborate styles: odango, chignon, french braid, fishtail braid

2. **Lengths (4-6 items):**
   - short hair, medium hair, long hair, very long hair
   - Optional: shoulder-length hair, waist-length hair

3. **Colors (30-50 items):**
   - Natural: blonde, brunette, black hair, brown hair, red hair, auburn, ginger, strawberry blonde, platinum blonde, grey hair, white hair
   - Anime colors: pink hair, blue hair, purple hair, green hair, silver hair, light blue hair, lavender hair, mint green hair, orange hair, teal hair
   - Special: gradient hair, multicolored hair, two-tone hair, streaked hair, ombre hair, rainbow hair
   - Shades: light brown, dark brown, light blonde, ash blonde, golden blonde

4. **Textures (8-15 items):**
   - straight hair, wavy hair, curly hair, messy hair, fluffy hair, spiky hair
   - Anime-specific: shiny hair, silky hair, windswept hair, wet hair

### Format Rules:
- Use lowercase for `id` and `name` (SD prompt style)
- Use underscores in `id`, spaces in `name`
- Ensure all item IDs are added to `index_by_category`
- Set `generated_utc` to the current timestamp

### Example Complete Item:

```json
{
  "id": "pink_twintails",
  "name": "pink twintails",
  "category": "style",
  "aliases": ["pink twin tails"]
}
```

Note: For this catalog, keep style and color separate. They will be combined by the generator (e.g., style="twintails" + color="pink" → "pink twintails").

---

## 6) Validation Checklist

Before finalizing, verify:
- [ ] All items have unique `id` values
- [ ] All items have `category` set to one of the 4 valid categories
- [ ] All item IDs appear in the corresponding `index_by_category` array
- [ ] `generated_utc` is set
- [ ] No duplicate entries
