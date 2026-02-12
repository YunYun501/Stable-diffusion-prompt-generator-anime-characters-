# Poses JSON Structure Guide

This document explains the structure of the poses JSON file and provides instructions for an AI agent to populate it.

- **Catalog file:** `poses.json`
- **Purpose:** Provide a structured catalog of character poses for anime image generation.

---

## 1) Top-level Schema

```text
['schema_version', 'title', 'generated_utc', 'items', 'index_by_category', 'categories', 'meta']
```

---

## 2) Categories

| Category | Description | Example Values |
|----------|-------------|----------------|
| `standing` | Standing positions | standing, leaning, contrapposto |
| `sitting` | Seated positions | sitting, seiza, crossed legs |
| `action` | Dynamic poses | running, jumping, fighting stance |
| `lying` | Reclining poses | lying down, on side, on back |
| `gesture` | Hand/arm gestures | peace sign, waving, pointing |
| `special` | Anime-specific poses | JoJo pose, magical girl pose |

---

## 3) Item Structure

```json
{
  "id": "peace_sign",
  "name": "peace sign",
  "category": "gesture",
  "aliases": ["v sign", "victory sign"],
  "uses_hands": true
}
```

---

## 4) Instructions for AI Agent

**Task:** Populate the `poses.json` with comprehensive anime pose options.

### Requirements:

1. **Standing Poses (15-25 items):**
   - standing, standing straight, casual standing
   - leaning forward, leaning back, leaning against wall
   - contrapposto, model pose, idol pose
   - hand on hip, hands on hips, arms crossed
   - arms behind back, hands behind head
   - looking back, looking over shoulder
   - from behind, from side
   - full body, upper body, portrait

2. **Sitting Poses (15-20 items):**
   - sitting, sitting on chair, sitting on floor
   - seiza (formal Japanese sitting)
   - crossed legs, indian style, legs crossed
   - wariza, w-sitting
   - hugging knees, knees up
   - sitting on bed, sitting on bench
   - lounging, relaxed sitting

3. **Action Poses (20-30 items):**
   - running, walking, jumping
   - fighting stance, combat pose, battle stance
   - kicking, punching, sword fighting
   - dancing, spinning, twirling
   - flying, floating, levitating
   - casting spell, magic pose
   - drawing weapon, aiming
   - falling, mid-air, action shot

4. **Lying Poses (10-15 items):**
   - lying down, lying on back, lying on side
   - lying on stomach, prone
   - sprawled, stretched out
   - curled up, fetal position
   - reclining, propped up on elbow

5. **Gestures (20-30 items):**
   - peace sign, v sign, victory pose
   - waving, waving hand
   - pointing, pointing at viewer, pointing up
   - thumbs up, ok sign
   - salute, military salute
   - finger to lips, shushing
   - hand over heart, hand on chest
   - covering mouth, covering face
   - adjusting glasses, pushing up glasses
   - hair flip, playing with hair, twirling hair
   - chin rest, hand on chin
   - prayer hands, clasped hands
   - fist raised, fist pump
   - blowing kiss, heart hands

6. **Special/Anime Poses (15-25 items):**
   - JoJo pose, dramatic pose
   - magical girl transformation, transformation pose
   - idol pose, stage pose, concert pose
   - cat pose, paw pose, nyaa pose
   - thinking pose, contemplating
   - embarrassed pose, shy pose
   - tsundere pose, looking away
   - greeting, bowing
   - curtsy, elegant pose
   - fighting game pose, victory pose
   - selfie pose, phone pose
   - eating, drinking
   - reading, studying

### Format Rules:
- Use lowercase for `id` and `name`
- Use underscores in `id`, spaces in `name`
- Focus on SFW poses
- Include `uses_hands` boolean for every item (`true` when pose/action relies on hands/arms)
- Ensure all item IDs are added to `index_by_category`

---

## 5) Validation Checklist

- [ ] All items have unique `id` values
- [ ] All items have valid `category` values
- [ ] All item IDs appear in `index_by_category`
- [ ] All items include `uses_hands` boolean
- [ ] `generated_utc` is set
- [ ] All poses are SFW appropriate
