#!/usr/bin/env python3
"""
Merge approved items from pending_items.json into the appropriate catalogs.

This script reads the reviewed pending_items.json file and merges approved
items into their target catalog files.

Usage:
    python tools/merge_catalog.py
    python tools/merge_catalog.py --file "prompt data/scraped/pending_items.json"
    python tools/merge_catalog.py --dry-run
"""

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


# Category to body_part mapping for clothing catalog
CATEGORY_TO_BODY_PART = {
    "head": "head",
    "neck": "neck",
    "upper_body": "upper_body",
    "chest": "chest",
    "waist": "waist",
    "lower_body": "lower_body",
    "full_body": "full_body",
    "outerwear": "outerwear",
    "hands": "hands",
    "arms": "arms",
    "legs": "legs",
    "feet": "feet",
    "accessory": "accessory"
}

# Category to hair catalog category mapping
HAIR_CATEGORIES = {
    "hair_style": "style",
    "hair_length": "length",
    "hair_texture": "texture",
    "hair_color": "color"
}

# Category to body catalog category mapping
BODY_CATEGORIES = {
    "body_type": "body_type",
    "skin": "skin",
    "special_features": "special_features"
}


class CatalogMerger:
    """Merges pending items into catalog files."""

    def __init__(
        self,
        pending_file: Optional[Path] = None,
        data_dir: Optional[Path] = None,
        dry_run: bool = False
    ):
        self.data_dir = data_dir or Path(__file__).parent.parent / "prompt data"
        self.pending_file = pending_file or self.data_dir / "scraped" / "pending_items.json"
        self.dry_run = dry_run
        self.catalogs_modified = {}

    def load_pending_items(self) -> list[dict]:
        """Load pending items from JSON file."""
        if not self.pending_file.exists():
            raise FileNotFoundError(f"Pending items file not found: {self.pending_file}")

        with open(self.pending_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        return data.get("items", [])

    def load_catalog(self, catalog_path: str) -> dict:
        """Load a catalog file."""
        full_path = self.data_dir / catalog_path

        if full_path in self.catalogs_modified:
            return self.catalogs_modified[full_path]

        if not full_path.exists():
            raise FileNotFoundError(f"Catalog file not found: {full_path}")

        with open(full_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.catalogs_modified[full_path] = data
        return data

    def get_existing_ids(self, catalog: dict) -> set:
        """Get all existing IDs and aliases from a catalog."""
        existing = set()
        for item in catalog.get("items", []):
            existing.add(item.get("id", "").lower())
            existing.add(item.get("name", "").lower())
            for alias in item.get("aliases", []):
                existing.add(alias.lower())
        return existing

    def rebuild_clothing_index(self, catalog: dict) -> None:
        """Rebuild clothing index_by_body_part from item body_part values."""
        items = catalog.get("items", [])
        ordered_parts = [
            entry.get("id")
            for entry in catalog.get("body_part_categories", [])
            if entry.get("id")
        ]

        index: dict[str, list[str]] = {}
        for part in ordered_parts:
            ids = sorted(
                item.get("id", "")
                for item in items
                if item.get("body_part") == part and item.get("id")
            )
            if ids:
                index[part] = ids

        # Keep any unexpected body_part values instead of dropping them silently.
        extra_parts = sorted(
            {
                item.get("body_part")
                for item in items
                if item.get("body_part") and item.get("body_part") not in index
            }
        )
        for part in extra_parts:
            index[part] = sorted(
                item.get("id", "")
                for item in items
                if item.get("body_part") == part and item.get("id")
            )

        catalog["index_by_body_part"] = index

    def create_catalog_item(self, pending_item: dict) -> dict:
        """Convert a pending item to a catalog item format."""
        category = pending_item.get("corrected_category", pending_item.get("suggested_category", ""))
        target = pending_item.get("corrected_target_catalog", pending_item.get("target_catalog", ""))
        group = pending_item.get("corrected_group", pending_item.get("suggested_group", "general"))

        item = {
            "id": pending_item["id"],
            "name": pending_item["name"],
            "aliases": [],
            "name_i18n": pending_item.get("name_i18n", {
                "en": pending_item["name"],
                "zh": ""
            })
        }

        # Add category-specific fields
        if "clothing" in target:
            body_part = CATEGORY_TO_BODY_PART.get(category, "accessory")
            item["body_part"] = body_part
            item["style_group"] = group

        elif "hair" in target:
            hair_category = HAIR_CATEGORIES.get(category, "style")
            item["category"] = hair_category
            item["group"] = group

        elif "eye" in target:
            item["category"] = "color" if category == "eye_color" else "accessory"
            item["group"] = group

        elif "body" in target:
            body_category = BODY_CATEGORIES.get(category, "other")
            item["category"] = body_category
            item["group"] = group

        elif "expression" in target:
            item["category"] = "positive" if group == "positive" else "neutral"
            item["group"] = group

        elif "pose" in target:
            item["category"] = "gesture" if category == "gesture" else "pose"
            item["group"] = group

        elif "view_angle" in target:
            item["category"] = "angle"
            item["group"] = group

        elif "background" in target:
            item["category"] = "setting"
            item["group"] = group

        return item

    def merge_item(self, pending_item: dict) -> tuple[bool, str]:
        """Merge a single item into its target catalog."""
        decision = pending_item.get("review_decision")
        if decision and decision != "keep":
            return False, f"Review decision is '{decision}'"

        target = pending_item.get("corrected_target_catalog", pending_item.get("target_catalog", ""))

        if not target:
            return False, "No target catalog specified"

        try:
            catalog = self.load_catalog(target)
        except FileNotFoundError as e:
            return False, str(e)

        # Check for duplicates
        existing = self.get_existing_ids(catalog)
        if pending_item["id"].lower() in existing:
            return False, f"ID '{pending_item['id']}' already exists"
        if pending_item["name"].lower() in existing:
            return False, f"Name '{pending_item['name']}' already exists"

        # Create and add the item
        new_item = self.create_catalog_item(pending_item)
        catalog.setdefault("items", []).append(new_item)
        if "clothing" in target:
            self.rebuild_clothing_index(catalog)

        return True, f"Added to {target}"

    def save_catalogs(self):
        """Save all modified catalogs."""
        for path, data in self.catalogs_modified.items():
            # Update timestamp if present
            if "generated_utc" in data:
                data["generated_utc"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

            if not self.dry_run:
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                print(f"  Saved: {path}")
            else:
                print(f"  [DRY RUN] Would save: {path}")

    def run(self):
        """Run the merge process."""
        print("=" * 60)
        print("Catalog Merger - Import Approved Items")
        print("=" * 60)
        print()

        # Load pending items
        print(f"Loading: {self.pending_file}")
        try:
            items = self.load_pending_items()
        except FileNotFoundError as e:
            print(f"Error: {e}")
            return

        print(f"Found {len(items)} pending items")
        print()

        # Process each item
        added = 0
        skipped = 0
        errors = []

        for item in items:
            success, message = self.merge_item(item)
            if success:
                added += 1
                print(f"  + {item['name']} -> {message}")
            else:
                skipped += 1
                errors.append(f"  - {item['name']}: {message}")

        # Print errors
        if errors:
            print("\nSkipped items:")
            for error in errors[:20]:  # Limit output
                print(error)
            if len(errors) > 20:
                print(f"  ... and {len(errors) - 20} more")

        # Save modified catalogs
        if added > 0:
            print("\nSaving catalogs...")
            self.save_catalogs()

        # Summary
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print(f"Total items processed: {len(items)}")
        print(f"Added: {added}")
        print(f"Skipped: {skipped}")

        if not self.dry_run and added > 0:
            # Archive the pending file
            archive_name = f"pending_items_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            archive_path = self.pending_file.parent / "archive"
            archive_path.mkdir(exist_ok=True)

            import shutil
            shutil.move(str(self.pending_file), str(archive_path / archive_name))
            print(f"\nArchived pending file to: {archive_path / archive_name}")


def main():
    parser = argparse.ArgumentParser(
        description="Merge approved items into catalogs"
    )
    parser.add_argument(
        "--file", "-f",
        type=Path,
        default=None,
        help="Path to pending_items.json"
    )
    parser.add_argument(
        "--data-dir", "-d",
        type=Path,
        default=None,
        help="Path to prompt data directory"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview without saving files"
    )

    args = parser.parse_args()

    merger = CatalogMerger(
        pending_file=args.file,
        data_dir=args.data_dir,
        dry_run=args.dry_run
    )

    merger.run()


if __name__ == "__main__":
    main()
