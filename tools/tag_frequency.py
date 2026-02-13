#!/usr/bin/env python3
"""
Tag Frequency Analyzer

Analyzes all CSV files in "All tags raw" folder and creates a frequency table.
Handles both English and Chinese tags, removes underscores.

Usage:
    python tools/tag_frequency.py
    python tools/tag_frequency.py --output my_frequency.csv
"""

import argparse
import csv
from collections import Counter
from pathlib import Path


def clean_tag(tag: str) -> str:
    """Clean a tag by replacing underscores with spaces and stripping whitespace."""
    return tag.replace("_", " ").strip()


def analyze_tags(input_dir: Path) -> tuple[Counter, Counter]:
    """
    Analyze all CSV files and count tag frequencies.

    Returns:
        Tuple of (english_counts, chinese_counts)
    """
    english_counts = Counter()
    chinese_counts = Counter()

    csv_files = sorted(input_dir.glob("*.csv"))
    print(f"Found {len(csv_files)} CSV files to analyze")

    for csv_file in csv_files:
        try:
            with open(csv_file, "r", encoding="utf-8-sig") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue

                    # Parse CSV line: tag,number,chinese
                    parts = line.split(",")
                    if len(parts) >= 1:
                        english_tag = clean_tag(parts[0])
                        if english_tag:
                            english_counts[english_tag] += 1

                    if len(parts) >= 3:
                        chinese_tag = clean_tag(parts[2])
                        if chinese_tag:
                            chinese_counts[chinese_tag] += 1

        except Exception as e:
            print(f"  Warning: Error reading {csv_file.name}: {e}")

    return english_counts, chinese_counts


def save_frequency_table(
    english_counts: Counter,
    chinese_counts: Counter,
    output_file: Path
):
    """Save combined frequency table as CSV."""

    # Combine all unique tags with their frequencies
    all_english = set(english_counts.keys())

    # Create rows sorted by frequency (highest first)
    rows = []
    for tag in all_english:
        eng_freq = english_counts.get(tag, 0)
        # Try to find matching Chinese translation
        rows.append({
            "english_tag": tag,
            "frequency": eng_freq
        })

    # Sort by frequency descending
    rows.sort(key=lambda x: x["frequency"], reverse=True)

    # Write CSV
    with open(output_file, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["english_tag", "frequency"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nSaved frequency table to: {output_file}")
    print(f"Total unique tags: {len(rows)}")


def save_detailed_frequency_table(
    input_dir: Path,
    output_file: Path
):
    """
    Save detailed tag table with both English and Chinese.
    Preserves the original pairing and category number from the source files.
    Cleans underscores from tags.
    """
    # Store all tags: list of (english, category_num, chinese)
    all_tags = []

    csv_files = sorted(input_dir.glob("*.csv"))
    print(f"Found {len(csv_files)} CSV files to analyze")

    for csv_file in csv_files:
        try:
            with open(csv_file, "r", encoding="utf-8-sig") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue

                    parts = line.split(",")
                    if len(parts) >= 3:
                        english_tag = clean_tag(parts[0])
                        try:
                            category_num = int(parts[1])
                        except ValueError:
                            category_num = 0
                        chinese_tag = clean_tag(parts[2])

                        if english_tag:
                            all_tags.append({
                                "english": english_tag,
                                "category": category_num,
                                "chinese": chinese_tag
                            })

        except Exception as e:
            print(f"  Warning: Error reading {csv_file.name}: {e}")

    # Sort alphabetically by english tag
    sorted_tags = sorted(all_tags, key=lambda x: x["english"].lower())

    # Write CSV (just English and Chinese, no category)
    with open(output_file, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["English Tag", "Chinese Tag"])
        for item in sorted_tags:
            writer.writerow([item["english"], item["chinese"]])

    print(f"\nSaved tag table to: {output_file}")
    print(f"Total tags: {len(sorted_tags)}")

    # Show sample
    print("\nSample tags (first 20):")
    print("-" * 50)
    for i, item in enumerate(sorted_tags[:20], 1):
        try:
            print(f"{i:3}. {item['english']:<30} | {item['chinese']}")
        except UnicodeEncodeError:
            print(f"{i:3}. {item['english']:<30} | (Chinese)")


def main():
    parser = argparse.ArgumentParser(
        description="Analyze tag frequencies from CSV files"
    )
    parser.add_argument(
        "--input", "-i",
        type=Path,
        default=None,
        help="Input directory containing CSV files (default: All tags raw)"
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=None,
        help="Output CSV file (default: tag_frequency.csv)"
    )

    args = parser.parse_args()

    # Set defaults
    project_dir = Path(__file__).parent.parent
    input_dir = args.input or project_dir / "All tags" / "All tags raw"
    output_file = args.output or project_dir / "tag_frequency.csv"

    if not input_dir.exists():
        print(f"Error: Input directory not found: {input_dir}")
        return

    print("=" * 60)
    print("Tag Frequency Analyzer")
    print("=" * 60)
    print(f"Input directory: {input_dir}")
    print(f"Output file: {output_file}")
    print()

    save_detailed_frequency_table(input_dir, output_file)


if __name__ == "__main__":
    main()
