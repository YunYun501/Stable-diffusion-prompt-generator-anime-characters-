# Clothing JSON Structure Guide

This document explains the structure of the clothing catalog JSON file:

- **Catalog file used by app:** `prompt data/clothing/clothing_list.json`
- **Purpose:** Provide an AI agent with a predictable schema so it can randomly sample clothing items by *body-part slot*.

Generated: 2026-02-10T23:49:08Z

---

## 1) Top-level schema

The JSON object contains these top-level keys (current file):

```text
['schema_version', 'title', 'generated_utc', 'source_files', 'body_part_categories', 'items', 'index_by_body_part']
```

The schema is designed around two core sections:

1. **`items`**: the master list of clothing entries (deduplicated)
2. **`index_by_body_part`**: a fast lookup map from body-part slot -> list of item IDs

Some files may also include optional metadata (e.g., `meta`).

---

## 2) `items` (master list)

- Type: **array of objects**
- Count: **324** items in the current file

Each item represents a *single wearable component* (e.g., "sailor uniform top" and "sailor uniform skirt" are separate items).

### 2.1 Item fields

Common fields present across the dataset:

```text
['aliases', 'alt_body_parts', 'body_part', 'covers_legs', 'id', 'name']
```

### 2.2 Field definitions

#### `id` (string)
A stable identifier (slug). Use this for indexing and random sampling.

Example: `sailor_uniform_top`

#### `name` (string)
Human-readable name for display.

Example: `Sailor uniform top`

#### `body_part` (string enum)
The primary *slot* this item occupies.

Allowed values in the current file:

```text
['accessory', 'feet', 'full_body', 'hands', 'head', 'legs', 'lower_body', 'neck', 'outerwear', 'upper_body', 'waist']
```

Interpretation (recommended):
- `head`: hats, headbands, hair ornaments, headdresses
- `neck`: scarves, chokers, neckties, collars
- `upper_body`: tops, blouses, shirts, bras, corset tops
- `waist`: belts, obi, waist sashes, harness belts
- `lower_body`: skirts, shorts, pants
- `full_body`: dresses, jumpsuits, bodysuits, onesies
- `outerwear`: coats, cloaks, capes, jackets, cardigans
- `hands`: gloves, arm warmers
- `legs`: stockings, tights, leg warmers
- `feet`: shoes, boots, sandals
- `accessory`: non-slot accessories that don't neatly map elsewhere (e.g., bags, pouches).

#### `aliases` (array of strings, optional)
Synonyms / alternative names an agent may match on.

Example: `["seifuku top", "sailor blouse"]`

#### `covers_legs` (boolean, optional; lower_body only)
Whether this lower-body item already covers the leg area enough that `legs`
slot items (e.g., tights/stockings) should be force-disabled.

Guideline:
- `true` for long pants / hakama-style items
- `false` for skirts, shorts, bloomers, bikini bottoms

> Note: You previously requested removing `sources`. This catalog contains **no `sources` field**.

### 2.3 Example item

```json
{
  "id": "barrette",
  "name": "barrette",
  "body_part": "head",
  "aliases": []
}
```

Lower-body example:

```json
{
  "id": "jeans",
  "name": "jeans",
  "body_part": "lower_body",
  "aliases": [],
  "covers_legs": true
}
```

---

## 3) `index_by_body_part` (fast lookup)

- Type: **object/dictionary**
- Keys: body-part slots (strings)
- Values: arrays of **item IDs**

Example:

```json
{
  "upper_body": ["t_shirt", "blouse", "sailor_uniform_top"],
  "lower_body": ["skirt", "shorts", "sailor_uniform_skirt"]
}
```

This is the recommended structure for an agent because it avoids scanning the full list when sampling by slot.

---

## 4) Recommended agent usage patterns

### 4.1 Load and sample by slot

Python-like pseudocode:

```python
import json, random

with open("prompt data/clothing/clothing_list.json", "r", encoding="utf-8") as f:
    catalog = json.load(f)

items = catalog["items"]
index = catalog["index_by_body_part"]

# Build id -> item map for O(1) access
by_id = {it["id"]: it for it in items}

def sample_slot(slot: str):
    pool = index.get(slot, [])
    if not pool:
        return None
    return by_id[random.choice(pool)]

upper = sample_slot("upper_body")
lower = sample_slot("lower_body")
feet  = sample_slot("feet")
```

### 4.2 Construct an outfit (simple)

Minimal "outfit":
- Required: `upper_body`, `lower_body`, `feet`
- Optional: `outerwear`, `head`, `neck`, `hands`, `legs`, `waist`, `accessory`

### 4.3 Avoid incompatible overlaps (optional logic)
If you sample a `full_body` item (dress/jumpsuit), you may want to:
- **skip** `upper_body` and `lower_body`, or
- allow `outerwear`/`legs`/`feet` to stack on top.

---

## 5) Extension points (safe to add later)

If you want more control, you can add optional fields per item without breaking existing agents:
- `style_tags`: e.g., `["lolita", "streetwear", "wafuku"]`
- `era`: e.g., `["modern", "historical", "fantasy"]`
- `layer`: e.g., `["under", "base", "over"]`
- `rarity_weight`: numeric weight for sampling bias

Agents should ignore unknown keys for forward compatibility.

