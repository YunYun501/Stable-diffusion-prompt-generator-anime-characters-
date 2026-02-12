"""
Prompt Parser - Reverse-engineers a prompt string back to slot settings.
Uses cached indices for O(1) lookups.
"""

import re
from typing import Dict, List, Optional, Tuple, Any
from fastapi import APIRouter
from pydantic import BaseModel

from generator.prompt_generator import PromptGenerator

router = APIRouter()


class ColorTrie:
    """Trie for O(k) color prefix detection."""

    def __init__(self):
        self.root = {}

    def insert(self, word: str, canonical: str = None):
        """Insert a color word into the trie."""
        node = self.root
        for char in word.lower():
            node = node.setdefault(char, {})
        node["$"] = canonical or word  # Store canonical form

    def find_prefix(self, text: str) -> Optional[Tuple[str, int]]:
        """
        Find longest color prefix in O(k) time.
        Returns (canonical_color, prefix_length) or None.
        """
        node = self.root
        last_match = None
        text_lower = text.lower()

        for i, char in enumerate(text_lower):
            if char not in node:
                break
            node = node[char]
            if "$" in node:
                # Check if next char is space (word boundary)
                if i + 1 < len(text) and text[i + 1] == " ":
                    last_match = (node["$"], i + 2)  # +2 to skip space

        return last_match


class PromptParser:
    """
    Parses prompt strings back to slot settings.
    Indices are built once and cached for fast lookups.
    """

    _instance = None

    def __init__(self, generator: PromptGenerator):
        self.generator = generator

        # Indices for fast lookup
        self.exact_index: Dict[str, List[Tuple[str, str]]] = {}  # name -> [(slot, id)]
        self.normalized_index: Dict[str, List[Tuple[str, str]]] = {}  # normalized -> [(slot, id)]
        self.word_index: Dict[str, List[Tuple[str, str, str]]] = {}  # word -> [(slot, id, full_name)]
        self.color_trie = ColorTrie()
        self.color_canonical: Dict[str, str] = {}  # localized -> canonical

        self._build_indices()

    @classmethod
    def get_instance(cls, generator: PromptGenerator) -> "PromptParser":
        """Get or create singleton instance."""
        if cls._instance is None:
            cls._instance = cls(generator)
        return cls._instance

    @classmethod
    def reset_instance(cls):
        """Reset singleton (for testing or reload)."""
        cls._instance = None

    def _normalize(self, text: str) -> str:
        """Normalize text by removing spaces, hyphens, underscores."""
        return re.sub(r'[\s\-_]+', '', text.lower())

    def _build_indices(self):
        """Build all lookup indices from catalog data."""
        # Build item indices
        for slot_name, slot_def in self.generator.SLOT_DEFINITIONS.items():
            options = self.generator.get_slot_options(slot_name)

            for item in options:
                item_id = item.get("id", "")
                if not item_id:
                    continue

                # Index English name
                name = item.get("name", "")
                if name:
                    self._index_name(name, slot_name, item_id)

                # Index localized names
                name_i18n = item.get("name_i18n", {})
                for lang, localized in name_i18n.items():
                    if localized and localized != name:
                        self._index_name(localized, slot_name, item_id)

        # Build color indices
        for color in self.generator.individual_colors:
            self.color_trie.insert(color, color)
            self.color_canonical[color.lower()] = color

        # Index localized color names
        for color, i18n in self.generator.color_i18n.items():
            for lang, localized in i18n.items():
                if localized:
                    self.color_trie.insert(localized, color)
                    self.color_canonical[localized.lower()] = color

    def _index_name(self, name: str, slot_name: str, item_id: str):
        """Add a name to all relevant indices."""
        name_lower = name.lower().strip()
        if not name_lower:
            return

        # Exact index
        self.exact_index.setdefault(name_lower, []).append((slot_name, item_id))

        # Normalized index
        normalized = self._normalize(name_lower)
        if normalized != name_lower:
            self.normalized_index.setdefault(normalized, []).append((slot_name, item_id))

        # Word index (for partial matching)
        words = name_lower.split()
        if len(words) > 1:
            for word in words:
                if len(word) > 2:  # Skip very short words
                    self.word_index.setdefault(word, []).append((slot_name, item_id, name_lower))

    def _tokenize(self, prompt: str) -> List[Dict[str, Any]]:
        """
        Split prompt into tokens, handling weight syntax.
        Returns list of {"text": str, "weight": float}
        """
        tokens = []

        for part in prompt.split(","):
            part = part.strip()
            if not part:
                continue

            weight = 1.0

            # Handle weight syntax: (item:1.3) or (item:0.8)
            if part.startswith("(") and part.endswith(")") and ":" in part:
                inner = part[1:-1]
                # Find last colon (weight is always at end)
                last_colon = inner.rfind(":")
                if last_colon > 0:
                    item_part = inner[:last_colon]
                    weight_part = inner[last_colon + 1:]
                    try:
                        weight = float(weight_part)
                        part = item_part
                    except ValueError:
                        pass

            tokens.append({"text": part, "weight": weight})

        return tokens

    def _extract_color(self, text: str) -> Tuple[Optional[str], str]:
        """
        Extract color prefix from text.
        Returns (canonical_color, remaining_text) or (None, original_text).
        """
        result = self.color_trie.find_prefix(text)
        if result:
            color, prefix_len = result
            return color, text[prefix_len:].strip()
        return None, text

    def _match_exact(self, text: str) -> Optional[List[Tuple[str, str]]]:
        """Try exact match. O(1)."""
        return self.exact_index.get(text.lower())

    def _match_normalized(self, text: str) -> Optional[List[Tuple[str, str]]]:
        """Try normalized match. O(1)."""
        normalized = self._normalize(text)
        return self.normalized_index.get(normalized)

    def _match_words(self, text: str) -> Optional[List[Tuple[str, str]]]:
        """Try word-based partial match. O(w) where w = words in text."""
        words = text.lower().split()

        # Find candidates that contain all words
        candidates = None
        for word in words:
            if len(word) <= 2:
                continue
            word_matches = self.word_index.get(word, [])
            if candidates is None:
                candidates = set((slot, id) for slot, id, _ in word_matches)
            else:
                candidates &= set((slot, id) for slot, id, _ in word_matches)

        if candidates:
            return list(candidates)
        return None

    def _match_fuzzy(self, text: str, threshold: float = 0.85) -> Optional[Tuple[List[Tuple[str, str]], float]]:
        """
        Fuzzy match using sequence matching. O(n) - use sparingly.
        Returns (matches, confidence) or None.
        """
        from difflib import SequenceMatcher

        text_lower = text.lower()
        best_matches = None
        best_score = 0

        for name, matches in self.exact_index.items():
            score = SequenceMatcher(None, text_lower, name).ratio()
            if score > best_score and score >= threshold:
                best_score = score
                best_matches = matches

        if best_matches:
            return best_matches, best_score
        return None

    def parse(self, prompt: str, use_fuzzy: bool = True) -> Dict[str, Any]:
        """
        Parse a prompt string into slot settings.

        Returns:
            {
                "slots": {slot_name: {"value_id", "color", "weight", "enabled"}},
                "unmatched": [tokens that couldn't be matched],
                "confidence": float (0-1)
            }
        """
        tokens = self._tokenize(prompt)
        results: Dict[str, Dict] = {}
        unmatched: List[str] = []
        matched_count = 0

        # Skip tokens
        skip_tokens = {"1girl", "1boy", "girl", "boy", "solo"}

        for token in tokens:
            text = token["text"]
            weight = token["weight"]

            # Skip base prompt tokens
            if text.lower() in skip_tokens:
                continue

            # Try to extract color prefix
            color, item_text = self._extract_color(text)

            # Try matching strategies in order of speed
            matches = None
            confidence = 1.0

            # 1. Exact match - O(1)
            matches = self._match_exact(item_text)

            # 2. Normalized match - O(1)
            if not matches:
                matches = self._match_normalized(item_text)
                confidence = 0.95

            # 3. Word-based match - O(w)
            if not matches:
                matches = self._match_words(item_text)
                confidence = 0.85

            # 4. Fuzzy match - O(n), only if enabled
            if not matches and use_fuzzy and len(item_text) > 3:
                fuzzy_result = self._match_fuzzy(item_text)
                if fuzzy_result:
                    matches, confidence = fuzzy_result

            # Assign to first unassigned slot
            if matches:
                assigned = False
                for slot_name, item_id in matches:
                    if slot_name not in results:
                        # Check if this slot should have a color
                        slot_def = self.generator.SLOT_DEFINITIONS.get(slot_name, {})
                        has_color = slot_def.get("has_color", False)

                        results[slot_name] = {
                            "value_id": item_id,
                            "color": color if has_color else None,
                            "weight": weight,
                            "enabled": True,
                            "confidence": confidence
                        }
                        assigned = True
                        matched_count += 1
                        break

                if not assigned:
                    # All matching slots already filled
                    unmatched.append(text)
            else:
                unmatched.append(text)

        total = matched_count + len(unmatched)
        overall_confidence = matched_count / total if total > 0 else 0

        return {
            "slots": results,
            "unmatched": unmatched,
            "matched_count": matched_count,
            "total_tokens": total,
            "confidence": round(overall_confidence, 3)
        }


# Global parser instance
_parser: Optional[PromptParser] = None


def get_parser() -> PromptParser:
    """Get or create the global parser instance."""
    global _parser
    if _parser is None:
        gen = PromptGenerator()
        _parser = PromptParser.get_instance(gen)
    return _parser


# API Models
class ParsePromptRequest(BaseModel):
    prompt: str
    use_fuzzy: bool = True


class ParsePromptResponse(BaseModel):
    slots: Dict[str, Any]
    unmatched: List[str]
    matched_count: int
    total_tokens: int
    confidence: float


@router.post("/parse-prompt", response_model=ParsePromptResponse)
async def parse_prompt(req: ParsePromptRequest):
    """
    Parse a prompt string back into slot settings.

    Returns matched slots with their values, colors, and weights,
    plus any unmatched tokens and overall confidence score.
    """
    parser = get_parser()
    result = parser.parse(req.prompt, use_fuzzy=req.use_fuzzy)
    return result
