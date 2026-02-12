# Body Features JSON Structure Guide

This document explains the structure of the body features JSON file and provides instructions for an AI agent to populate it.

- **Catalog file:** `body_features.json`
- **Purpose:** Provide a structured catalog of body characteristics for anime character generation.

---

## 1) Top-level Schema

```text
['schema_version', 'title', 'generated_utc', 'items', 'index_by_category', 'categories', 'meta']
```

---

## 2) Categories

| Category | Description | Example Values |
|----------|-------------|----------------|
| `body_type` | Overall build | slim, athletic, curvy, petite, muscular |
| `height` | Height descriptors | tall, short, average height |
| `skin` | Skin characteristics | pale skin, tan skin, dark skin, fair skin |
| `age_appearance` | Apparent age | young adult, mature, teenage appearance |
| `special_features` | Fantasy/unique features | elf ears, wings, tail, horns, fangs |

---

## 3) Item Structure

```json
{
  "id": "elf_ears",
  "name": "elf ears",
  "category": "special_features",
  "aliases": ["pointed ears", "elven ears"]
}
```

### Field Definitions

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique slug identifier |
| `name` | string | The exact term to use in SD prompts |
| `category` | string | One of the 5 categories |
| `aliases` | array | Alternative names |

---

## 4) Instructions for AI Agent

**Task:** Populate the `body_features.json` with anime-appropriate body descriptors.

### Requirements:

1. **Body Types (10-15 items):**
   - slim, slender, petite, athletic, fit, toned
   - curvy, voluptuous, plump
   - muscular, well-built
   - delicate, graceful

2. **Height (5-8 items):**
   - tall, short, average height
   - very tall, very short
   - towering, tiny

3. **Skin (15-25 items):**
   
   **Tones:**
   - pale skin, fair skin, light skin, white skin
   - tan skin, tanned, sun-kissed skin
   - dark skin, brown skin, ebony skin
   - olive skin
   
   **Characteristics:**
   - freckles, moles, beauty mark
   - smooth skin, flawless skin
   - blushing, flushed cheeks

4. **Age Appearance (5-8 items):**
   - young, youthful, mature
   - adult, young adult
   - Note: Keep to appropriate anime age representations

5. **Special Features (20-35 items):**
   
   **Ears:**
   - elf ears, pointed ears, animal ears, cat ears, fox ears, rabbit ears, dog ears
   
   **Tails:**
   - tail, cat tail, fox tail, demon tail, fluffy tail
   
   **Wings:**
   - wings, angel wings, demon wings, fairy wings, bat wings, feathered wings
   
   **Horns:**
   - horns, demon horns, small horns, curved horns, oni horns
   
   **Other:**
   - fangs, sharp teeth
   - halo, floating halo
   - third eye
   - tattoo, tribal tattoo, arm tattoo
   - scar, facial scar
   - mole, beauty mark
   - heterochromia (can also be in eyes)

### Format Rules:
- Use lowercase for `id` and `name`
- Use underscores in `id`, spaces in `name`
- Focus on SFW descriptors
- Ensure all item IDs are added to `index_by_category`

---

## 5) Validation Checklist

- [ ] All items have unique `id` values
- [ ] All items have valid `category` values
- [ ] All item IDs appear in `index_by_category`
- [ ] `generated_utc` is set
- [ ] Content is appropriate and SFW
