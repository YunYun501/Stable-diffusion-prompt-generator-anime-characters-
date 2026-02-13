"""
Clean tags by removing color mentions from English tags.

This helps with frequency analysis on base item types:
- blue_eyes, red_eyes, green_eyes → eyes
- blonde_hair, pink_hair, black_hair → hair
- white_shirt, black_shirt → shirt
"""

import csv
from pathlib import Path

# Colors to remove from tags
COLORS = {
    "red", "blue", "green", "yellow", "orange", "purple", "pink",
    "white", "black", "grey", "gray", "brown", "blonde", "silver",
    "gold", "golden", "aqua", "cyan", "magenta", "teal", "violet",
    "scarlet", "crimson", "azure", "indigo", "beige", "tan",
    "light", "dark", "pale", "bright", "multicolored", "two-tone"
}


def clean_tag(tag: str) -> str:
    """Remove color words from a tag and clean underscores."""
    # Split by underscore
    parts = tag.split("_")

    # Filter out color words
    cleaned_parts = [p for p in parts if p.lower() not in COLORS]

    # If all parts were colors, keep the original
    if not cleaned_parts:
        return tag.replace("_", " ")

    # Join with spaces
    return " ".join(cleaned_parts)


def main():
    # Paths
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    input_file = project_root / "All tags" / "Original_all_tags.csv"
    output_file = project_root / "All tags" / "Cleaned_all_tags.csv"

    # Read and clean
    cleaned_rows = []

    with open(input_file, "r", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) >= 3:
                english_tag = row[0]
                chinese_tag = row[2]

                cleaned_english = clean_tag(english_tag)
                cleaned_rows.append([cleaned_english, chinese_tag])

    # Write output
    with open(output_file, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["English Tag", "Chinese Tag"])
        writer.writerows(cleaned_rows)

    print(f"Cleaned {len(cleaned_rows)} tags")
    print(f"Output: {output_file}")

    # Show some examples
    print("\nExamples:")
    examples = [
        ("blue_eyes", clean_tag("blue_eyes")),
        ("blonde_hair", clean_tag("blonde_hair")),
        ("white_shirt", clean_tag("white_shirt")),
        ("long_hair", clean_tag("long_hair")),
        ("dark_skin", clean_tag("dark_skin")),
    ]
    for orig, cleaned in examples:
        print(f"  {orig} -> {cleaned}")


if __name__ == "__main__":
    main()
