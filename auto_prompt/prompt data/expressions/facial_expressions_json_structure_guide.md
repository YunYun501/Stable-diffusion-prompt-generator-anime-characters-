# Facial Expressions JSON Structure Guide
This document explains the structure of the facial expression catalog JSON file:
- **Catalog file:** `female_expressions.json`
- **Purpose:** Let an AI agent reliably sample anime-style facial expressions by *emotion family*.

Generated: 2026-02-10T23:59:19Z

---
## 1) Top-level schema
The JSON root is an object with these keys (current file):

```text
['schema_version', 'title', 'generated_utc', 'items', 'index_by_emotion_family', 'meta']
```

The schema centers on two core sections:
1. **`items`**: the master list of expression labels
2. **`index_by_emotion_family`**: a fast lookup map from emotion-family → list of item IDs

Optional metadata lives under `meta`.

---
## 2) `items` (master list)
- Type: **array of objects**
- Count: **92** items in the current file

Each item represents **one exact facial-expression label** (a string you can use directly in prompts/tags).

### 2.1 Item fields
Fields present across the dataset:

```text
['emotion_family', 'id', 'name']
```

### 2.2 Field definitions
#### `id` (string)
A stable identifier (slug). Use this for indexing, storage, and random selection.

#### `name` (string)
The **exact** expression text.

#### `emotion_family` (string enum)
The emotion grouping this expression belongs to (e.g., happiness, anger, embarrassment).

### 2.3 Example item
```json
{
  "id": "neutral_baseline__neutral_blank",
  "name": "Neutral / blank",
  "emotion_family": "neutral_baseline"
}
```

---
## 3) `index_by_emotion_family` (fast lookup)
- Type: **object/dictionary**
- Keys: emotion-family IDs (strings)
- Values: arrays of **item IDs** (strings)

Example:

```json
{
  "happiness_positive": [
    "happiness_positive__smile_closedmouth",
    "happiness_positive__big_smile_openmouth"
  ]
}
```

This section lets an agent sample by emotion family without scanning the full `items` array.

---
## 4) `meta` (optional metadata)
`meta` contains helpful human-readable information:

- **`emotion_families`**: list of `{id, name}` entries for all families
- **`notes`**: schema usage notes

### 4.1 Emotion families (current file)
IDs and names:

```text
- neutral_baseline: Neutral / baseline
- happiness_positive: Happiness / positive mood
- affection_romance: Affection / romance
- playful_teasing_smug: Playful / teasing / smug
- embarrassment_shyness: Embarrassment / shyness
- surprise_shock: Surprise / shock
- anger_irritation: Anger / irritation
- sadness_hurt: Sadness / hurt
- fear_anxiety_panic: Fear / anxiety / panic
- disgust_contempt: Disgust / "ew" / contempt
- determination_resolve: Determination / resolve
- confusion_skepticism: Confusion / skepticism
- tired_sleepy_bored: Tired / sleepy / bored
- pain_strain_sickness: Pain / strain / sickness
- extreme_anime_stylized: "Extreme anime" expressions (stylized tropes)
```

### 4.2 Counts per emotion family
Number of expressions available in each family:

```text
- extreme_anime_stylized: 12
- anger_irritation: 7
- happiness_positive: 7
- sadness_hurt: 7
- affection_romance: 6
- embarrassment_shyness: 6
- fear_anxiety_panic: 6
- neutral_baseline: 6
- playful_teasing_smug: 6
- confusion_skepticism: 5
- determination_resolve: 5
- pain_strain_sickness: 5
- surprise_shock: 5
- tired_sleepy_bored: 5
- disgust_contempt: 4
```

---
## 5) Recommended agent usage patterns
### 5.1 Load and sample by emotion family
Python-like pseudocode:

```python
import json, random

with open('female_anime_facial_expressions_emotion_indexed.json', 'r', encoding='utf-8') as f:
    catalog = json.load(f)

items = catalog['items']
index = catalog['index_by_emotion_family']

# Build id -> item map for O(1) access
by_id = {it['id']: it for it in items}

def sample_expression(family_id: str):
    pool = index.get(family_id, [])
    if not pool:
        return None
    return by_id[random.choice(pool)]['name']

expr = sample_expression('embarrassment_shyness')
print(expr)
```

### 5.2 Random expression across all families
If you want fully random selection:

```python
import random
expr = random.choice(items)['name']
```

---
## 6) Extension points (safe to add later)
You can add optional fields without breaking basic agents (agents should ignore unknown keys):
- `feature_tags`: e.g., `{eyes: 'sparkly', mouth: 'open', extras: ['blush']}`
- `intensity`: e.g., `low/medium/high`
- `rarity_weight`: numeric sampling weight
