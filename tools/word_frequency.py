#!/usr/bin/env python3
"""
Word Frequency Analyzer

Counts how many times each individual word appears across all tags.
Example output: hair,15000 | eyes,8000 | dress,5000

Usage:
    python tools/word_frequency.py
    python tools/word_frequency.py --output word_counts.csv
"""

import argparse
import csv
import re
from collections import Counter
from pathlib import Path


def extract_words(text: str) -> list[str]:
    """Extract individual words from text, cleaning special characters."""
    # Replace underscores with spaces
    text = text.replace("_", " ")
    # Remove special characters, keep only letters and spaces
    text = re.sub(r"[^a-zA-Z\s]", " ", text)
    # Split into words and filter empty
    words = [w.strip().lower() for w in text.split() if w.strip()]
    # Filter very short words (1-2 chars) that are usually noise
    words = [w for w in words if len(w) >= 3]
    return words


def analyze_word_frequency(input_dir: Path, output_file: Path):
    """Analyze word frequency across all CSV files."""
    word_counts = Counter()

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
                    if len(parts) >= 1:
                        # Extract words from English tag
                        english_tag = parts[0]
                        words = extract_words(english_tag)
                        word_counts.update(words)

        except Exception as e:
            print(f"  Warning: Error reading {csv_file.name}: {e}")

    # Sort by frequency descending
    sorted_words = word_counts.most_common()

    # Write CSV
    with open(output_file, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Word", "Frequency"])
        for word, count in sorted_words:
            writer.writerow([word, count])

    print(f"\nSaved word frequency to: {output_file}")
    print(f"Total unique words: {len(sorted_words)}")

    # Show top 30
    print("\nTop 30 most frequent words:")
    print("-" * 40)
    for i, (word, count) in enumerate(sorted_words[:30], 1):
        print(f"{i:3}. {word:<20} {count:>6}")


def main():
    parser = argparse.ArgumentParser(
        description="Analyze word frequencies from tag CSV files"
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
        help="Output CSV file (default: word_frequency.csv)"
    )

    args = parser.parse_args()

    # Set defaults
    project_dir = Path(__file__).parent.parent
    input_dir = args.input or project_dir / "All tags" / "All tags raw"
    output_file = args.output or project_dir / "word_frequency.csv"

    if not input_dir.exists():
        print(f"Error: Input directory not found: {input_dir}")
        return

    print("=" * 50)
    print("Word Frequency Analyzer")
    print("=" * 50)
    print(f"Input directory: {input_dir}")
    print(f"Output file: {output_file}")
    print()

    analyze_word_frequency(input_dir, output_file)


if __name__ == "__main__":
    main()
