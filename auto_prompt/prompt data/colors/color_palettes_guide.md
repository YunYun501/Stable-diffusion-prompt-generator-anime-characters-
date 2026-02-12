# Color Palettes JSON Structure Guide

This document explains the structure of the color palettes JSON file and provides instructions for an AI agent to populate it.

- **Catalog file:** `color_palettes.json`
- **Purpose:** Provide art-proven color combinations that work well together for anime character generation.

---

## 1) Top-level Schema

```text
['schema_version', 'title', 'generated_utc', 'palettes', 'individual_colors', 'index_by_palette_type', 'palette_types', 'meta']
```

---

## 2) Palette Types

| Type | Description | Example Palettes |
|------|-------------|------------------|
| `harmony` | Color theory based | Complementary Blue-Orange, Triadic Primary |
| `mood` | Emotional atmosphere | Warm Sunset, Cool Ocean, Dark Mysterious |
| `theme` | Visual aesthetic | Gothic, Pastel Dream, Cyberpunk Neon |
| `anime_classic` | Common anime combos | Sailor Uniform, Maid Classic, Magical Pink |
| `seasonal` | Season/holiday | Spring Sakura, Summer Beach, Winter Snow |

---

## 3) Palette Structure

Each palette in the `palettes` array should have:

```json
{
  "id": "sailor_navy_classic",
  "name": "Classic Sailor Navy",
  "type": "anime_classic",
  "colors": ["navy blue", "white", "red", "gold"],
  "description": "Traditional Japanese sailor uniform colors",
  "suggested_assignments": {
    "primary": "navy blue",
    "secondary": "white",
    "accent": "red",
    "detail": "gold"
  }
}
```

### Field Definitions

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique slug identifier |
| `name` | string | Human-readable palette name |
| `type` | string | One of the 5 palette types |
| `colors` | array | List of 3-6 color names (in dominance order) |
| `description` | string | Brief description of the palette |
| `suggested_assignments` | object | Optional hints for how to assign colors |

### Color Assignment Roles

- `primary` - Main/dominant color (large areas like dress, top)
- `secondary` - Supporting color (skirt, pants, large accessories)
- `accent` - Pop of contrast (ribbons, ties, small details)
- `detail` - Minor touches (buttons, trim, small accents)

---

## 4) Individual Colors List

The `individual_colors` array provides all available color options for "full random" mode:

```json
{
  "individual_colors": [
    "white", "black", "grey", "silver",
    "red", "crimson", "scarlet", "maroon", "burgundy", "wine red",
    "pink", "light pink", "hot pink", "magenta", "rose",
    "orange", "coral", "peach",
    "yellow", "gold", "cream", "ivory", "beige",
    "green", "lime", "mint", "forest green", "olive", "teal",
    "blue", "navy blue", "light blue", "sky blue", "royal blue", "cyan", "aqua",
    "purple", "violet", "lavender", "plum", "indigo",
    "brown", "tan", "chocolate", "coffee"
  ]
}
```

---

## 5) Instructions for AI Agent

**Task:** Populate the `color_palettes.json` with 50-80 art-proven color palettes.

### Requirements by Type:

#### 1. Harmony Palettes (10-15 palettes)

Based on color wheel relationships:

**Complementary (opposites):**
- Blue & Orange Harmony: `["blue", "orange", "white", "grey"]`
- Red & Green Classic: `["red", "green", "white", "gold"]`
- Purple & Yellow: `["purple", "yellow", "white", "grey"]`

**Analogous (neighbors):**
- Ocean Blues: `["navy blue", "blue", "teal", "cyan", "white"]`
- Sunset Warm: `["red", "orange", "yellow", "gold"]`
- Forest Greens: `["forest green", "green", "lime", "mint"]`

**Triadic (evenly spaced):**
- Primary Triadic: `["red", "blue", "yellow", "white"]`
- Secondary Triadic: `["orange", "green", "purple", "white"]`

**Split-Complementary:**
- Blue Split: `["blue", "orange", "yellow", "white"]`

**Monochromatic:**
- Blue Monochrome: `["navy blue", "royal blue", "blue", "light blue", "white"]`
- Pink Monochrome: `["magenta", "hot pink", "pink", "light pink", "white"]`
- Grey Monochrome: `["black", "dark grey", "grey", "light grey", "white"]`

#### 2. Mood Palettes (10-15 palettes)

**Warm:**
- Cozy Warm: `["cream", "brown", "orange", "gold", "white"]`
- Passionate: `["red", "crimson", "gold", "black"]`
- Cheerful: `["yellow", "orange", "pink", "white"]`

**Cool:**
- Cool Ocean: `["blue", "teal", "white", "silver"]`
- Mysterious Night: `["navy blue", "purple", "silver", "black"]`
- Icy: `["white", "light blue", "silver", "pale blue"]`

**Dark/Gothic:**
- Gothic Dark: `["black", "crimson", "purple", "silver"]`
- Elegant Dark: `["black", "wine red", "gold"]`
- Vampire: `["black", "red", "white", "gold"]`

**Soft/Light:**
- Soft Dream: `["lavender", "pink", "white", "cream"]`
- Cloud Soft: `["white", "light blue", "light pink", "cream"]`

#### 3. Theme Palettes (15-20 palettes)

**Pastel:**
- Pastel Rainbow: `["light pink", "light blue", "mint", "lavender", "cream"]`
- Pastel Warm: `["light pink", "peach", "cream", "light yellow"]`
- Pastel Cool: `["lavender", "light blue", "mint", "white"]`

**Neon/Cyberpunk:**
- Cyberpunk Neon: `["hot pink", "cyan", "purple", "black"]`
- Arcade Glow: `["magenta", "lime", "cyan", "black"]`

**Military/Tactical:**
- Military Green: `["olive", "tan", "brown", "black"]`
- Naval: `["navy blue", "white", "gold", "red"]`

**Gothic Lolita:**
- Classic Gothic: `["black", "white", "red", "silver"]`
- Sweet Gothic: `["black", "pink", "white", "purple"]`

**Elegant:**
- Royal Elegant: `["royal blue", "gold", "white"]`
- Rose Elegant: `["wine red", "gold", "cream", "black"]`
- Black Tie: `["black", "white", "gold", "silver"]`

**Nature:**
- Forest Fairy: `["green", "brown", "gold", "cream"]`
- Ocean Mermaid: `["teal", "aqua", "purple", "silver"]`
- Flower Garden: `["pink", "green", "yellow", "white"]`

#### 4. Anime Classic Palettes (15-20 palettes)

**School Uniforms:**
- Sailor Navy: `["navy blue", "white", "red"]`
- Sailor Green: `["forest green", "white", "red", "yellow"]`
- Blazer Classic: `["navy blue", "white", "red", "grey"]`
- Summer Sailor: `["white", "blue", "light blue"]`

**Maid:**
- Classic Maid: `["black", "white", "red"]`
- Victorian Maid: `["black", "white", "purple", "gold"]`
- Pastel Maid: `["pink", "white", "light blue"]`

**Magical Girl:**
- Magical Pink: `["pink", "white", "gold", "red"]`
- Magical Blue: `["blue", "white", "gold", "pink"]`
- Dark Magical: `["purple", "black", "silver", "pink"]`

**Japanese Traditional:**
- Shrine Maiden: `["white", "red"]`
- Kimono Classic: `["red", "white", "gold", "black"]`
- Yukata Summer: `["light blue", "white", "pink"]`

**Fantasy:**
- Knight Silver: `["silver", "blue", "white", "gold"]`
- Witch Classic: `["black", "purple", "gold", "orange"]`
- Elf Forest: `["green", "brown", "gold", "silver"]`
- Demon: `["black", "red", "purple", "gold"]`

#### 5. Seasonal Palettes (10-15 palettes)

**Spring:**
- Cherry Blossom: `["pink", "white", "green", "brown"]`
- Spring Fresh: `["light green", "pink", "yellow", "white"]`

**Summer:**
- Summer Beach: `["light blue", "white", "yellow", "coral"]`
- Tropical: `["cyan", "orange", "pink", "green"]`
- Festival: `["red", "white", "gold", "blue"]`

**Autumn:**
- Autumn Leaves: `["orange", "red", "brown", "gold"]`
- Harvest: `["brown", "orange", "cream", "burgundy"]`

**Winter:**
- Winter Snow: `["white", "light blue", "silver", "navy blue"]`
- Christmas: `["red", "green", "gold", "white"]`
- Cozy Winter: `["cream", "brown", "red", "green"]`

**Holiday:**
- Valentine: `["pink", "red", "white", "gold"]`
- Halloween: `["orange", "black", "purple", "green"]`

---

## 6) Format Rules

- Use lowercase for all color names
- Keep color names simple and SD-compatible (e.g., "blue" not "cerulean")
- Order colors by dominance (primary first, accents last)
- Include 3-6 colors per palette
- White and black can appear in multiple palettes as they are neutral
- Ensure all palette IDs are added to `index_by_palette_type`

---

## 7) Validation Checklist

- [ ] All palettes have unique `id` values
- [ ] All palettes have `type` set to one of 5 valid types
- [ ] All palette IDs appear in `index_by_palette_type`
- [ ] `individual_colors` contains all colors used in palettes
- [ ] Each palette has 3-6 colors
- [ ] `generated_utc` is set
- [ ] Descriptions are concise but helpful
