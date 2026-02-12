# Backgrounds JSON Structure Guide

This document explains the structure of the backgrounds JSON file and provides instructions for an AI agent to populate it.

- **Catalog file:** `backgrounds.json`
- **Purpose:** Provide a structured catalog of scene backgrounds and settings for anime image generation.

---

## 1) Top-level Schema

```text
['schema_version', 'title', 'generated_utc', 'items', 'index_by_category', 'categories', 'meta']
```

---

## 2) Categories

| Category | Description | Example Values |
|----------|-------------|----------------|
| `simple` | Minimal backgrounds | white background, gradient background |
| `indoor` | Interior locations | bedroom, kitchen, library |
| `outdoor_urban` | City environments | street, rooftop, cafe |
| `outdoor_nature` | Natural settings | forest, beach, mountain |
| `fantasy` | Magical locations | castle, dungeon, floating island |
| `school` | School settings | classroom, hallway, gym |
| `special` | Seasonal/event | cherry blossoms, festival, Christmas |

---

## 3) Item Structure

```json
{
  "id": "classroom",
  "name": "classroom",
  "category": "school",
  "aliases": ["school classroom", "class"]
}
```

---

## 4) Instructions for AI Agent

**Task:** Populate the `backgrounds.json` with comprehensive background options.

### Requirements:

1. **Simple Backgrounds (15-20 items):**
   - white background, black background, grey background
   - simple background, plain background
   - gradient background, blue gradient, pink gradient
   - bokeh, blurry background, depth of field
   - starry background, sparkle background
   - solid color background
   - two-tone background
   - abstract background
   - studio lighting, professional lighting

2. **Indoor Settings (25-35 items):**
   
   **Home:**
   - bedroom, living room, kitchen, bathroom
   - hallway, dining room, attic
   - traditional Japanese room, tatami room
   - modern apartment, cozy room
   
   **Commercial:**
   - cafe, restaurant, bar, coffee shop
   - library, bookstore, shop
   - office, workspace
   - hospital, clinic
   
   **Entertainment:**
   - stage, concert hall, theater
   - arcade, game center
   - karaoke room
   - gym, dojo, training room
   
   **Other:**
   - church, temple, shrine interior
   - museum, gallery
   - train interior, bus interior

3. **Urban Outdoor (20-30 items):**
   - city street, urban street, downtown
   - rooftop, building rooftop
   - alleyway, back alley
   - park, city park, playground
   - shopping district, market
   - train station, bus stop
   - bridge, overpass
   - sidewalk cafe, outdoor seating
   - parking lot, parking garage
   - construction site
   - neon city, night city, cyberpunk city
   - Tokyo street, Japanese city

4. **Nature Outdoor (25-35 items):**
   - forest, woods, jungle
   - beach, seaside, ocean
   - mountain, hilltop, cliff
   - meadow, field, grassland
   - lake, river, waterfall
   - garden, flower garden, rose garden
   - cherry blossom trees, sakura trees
   - bamboo forest
   - desert, canyon
   - snow field, winter landscape
   - sunset, sunrise, golden hour
   - night sky, starry night, moonlit
   - rain, rainy day
   - cloudy sky, dramatic sky

5. **Fantasy Settings (20-30 items):**
   - castle, throne room, palace
   - dungeon, cave, underground
   - floating island, sky island
   - magical forest, enchanted woods
   - dragon's lair
   - wizard tower, mage tower
   - ancient ruins, temple ruins
   - crystal cave, ice cave
   - volcanic, lava, fire realm
   - underwater, ocean floor
   - heaven, clouds, celestial
   - hell, inferno, demon realm
   - space, galaxy, nebula
   - alien planet, sci-fi
   - steampunk city
   - medieval village, fantasy town

6. **School Settings (15-20 items):**
   - classroom, empty classroom
   - school hallway, corridor
   - school rooftop
   - gymnasium, school gym
   - swimming pool, school pool
   - cafeteria, lunch room
   - library, school library
   - club room
   - locker room
   - school gate, school entrance
   - schoolyard, school grounds
   - track field, sports field
   - music room
   - science lab

7. **Special/Seasonal (20-30 items):**
   
   **Seasons:**
   - spring, cherry blossom season
   - summer, summer festival
   - autumn, fall leaves, autumn leaves
   - winter, snow, snowy
   
   **Events:**
   - festival, matsuri, Japanese festival
   - fireworks, fireworks festival
   - Christmas, Christmas lights, Christmas tree
   - Halloween, spooky
   - New Year, shrine visit
   - Valentine's Day
   - beach vacation, summer vacation
   
   **Time of day:**
   - morning, early morning
   - noon, midday
   - afternoon
   - evening, dusk, twilight
   - night, nighttime, midnight

### Format Rules:
- Use lowercase for `id` and `name`
- Use underscores in `id`, spaces in `name`
- Be specific enough to guide SD but not overly complex
- Ensure all item IDs are added to `index_by_category`

---

## 5) Validation Checklist

- [ ] All items have unique `id` values
- [ ] All items have valid `category` values
- [ ] All item IDs appear in `index_by_category`
- [ ] `generated_utc` is set
- [ ] Good variety within each category
