#!/usr/bin/env python3
"""
CivitAI Prompt Scraper & Auto-Categorizer

Scrapes most-collected anime posts from CivitAI (female characters only),
extracts prompts, and auto-categorizes tokens into catalog categories.

Outputs a review JSON file for manual approval - does NOT auto-merge into catalogs.

Usage:
    python tools/scrape_civitai.py --limit 500 --period Month
    python tools/scrape_civitai.py --limit 100 --dry-run
"""

import argparse
import json
import re
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from urllib.parse import urlencode

try:
    import requests
except ImportError:
    print("ERROR: 'requests' library required. Install with: pip install requests")
    exit(1)

# === Configuration ===

API_URL = "https://civitai.com/api/v1/images"

# Female character detection tags
FEMALE_TAGS = {
    "1girl", "girl", "woman", "female", "2girls", "3girls", "multiple girls",
    "1woman", "solo female", "female focus", "girls", "women"
}

# Tags to skip (quality tags, technical, LoRAs)
SKIP_PATTERNS = [
    "masterpiece", "best quality", "highres", "absurdres", "4k", "8k",
    "ultra detailed", "extremely detailed", "detailed", "high quality",
    "high resolution", "hq", "uhd", "hdr", "<lora", "embedding:",
    "score_", "source_", "rating:", "nsfw", "sfw", "year 20", "newest",
    "very aesthetic", "intricate details", "incredible quality", "amazing quality"
]

# Keyword patterns for classification (order matters - more specific first)
KEYWORD_PATTERNS = {
    # Hair styles
    "hair_style": [
        "ponytail", "twintails", "twin tails", "pigtails", "braid", "braids",
        "braided hair", "french braid", "side braid", "bangs", "blunt bangs",
        "swept bangs", "parted bangs", "hair over eye", "ahoge", "antenna hair",
        "bun", "hair bun", "double bun", "side bun", "bob cut", "hime cut",
        "pixie cut", "asymmetrical hair", "drill hair", "ringlets", "sidelocks",
        "hair intakes", "hair flaps", "forehead", "curtained hair", "updo"
    ],
    # Hair length
    "hair_length": [
        "very long hair", "long hair", "medium hair", "short hair", "very short hair",
        "shoulder-length hair", "waist-length hair"
    ],
    # Hair texture
    "hair_texture": [
        "wavy hair", "curly hair", "straight hair", "messy hair", "wet hair",
        "floating hair", "hair spread out", "windswept hair", "slicked back"
    ],
    # Eye accessories
    "eye_accessories": [
        "glasses", "eyepatch", "monocle", "sunglasses", "blindfold", "eyewear",
        "semi-rimless", "round glasses", "red-framed glasses"
    ],
    # Body type
    "body_type": [
        "slim", "petite", "muscular", "curvy", "slender", "athletic",
        "large breasts", "medium breasts", "small breasts", "flat chest"
    ],
    # Skin
    "skin": [
        "pale skin", "tan skin", "dark skin", "fair skin", "white skin",
        "tanned"
    ],
    # Special features
    "special_features": [
        "wings", "angel wings", "demon wings", "bat wings", "horns",
        "tail", "demon tail", "cat tail", "fox tail", "elf ears", "pointy ears",
        "halo", "fangs", "cat ears", "animal ears", "fox ears", "rabbit ears",
        "dog ears", "wolf ears", "scales", "claws", "antlers", "kemonomimi"
    ],
    # Expressions
    "expression": [
        "smile", "smiling", "grin", "frown", "blush", "blushing", "tears",
        "crying", "angry", "happy", "sad", "smirk", "pout", "pouting",
        "closed eyes", "one eye closed", "wink", "open mouth", "parted lips",
        "tongue out", "licking lips", "surprised", "embarrassed", "shy",
        "serious", "expressionless", "ahegao", "nervous", "worried"
    ],
    # Neck
    "neck": [
        "choker", "necklace", "scarf", "collar", "tie", "bowtie", "necktie",
        "neck ribbon", "pendant", "chain necklace", "pearl necklace"
    ],
    # Outerwear
    "outerwear": [
        "coat", "cape", "jacket", "cardigan", "hoodie", "cloak", "robe",
        "blazer", "trench coat", "fur coat", "leather jacket", "denim jacket",
        "bomber jacket", "overcoat", "poncho", "shawl", "mantle"
    ],
    # Chest
    "chest": [
        "chest harness", "breastplate", "chest armor", "chest wrap",
        "bustier", "corsage", "chestpiece"
    ],
    # Arms
    "arms": [
        "sleeves", "detached sleeves", "long sleeves", "short sleeves",
        "arm warmers", "armlet", "bare arms", "single sleeve", "puffy sleeves",
        "wide sleeves", "arm tattoo"
    ],
    # Hands
    "hands": [
        "gloves", "bracelet", "gauntlet", "fingerless gloves", "nail polish",
        "black gloves", "white gloves", "elbow gloves", "mittens", "wrist cuffs",
        "ring", "rings", "watch", "wristband"
    ],
    # Waist
    "waist": [
        "belt", "sash", "corset", "obi", "waist ribbon", "chain belt",
        "leather belt", "waist apron", "cummerbund"
    ],
    # Upper body
    "upper_body": [
        "shirt", "blouse", "top", "sweater", "vest", "bra", "bikini top",
        "crop top", "tank top", "t-shirt", "halter top", "tube top",
        "turtleneck", "off-shoulder", "camisole", "corset top", "bodice",
        "polo shirt", "button-up", "sleeveless shirt", "sailor collar"
    ],
    # Lower body
    "lower_body": [
        "skirt", "pants", "shorts", "miniskirt", "pleated skirt", "jeans",
        "long skirt", "pencil skirt", "a-line skirt", "high-waisted",
        "hot pants", "denim shorts", "short shorts", "hakama", "bloomers",
        "panties", "underwear", "bikini bottom", "frilled skirt"
    ],
    # Full body outfits
    "full_body": [
        "dress", "uniform", "bodysuit", "jumpsuit", "kimono", "yukata",
        "maid", "maid outfit", "maid dress", "wedding dress", "gown",
        "evening dress", "cocktail dress", "school uniform", "sailor uniform",
        "serafuku", "military uniform", "nurse uniform", "waitress",
        "bunny suit", "leotard", "swimsuit", "one-piece swimsuit", "bikini",
        "qipao", "cheongsam", "hanfu", "ao dai", "gothic lolita", "lolita",
        "armor", "knight", "witch", "magical girl", "idol", "nun", "shrine maiden"
    ],
    # Legs
    "legs": [
        "thighhighs", "pantyhose", "kneehighs", "leggings", "bare legs",
        "stockings", "fishnet", "garter", "garter belt", "thigh strap",
        "knee-high socks", "ankle socks", "leg tattoo", "tights", "over-knee"
    ],
    # Feet
    "feet": [
        "shoes", "boots", "heels", "sandals", "sneakers", "barefoot",
        "high heels", "platform shoes", "mary janes", "loafers", "flats",
        "ankle boots", "thigh boots", "knee boots", "slippers", "flip flops"
    ],
    # Head accessories
    "head": [
        "hat", "cap", "crown", "hairpin", "headband", "tiara", "hair ribbon",
        "hair flower", "hair ornament", "bow", "hair bow", "headpiece",
        "veil", "headdress", "circlet", "headphones", "hair clip", "barrette",
        "kanzashi", "beret", "witch hat", "hood", "bunny ears", "cat ears headband"
    ],
    # Accessories
    "accessory": [
        "earrings", "bag", "backpack", "umbrella", "parasol", "fan",
        "handbag", "purse", "weapon", "sword", "katana", "staff", "wand",
        "book", "camera", "phone", "smartphone", "microphone", "wings accessory",
        "mask", "domino mask", "eye mask"
    ],
    # Poses
    "pose": [
        "sitting", "standing", "lying", "kneeling", "jumping", "running",
        "walking", "leaning", "crouching", "squatting", "floating", "flying",
        "lounging", "reclining", "bending over", "looking back", "turning around",
        "arms up", "arms behind back", "hands behind back", "hands on hips"
    ],
    # Gestures
    "gesture": [
        "pointing", "waving", "peace sign", "v sign", "crossed arms",
        "hands together", "praying", "salute", "thumbs up", "hand on chest",
        "hand on chin", "finger to mouth", "shushing", "beckoning", "reaching out"
    ],
    # View angles
    "view_angle": [
        "from above", "from below", "from behind", "from side", "portrait",
        "close-up", "upper body", "cowboy shot", "full body", "face focus",
        "dutch angle", "low angle", "high angle", "pov", "first-person view"
    ],
    # Backgrounds
    "background": [
        "simple background", "white background", "gradient background",
        "outdoors", "indoors", "forest", "beach", "classroom", "bedroom",
        "kitchen", "bathroom", "office", "street", "city", "night",
        "sunset", "sunrise", "sky", "clouds", "rain", "snow", "cherry blossoms",
        "window", "balcony", "rooftop", "garden", "park", "temple", "shrine",
        "castle", "ruins", "fantasy", "futuristic", "cyberpunk", "nature"
    ]
}

# Map categories to catalog files
CATEGORY_TO_CATALOG = {
    "hair_style": "hair/hair_catalog.json",
    "hair_length": "hair/hair_catalog.json",
    "hair_texture": "hair/hair_catalog.json",
    "hair_color": "hair/hair_catalog.json",
    "eye_color": "eyes/eye_catalog.json",
    "eye_accessories": "eyes/eye_catalog.json",
    "body_type": "body/body_features.json",
    "skin": "body/body_features.json",
    "special_features": "body/body_features.json",
    "expression": "expressions/female_expressions.json",
    "neck": "clothing/clothing_list.json",
    "outerwear": "clothing/clothing_list.json",
    "chest": "clothing/clothing_list.json",
    "arms": "clothing/clothing_list.json",
    "hands": "clothing/clothing_list.json",
    "waist": "clothing/clothing_list.json",
    "upper_body": "clothing/clothing_list.json",
    "lower_body": "clothing/clothing_list.json",
    "full_body": "clothing/clothing_list.json",
    "legs": "clothing/clothing_list.json",
    "feet": "clothing/clothing_list.json",
    "head": "clothing/clothing_list.json",
    "accessory": "clothing/clothing_list.json",
    "pose": "poses/poses.json",
    "gesture": "poses/poses.json",
    "view_angle": "view_angles/view_angles.json",
    "background": "backgrounds/backgrounds.json"
}

# Suggest style groups based on context
STYLE_GROUP_KEYWORDS = {
    "modern_everyday": ["shirt", "jeans", "sneakers", "casual", "hoodie", "t-shirt"],
    "cute_themed": ["bunny", "cat", "bow", "ribbon", "lolita", "maid", "frilly"],
    "fantasy_medieval": ["armor", "knight", "cape", "cloak", "sword", "medieval", "witch"],
    "traditional_asian": ["kimono", "hanfu", "qipao", "hakama", "obi", "kanzashi"],
    "formal_elegant": ["dress", "gown", "heels", "evening", "formal", "elegant"],
    "athletic_sporty": ["sportswear", "athletic", "gym", "sneakers", "shorts"],
    "futuristic_scifi": ["cyber", "futuristic", "neon", "tech", "sci-fi", "mech"]
}


class CivitAIScraper:
    """Scrapes and processes CivitAI image prompts."""

    def __init__(
        self,
        limit: int = 100,
        period: str = "Month",
        min_frequency: int = 2,
        nsfw: str = "None",
        dry_run: bool = False,
        data_dir: Optional[Path] = None
    ):
        self.limit = limit
        self.period = period
        self.min_frequency = min_frequency
        self.nsfw = nsfw
        self.dry_run = dry_run
        self.data_dir = data_dir or Path(__file__).parent.parent / "prompt data"
        self.existing_items = self._load_existing_items()
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "PromptScraper/1.0 (Educational/Research)"
        })

    def _load_existing_items(self) -> set:
        """Load all existing item IDs and aliases from catalogs."""
        existing = set()
        catalogs = [
            "clothing/clothing_list.json",
            "hair/hair_catalog.json",
            "eyes/eye_catalog.json",
            "body/body_features.json",
            "expressions/female_expressions.json",
            "poses/poses.json",
            "view_angles/view_angles.json",
            "backgrounds/backgrounds.json"
        ]

        for catalog_path in catalogs:
            full_path = self.data_dir / catalog_path
            if full_path.exists():
                try:
                    with open(full_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        for item in data.get("items", []):
                            existing.add(item.get("id", "").lower())
                            existing.add(item.get("name", "").lower())
                            for alias in item.get("aliases", []):
                                existing.add(alias.lower())
                except Exception as e:
                    print(f"Warning: Could not load {catalog_path}: {e}")

        return existing

    def fetch_images(self) -> list[dict]:
        """Fetch images from CivitAI API with pagination."""
        all_images = []
        cursor = None
        fetched = 0
        page = 1

        print(f"Fetching up to {self.limit} images from CivitAI...")
        print(f"  Period: {self.period}")
        print(f"  NSFW: {self.nsfw}")
        print(f"  Sort: Most Collected")
        print()

        while fetched < self.limit:
            params = {
                "limit": min(100, self.limit - fetched),
                "nsfw": self.nsfw,
                "sort": "Most Collected",
                "period": self.period
            }
            if cursor:
                params["cursor"] = cursor

            url = f"{API_URL}?{urlencode(params)}"
            print(f"  Page {page}: Fetching {params['limit']} images...")

            try:
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                data = response.json()
            except requests.RequestException as e:
                print(f"    Error: {e}")
                break

            items = data.get("items", [])
            if not items:
                print("    No more images available")
                break

            all_images.extend(items)
            fetched += len(items)
            print(f"    Got {len(items)} images (total: {fetched})")

            # Get next cursor for pagination
            metadata = data.get("metadata", {})
            cursor = metadata.get("nextCursor")
            if not cursor:
                break

            page += 1
            # Rate limiting: 1 second between requests
            time.sleep(1)

        print(f"\nTotal images fetched: {len(all_images)}")
        return all_images

    def extract_prompts(self, images: list[dict]) -> list[dict]:
        """Extract prompts from images, filtering for female characters only."""
        prompts = []

        for img in images:
            meta = img.get("meta") or {}
            prompt = meta.get("prompt", "")

            if not prompt:
                continue

            # Check if it's a female character prompt
            if not self._is_female_prompt(prompt):
                continue

            prompts.append({
                "id": img.get("id"),
                "url": img.get("url"),
                "prompt": prompt,
                "negative_prompt": meta.get("negativePrompt", ""),
                "stats": img.get("stats", {})
            })

        print(f"Extracted {len(prompts)} female character prompts")
        return prompts

    def _is_female_prompt(self, prompt: str) -> bool:
        """Check if prompt contains female character tags."""
        tokens = {t.strip().lower() for t in prompt.split(",")}
        return bool(tokens & FEMALE_TAGS)

    def tokenize_prompt(self, prompt: str) -> list[str]:
        """Tokenize a prompt into individual tags."""
        tokens = []
        for token in prompt.split(","):
            token = token.strip()
            if not token:
                continue

            # Remove weighting syntax: (tag:1.2) -> tag
            token = re.sub(r"\(([^:]+):[0-9.]+\)", r"\1", token)
            # Remove parentheses: ((tag)) -> tag
            token = re.sub(r"[()]+", "", token)
            # Clean up extra spaces
            token = re.sub(r"\s+", " ", token).strip()

            if token:
                tokens.append(token)

        return tokens

    def classify_token(self, token: str) -> str:
        """Classify a token into a category."""
        token_lower = token.lower().strip()

        # Skip quality/technical tags
        for skip in SKIP_PATTERNS:
            if skip in token_lower:
                return "skip"

        # Skip very short tokens (likely noise)
        if len(token_lower) < 3:
            return "skip"

        # Skip numeric-only tokens
        if token_lower.isdigit():
            return "skip"

        # Check keyword patterns (ordered for specificity)
        for category, keywords in KEYWORD_PATTERNS.items():
            for keyword in keywords:
                if keyword in token_lower:
                    return category

        # Regex patterns for color-based items
        # Hair color: "blonde hair", "pink hair", etc.
        if re.match(r"^[\w\s-]+\s+hair$", token_lower) and "hair" not in token_lower.replace(" hair", ""):
            return "hair_color"

        # Eye color: "blue eyes", "red eyes", etc.
        if re.match(r"^[\w\s-]+\s+eyes$", token_lower):
            return "eye_color"

        # Background detection
        if "background" in token_lower:
            return "background"

        return "unknown"

    def suggest_style_group(self, token: str, category: str) -> str:
        """Suggest a style group based on the token and category."""
        token_lower = token.lower()

        for group, keywords in STYLE_GROUP_KEYWORDS.items():
            for keyword in keywords:
                if keyword in token_lower:
                    return group

        # Default groups by category
        default_groups = {
            "hair_style": "natural",
            "hair_length": "natural",
            "hair_color": "natural",
            "expression": "positive",
            "pose": "static",
            "gesture": "expressive",
            "full_body": "general"
        }

        return default_groups.get(category, "general")

    def generate_id(self, token: str) -> str:
        """Generate a unique ID from a token."""
        # Lowercase, replace spaces with underscores, remove special chars
        id_str = token.lower().strip()
        id_str = re.sub(r"[^a-z0-9\s]", "", id_str)
        id_str = re.sub(r"\s+", "_", id_str)
        return id_str

    def process_prompts(self, prompts: list[dict]) -> dict:
        """Process all prompts and generate categorized items."""
        # Count token frequency
        token_counts = Counter()
        token_categories = {}

        for prompt_data in prompts:
            tokens = self.tokenize_prompt(prompt_data["prompt"])
            for token in tokens:
                token_clean = token.lower().strip()
                token_counts[token_clean] += 1

                if token_clean not in token_categories:
                    token_categories[token_clean] = self.classify_token(token)

        # Filter by minimum frequency
        popular_tokens = {
            t: c for t, c in token_counts.items()
            if c >= self.min_frequency
        }

        print(f"Found {len(popular_tokens)} tokens appearing {self.min_frequency}+ times")

        # Build pending items
        pending_items = []
        skipped_count = 0
        existing_count = 0
        unknown_count = 0

        for token, count in sorted(popular_tokens.items(), key=lambda x: -x[1]):
            category = token_categories.get(token, "unknown")

            if category == "skip":
                skipped_count += 1
                continue

            item_id = self.generate_id(token)

            # Check if already exists
            already_exists = (
                item_id in self.existing_items or
                token in self.existing_items
            )

            if already_exists:
                existing_count += 1
                continue

            if category == "unknown":
                unknown_count += 1
                # Still include unknown items for manual review
                category = "uncategorized"

            pending_items.append({
                "id": item_id,
                "name": token,
                "name_i18n": {
                    "en": token,
                    "zh": ""  # Leave empty for manual translation
                },
                "suggested_category": category,
                "suggested_group": self.suggest_style_group(token, category),
                "target_catalog": CATEGORY_TO_CATALOG.get(category, ""),
                "frequency": count,
                "already_exists": False,
                "source": "civitai_scrape"
            })

        print(f"  Skipped: {skipped_count} (quality/technical tags)")
        print(f"  Already exist: {existing_count}")
        print(f"  Unknown category: {unknown_count}")
        print(f"  New items: {len(pending_items)}")

        return {
            "pending_items": pending_items,
            "stats": {
                "total_tokens": len(token_counts),
                "popular_tokens": len(popular_tokens),
                "skipped": skipped_count,
                "existing": existing_count,
                "unknown": unknown_count,
                "new_items": len(pending_items)
            }
        }

    def save_results(self, prompts: list[dict], processed: dict):
        """Save results to output files."""
        output_dir = self.data_dir / "scraped"
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        # Save raw prompts
        raw_prompts_file = output_dir / "raw_prompts.json"
        raw_data = {
            "scraped_at": timestamp,
            "source": "civitai",
            "period": self.period,
            "total_prompts": len(prompts),
            "prompts": prompts
        }

        if not self.dry_run:
            with open(raw_prompts_file, "w", encoding="utf-8") as f:
                json.dump(raw_data, f, indent=2, ensure_ascii=False)
            print(f"Saved raw prompts to: {raw_prompts_file}")
        else:
            print(f"[DRY RUN] Would save raw prompts to: {raw_prompts_file}")

        # Save pending items for review
        pending_file = output_dir / "pending_items.json"
        pending_data = {
            "generated_at": timestamp,
            "source": "civitai",
            "period": self.period,
            "min_frequency": self.min_frequency,
            "stats": processed["stats"],
            "instructions": (
                "Review items below. Remove unwanted items, add Chinese translations, "
                "and adjust categories/groups as needed. Then run merge_catalog.py to import."
            ),
            "items": processed["pending_items"]
        }

        if not self.dry_run:
            with open(pending_file, "w", encoding="utf-8") as f:
                json.dump(pending_data, f, indent=2, ensure_ascii=False)
            print(f"Saved pending items to: {pending_file}")
        else:
            print(f"[DRY RUN] Would save pending items to: {pending_file}")

        return pending_file

    def run(self):
        """Run the full scraping and processing pipeline."""
        print("=" * 60)
        print("CivitAI Prompt Scraper - Female Characters Only")
        print("=" * 60)
        print()

        # Step 1: Fetch images
        images = self.fetch_images()
        if not images:
            print("No images fetched. Exiting.")
            return

        # Step 2: Extract prompts (female only)
        prompts = self.extract_prompts(images)
        if not prompts:
            print("No female character prompts found. Exiting.")
            return

        # Step 3: Process and categorize
        print("\nProcessing and categorizing tokens...")
        processed = self.process_prompts(prompts)

        # Step 4: Save results
        print("\nSaving results...")
        output_file = self.save_results(prompts, processed)

        # Summary
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print(f"Images fetched: {len(images)}")
        print(f"Female prompts extracted: {len(prompts)}")
        print(f"New items for review: {processed['stats']['new_items']}")
        print()
        print("Next steps:")
        print(f"  1. Review: {output_file}")
        print("  2. Remove unwanted items")
        print("  3. Add Chinese translations")
        print("  4. Run: python tools/merge_catalog.py")


def main():
    parser = argparse.ArgumentParser(
        description="Scrape CivitAI for anime prompts and categorize tokens"
    )
    parser.add_argument(
        "--limit", "-l",
        type=int,
        default=100,
        help="Number of images to scrape (default: 100)"
    )
    parser.add_argument(
        "--period", "-p",
        choices=["Day", "Week", "Month", "Year", "AllTime"],
        default="Month",
        help="Time period for sorting (default: Month)"
    )
    parser.add_argument(
        "--min-frequency", "-f",
        type=int,
        default=2,
        help="Minimum frequency for including a token (default: 2)"
    )
    parser.add_argument(
        "--nsfw",
        choices=["None", "Soft", "Mature", "X"],
        default="None",
        help="NSFW filter level (default: None = SFW only)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview without saving files"
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=None,
        help="Path to prompt data directory"
    )

    args = parser.parse_args()

    scraper = CivitAIScraper(
        limit=args.limit,
        period=args.period,
        min_frequency=args.min_frequency,
        nsfw=args.nsfw,
        dry_run=args.dry_run,
        data_dir=args.data_dir
    )

    scraper.run()


if __name__ == "__main__":
    main()
