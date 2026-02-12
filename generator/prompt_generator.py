"""
Core prompt generator logic for Random Character Prompt Generator.
Handles loading catalogs, random sampling, color palettes, and prompt building.
"""

import json
import random
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, Dict, List, Any
from datetime import datetime


@dataclass
class SlotConfig:
    """Configuration for a single slot (e.g., upper_body, hair_color)."""
    enabled: bool = True
    locked: bool = False  # If locked, won't be changed by "Randomize All"
    value: Optional[str] = None  # Current selected item name
    value_id: Optional[str] = None  # Current selected item ID
    color: Optional[str] = None  # Color modifier (if applicable)
    color_enabled: bool = False  # Whether to include color in output
    weight: float = 1.0  # Prompt weight (1.0 = default, no weight syntax)
    
    def to_dict(self) -> dict:
        return {
            "enabled": self.enabled,
            "locked": self.locked,
            "value": self.value,
            "value_id": self.value_id,
            "color": self.color,
            "color_enabled": self.color_enabled,
            "weight": self.weight
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "SlotConfig":
        return cls(**data)


@dataclass 
class GeneratorConfig:
    """Overall generator configuration."""
    # Slot configurations by slot name
    slots: Dict[str, SlotConfig] = field(default_factory=dict)
    
    # Color mode: "none", "palette", "random"
    color_mode: str = "none"
    active_palette_id: Optional[str] = None
    
    # Full body mode toggle
    full_body_mode: bool = True  # When True, full_body disables upper/lower
    
    # Metadata
    name: str = "Untitled"
    created_at: Optional[str] = None
    
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "created_at": self.created_at or datetime.now().isoformat(),
            "color_mode": self.color_mode,
            "active_palette_id": self.active_palette_id,
            "full_body_mode": self.full_body_mode,
            "slots": {k: v.to_dict() for k, v in self.slots.items()}
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "GeneratorConfig":
        config = cls(
            name=data.get("name", "Untitled"),
            created_at=data.get("created_at"),
            color_mode=data.get("color_mode", "none"),
            active_palette_id=data.get("active_palette_id"),
            full_body_mode=data.get("full_body_mode", True)
        )
        for slot_name, slot_data in data.get("slots", {}).items():
            config.slots[slot_name] = SlotConfig.from_dict(slot_data)
        return config


class PromptGenerator:
    """Main prompt generator class."""
    DEFAULT_DATA_DIRNAME = "prompt data"
    SUPPORTED_LANGUAGES = ("en", "zh")
    
    # Define all available slots and their categories
    SLOT_DEFINITIONS = {
        # Appearance
        "hair_style": {"category": "appearance", "catalog": "hair", "index_key": "style", "has_color": False},
        "hair_length": {"category": "appearance", "catalog": "hair", "index_key": "length", "has_color": False},
        "hair_color": {"category": "appearance", "catalog": "hair", "index_key": "color", "has_color": False},
        "hair_texture": {"category": "appearance", "catalog": "hair", "index_key": "texture", "has_color": False},
        "eye_color": {"category": "appearance", "catalog": "eyes", "index_key": "color", "has_color": False},
        "eye_expression_quality": {"category": "appearance", "catalog": "eyes", "index_key": "expression_quality", "has_color": False},
        "eye_shape": {"category": "appearance", "catalog": "eyes", "index_key": "eye_shape", "has_color": False},
        "eye_pupil_state": {"category": "appearance", "catalog": "eyes", "index_key": "pupil_state", "has_color": False},
        "eye_state": {"category": "appearance", "catalog": "eyes", "index_key": "eye_state", "has_color": False},
        "eye_accessories": {"category": "appearance", "catalog": "eyes", "index_key": "eye_accessories", "has_color": False},
        
        # Body
        "body_type": {"category": "body", "catalog": "body", "index_key": "body_type", "has_color": False},
        "height": {"category": "body", "catalog": "body", "index_key": "height", "has_color": False},
        "skin": {"category": "body", "catalog": "body", "index_key": "skin", "has_color": False},
        "age_appearance": {"category": "body", "catalog": "body", "index_key": "age_appearance", "has_color": False},
        "special_features": {"category": "body", "catalog": "body", "index_key": "special_features", "has_color": False},
        
        # Expression
        "expression": {"category": "expression", "catalog": "expressions", "index_key": None, "has_color": False},
        
        # Clothing
        "head": {"category": "clothing", "catalog": "clothing", "index_key": "head", "has_color": True},
        "neck": {"category": "clothing", "catalog": "clothing", "index_key": "neck", "has_color": True},
        "upper_body": {"category": "clothing", "catalog": "clothing", "index_key": "upper_body", "has_color": True},
        "waist": {"category": "clothing", "catalog": "clothing", "index_key": "waist", "has_color": True},
        "lower_body": {"category": "clothing", "catalog": "clothing", "index_key": "lower_body", "has_color": True},
        "full_body": {"category": "clothing", "catalog": "clothing", "index_key": "full_body", "has_color": True},
        "outerwear": {"category": "clothing", "catalog": "clothing", "index_key": "outerwear", "has_color": True},
        "hands": {"category": "clothing", "catalog": "clothing", "index_key": "hands", "has_color": True},
        "legs": {"category": "clothing", "catalog": "clothing", "index_key": "legs", "has_color": True},
        "feet": {"category": "clothing", "catalog": "clothing", "index_key": "feet", "has_color": True},
        "accessory": {"category": "clothing", "catalog": "clothing", "index_key": "accessory", "has_color": True},
        
        # Pose
        "pose": {"category": "pose", "catalog": "poses", "index_key": None, "has_color": False},
        "gesture": {"category": "pose", "catalog": "poses", "index_key": "gesture", "has_color": False},
        "view_angle": {"category": "pose", "catalog": "view_angles", "index_key": None, "has_color": False},
        
        # Background
        "background": {"category": "background", "catalog": "backgrounds", "index_key": None, "has_color": False},
    }
    
    # Categories for section-based randomization
    CATEGORIES = ["appearance", "body", "expression", "clothing", "pose", "background"]
    
    def __init__(self, data_dir: Optional[Path] = None):
        """Initialize the generator with data directory."""
        if data_dir is None:
            # Default to catalog root under project root.
            data_dir = Path(__file__).parent.parent / self.DEFAULT_DATA_DIRNAME
        self.data_dir = Path(data_dir)
        
        # Loaded catalogs
        self.catalogs: Dict[str, dict] = {}
        
        # Color palettes
        self.palettes: Dict[str, dict] = {}
        self.individual_colors: List[str] = []
        
        # Item lookup maps (catalog -> id -> item)
        self.items_by_id: Dict[str, Dict[str, dict]] = {}
        # Reverse lookup maps (catalog -> lower(name) -> id)
        self.item_id_by_name: Dict[str, Dict[str, str]] = {}
        # Color token localization map (color -> {lang: localized_text})
        self.color_i18n: Dict[str, Dict[str, str]] = {}
        
        # Load all data
        self._load_catalogs()
    
    def _load_catalogs(self):
        """Load all catalog JSON files."""
        catalog_paths = {
            "clothing": self.data_dir / "clothing" / "clothing_list.json",
            "expressions": self.data_dir / "expressions" / "female_expressions.json",
            "hair": self.data_dir / "hair" / "hair_catalog.json",
            "eyes": self.data_dir / "eyes" / "eye_catalog.json",
            "body": self.data_dir / "body" / "body_features.json",
            "poses": self.data_dir / "poses" / "poses.json",
            "view_angles": self.data_dir / "view_angles" / "view_angles.json",
            "backgrounds": self.data_dir / "backgrounds" / "backgrounds.json",
            "colors": self.data_dir / "colors" / "color_palettes.json",
        }
        
        for name, path in catalog_paths.items():
            if path.exists():
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.catalogs[name] = data
                    
                    # Build item lookup
                    if "items" in data:
                        self.items_by_id[name] = {
                            item["id"]: item for item in data["items"]
                        }
                        self.item_id_by_name[name] = {}
                        for item in data["items"]:
                            label = item.get("name")
                            if isinstance(label, str) and label:
                                self.item_id_by_name[name][label.strip().lower()] = item["id"]
                    
                    # Special handling for colors
                    if name == "colors":
                        self.palettes = {
                            p["id"]: p for p in data.get("palettes", [])
                        }
                        self.individual_colors = data.get("individual_colors", [])
                        self.color_i18n = data.get("individual_colors_i18n", {})

    @classmethod
    def normalize_language(cls, language: Optional[str]) -> str:
        """Normalize incoming locale code to supported language."""
        code = (language or "en").strip().lower()
        if code.startswith("zh"):
            return "zh"
        return "en"

    def get_item_localized_name(self, item: dict, language: str = "en") -> str:
        """Return localized display text for an item, with safe fallback."""
        lang = self.normalize_language(language)
        names = item.get("name_i18n")
        if isinstance(names, dict):
            localized = names.get(lang) or names.get("en")
            if isinstance(localized, str) and localized.strip():
                return localized
        return item.get("name", item.get("id", ""))

    def get_palette_localized_name(self, palette: dict, language: str = "en") -> str:
        """Return localized palette name with fallback."""
        lang = self.normalize_language(language)
        names = palette.get("name_i18n")
        if isinstance(names, dict):
            localized = names.get(lang) or names.get("en")
            if isinstance(localized, str) and localized.strip():
                return localized
        return palette.get("name", palette.get("id", ""))

    def get_palette_localized_description(self, palette: dict, language: str = "en") -> str:
        """Return localized palette description with fallback."""
        lang = self.normalize_language(language)
        descriptions = palette.get("description_i18n")
        if isinstance(descriptions, dict):
            localized = descriptions.get(lang) or descriptions.get("en")
            if isinstance(localized, str) and localized.strip():
                return localized
        return palette.get("description", "")

    def localize_color_token(self, color_token: Optional[str], language: str = "en") -> Optional[str]:
        """Convert a canonical color token to localized display/output text."""
        if not color_token:
            return None
        lang = self.normalize_language(language)
        names = self.color_i18n.get(color_token)
        if isinstance(names, dict):
            localized = names.get(lang) or names.get("en")
            if isinstance(localized, str) and localized.strip():
                return localized
        return color_token

    def get_slot_item_by_id(self, slot_name: str, item_id: Optional[str]) -> Optional[dict]:
        """Resolve slot item dict by slot name + item id."""
        if not item_id or slot_name not in self.SLOT_DEFINITIONS:
            return None
        catalog_name = self.SLOT_DEFINITIONS[slot_name]["catalog"]
        return self.items_by_id.get(catalog_name, {}).get(item_id)

    def resolve_slot_item(self, slot_name: str, value_id: Optional[str], value_name: Optional[str]) -> Optional[dict]:
        """
        Resolve a slot item from either canonical id or legacy display name.
        Supports backward compatibility for old saved configs.
        """
        if slot_name not in self.SLOT_DEFINITIONS:
            return None
        catalog_name = self.SLOT_DEFINITIONS[slot_name]["catalog"]
        items_map = self.items_by_id.get(catalog_name, {})

        if value_id and value_id in items_map:
            return items_map[value_id]

        if value_name:
            name_key = value_name.strip().lower()
            mapped_id = self.item_id_by_name.get(catalog_name, {}).get(name_key)
            if mapped_id and mapped_id in items_map:
                return items_map[mapped_id]
        return None

    def resolve_slot_value_name(
        self,
        slot_name: str,
        value_id: Optional[str],
        value_name: Optional[str] = None,
        language: str = "en",
    ) -> Optional[str]:
        """Resolve localized slot text for a selected value id/name."""
        item = self.resolve_slot_item(slot_name, value_id, value_name)
        if not item:
            return None
        return self.get_item_localized_name(item, language)
    
    def get_slot_options(self, slot_name: str) -> List[dict]:
        """Get all available options for a slot."""
        if slot_name not in self.SLOT_DEFINITIONS:
            return []
        
        slot_def = self.SLOT_DEFINITIONS[slot_name]
        catalog_name = slot_def["catalog"]
        index_key = slot_def["index_key"]
        
        if catalog_name not in self.catalogs:
            return []
        
        catalog = self.catalogs[catalog_name]
        
        # Handle expressions (uses index_by_emotion_family)
        if catalog_name == "expressions":
            return catalog.get("items", [])
        
        # Handle poses/backgrounds (may have multiple indices)
        if index_key is None:
            items = catalog.get("items", [])
            # Keep pose slot focused on body poses; hand actions live in gesture slot.
            if catalog_name == "poses" and slot_name == "pose":
                return [item for item in items if item.get("category") != "gesture"]
            return items
        
        # Handle clothing (uses index_by_body_part)
        if catalog_name == "clothing":
            index = catalog.get("index_by_body_part", {})
            item_ids = index.get(index_key, [])
            items_map = self.items_by_id.get(catalog_name, {})
            return [items_map[id] for id in item_ids if id in items_map]
        
        # Handle other catalogs (hair, eyes, body) - uses index_by_category
        index = catalog.get("index_by_category", {})
        item_ids = index.get(index_key, [])
        items_map = self.items_by_id.get(catalog_name, {})
        return [items_map[id] for id in item_ids if id in items_map]

    def get_slot_options_localized(self, slot_name: str, language: str = "en") -> List[dict]:
        """Get options for a slot with localized names embedded."""
        options = self.get_slot_options(slot_name)
        lang = self.normalize_language(language)
        slot_def = self.SLOT_DEFINITIONS.get(slot_name, {})
        catalog_name = slot_def.get("catalog")
        catalog = self.catalogs.get(catalog_name, {})
        # Optional catalog-level map for grouping labels.
        catalog_group_i18n = {}
        for key in ("style_groups_i18n", "ui_groups_i18n", "emotion_family_i18n", "group_i18n"):
            maybe_map = catalog.get(key)
            if isinstance(maybe_map, dict):
                catalog_group_i18n = maybe_map
                break

        result: List[dict] = []
        for item in options:
            names = item.get("name_i18n", {})
            localized = names.get(lang) if isinstance(names, dict) else None
            group = (
                item.get("style_group")
                or item.get("ui_group")
                or item.get("group")
                or item.get("emotion_family")
                or item.get("category")
            )
            if not isinstance(group, str) or not group.strip():
                group = None

            group_i18n = {}
            for key in ("style_group_i18n", "ui_group_i18n", "group_i18n"):
                maybe_map = item.get(key)
                if isinstance(maybe_map, dict):
                    group_i18n = maybe_map
                    break
            if not group_i18n and group:
                maybe_map = catalog_group_i18n.get(group)
                if isinstance(maybe_map, dict):
                    group_i18n = maybe_map

            localized_group = None
            if group:
                localized_group = (
                    group_i18n.get(lang)
                    if isinstance(group_i18n, dict)
                    else None
                ) or (
                    group_i18n.get("en")
                    if isinstance(group_i18n, dict)
                    else None
                ) or group

            result.append(
                {
                    "id": item.get("id", ""),
                    "name": item.get("name", item.get("id", "")),
                    "name_i18n": names if isinstance(names, dict) else {"en": item.get("name", ""), "zh": item.get("name", "")},
                    "localized_name": localized or item.get("name", item.get("id", "")),
                    "group": group,
                    "group_i18n": group_i18n,
                    "localized_group": localized_group,
                }
            )
        return result
    
    def get_slot_option_names(self, slot_name: str) -> List[str]:
        """Get list of option names for dropdown display."""
        options = self.get_slot_options(slot_name)
        return [opt.get("name", opt.get("id", "")) for opt in options]

    def get_lower_body_covers_legs_by_name(self) -> Dict[str, bool]:
        """
        Return a map of lower_body item name -> whether it covers legs.
        Missing flag defaults to False for backward compatibility.
        """
        mapping: Dict[str, bool] = {}
        for item in self.get_slot_options("lower_body"):
            name = item.get("name")
            if not name:
                continue
            mapping[name] = bool(item.get("covers_legs", False))
        return mapping

    def get_lower_body_covers_legs_by_id(self) -> Dict[str, bool]:
        """Return a map of lower_body item id -> whether it covers legs."""
        mapping: Dict[str, bool] = {}
        for item in self.get_slot_options("lower_body"):
            item_id = item.get("id")
            if not item_id:
                continue
            mapping[item_id] = bool(item.get("covers_legs", False))
        return mapping

    def get_pose_uses_hands_by_name(self) -> Dict[str, bool]:
        """
        Return a map of pose item name -> whether it uses hands.
        Missing flag defaults to False for backward compatibility.
        """
        mapping: Dict[str, bool] = {}
        for item in self.get_slot_options("pose"):
            name = item.get("name")
            if not name:
                continue
            mapping[name] = bool(item.get("uses_hands", False))
        return mapping

    def get_pose_uses_hands_by_id(self) -> Dict[str, bool]:
        """Return a map of pose item id -> whether it uses hands."""
        mapping: Dict[str, bool] = {}
        for item in self.get_slot_options("pose"):
            item_id = item.get("id")
            if not item_id:
                continue
            mapping[item_id] = bool(item.get("uses_hands", False))
        return mapping

    def lower_body_item_covers_legs(self, item: Optional[dict]) -> bool:
        """Check coverage flag on a sampled lower_body item dict."""
        if not item:
            return False
        return bool(item.get("covers_legs", False))

    def lower_body_value_covers_legs(self, value: Optional[str]) -> bool:
        """Check whether a selected lower_body display value covers legs."""
        if not value:
            return False
        mapping = self.get_lower_body_covers_legs_by_name()
        return bool(mapping.get(value, False))

    def lower_body_id_covers_legs(self, item_id: Optional[str]) -> bool:
        """Check whether a lower_body item id covers legs."""
        if not item_id:
            return False
        item = self.get_slot_item_by_id("lower_body", item_id)
        return bool(item and item.get("covers_legs", False))
    
    def sample_slot(self, slot_name: str) -> Optional[dict]:
        """Randomly sample an item for a slot."""
        options = self.get_slot_options(slot_name)
        if not options:
            return None
        return random.choice(options)
    
    def get_palette_list(self) -> List[dict]:
        """Get list of available palettes."""
        return list(self.palettes.values())
    
    def get_palette_names(self) -> List[str]:
        """Get palette names for dropdown."""
        return [p.get("name", p.get("id", "")) for p in self.palettes.values()]
    
    def sample_color_from_palette(self, palette_id: str) -> Optional[str]:
        """Sample a random color from a palette."""
        if palette_id not in self.palettes:
            return None
        palette = self.palettes[palette_id]
        colors = palette.get("colors", [])
        if not colors:
            return None
        return random.choice(colors)
    
    def sample_random_color(self) -> Optional[str]:
        """Sample a completely random color."""
        if not self.individual_colors:
            # Fallback basic colors
            basic = ["white", "black", "red", "blue", "pink", "purple", "green", "yellow"]
            return random.choice(basic)
        return random.choice(self.individual_colors)
    
    def get_colors_for_palette(self, palette_id: str) -> List[str]:
        """Get all colors in a palette."""
        if palette_id not in self.palettes:
            return []
        return self.palettes[palette_id].get("colors", [])
    
    def create_default_config(self) -> GeneratorConfig:
        """Create a default configuration with all slots."""
        config = GeneratorConfig()
        for slot_name in self.SLOT_DEFINITIONS:
            config.slots[slot_name] = SlotConfig()
        return config
    
    def randomize_slot(self, config: GeneratorConfig, slot_name: str, 
                       include_color: bool = False, palette_id: Optional[str] = None) -> None:
        """Randomize a single slot in the config."""
        if slot_name not in config.slots:
            config.slots[slot_name] = SlotConfig()
        
        slot = config.slots[slot_name]
        if slot.locked:
            return
        
        item = self.sample_slot(slot_name)
        if item:
            slot.value = item.get("name", "")
            slot.value_id = item.get("id", "")
        else:
            slot.value = None
            slot.value_id = None
        
        # Handle color
        if include_color and self.SLOT_DEFINITIONS[slot_name].get("has_color", False):
            if palette_id and palette_id in self.palettes:
                slot.color = self.sample_color_from_palette(palette_id)
                slot.color_enabled = True
            elif config.color_mode == "random":
                slot.color = self.sample_random_color()
                slot.color_enabled = True
    
    def randomize_category(self, config: GeneratorConfig, category: str,
                          include_color: bool = False, palette_id: Optional[str] = None) -> None:
        """Randomize all slots in a category."""
        for slot_name, slot_def in self.SLOT_DEFINITIONS.items():
            if slot_def["category"] == category:
                self.randomize_slot(config, slot_name, include_color, palette_id)
    
    def randomize_all(self, config: GeneratorConfig, 
                      include_color: bool = False, palette_id: Optional[str] = None) -> None:
        """Randomize all non-locked slots."""
        for slot_name in self.SLOT_DEFINITIONS:
            if slot_name in config.slots and config.slots[slot_name].locked:
                continue
            self.randomize_slot(config, slot_name, include_color, palette_id)
        
        # Handle full_body logic
        if config.full_body_mode:
            self._apply_full_body_logic(config)
        self._apply_lower_body_leg_logic(config)
    
    def _apply_full_body_logic(self, config: GeneratorConfig) -> None:
        """Apply full_body override logic - if full_body is set, clear upper/lower."""
        full_body_slot = config.slots.get("full_body")
        if full_body_slot and full_body_slot.enabled and full_body_slot.value:
            # Clear upper_body and lower_body (but don't disable - user can override)
            for slot_name in ["upper_body", "lower_body"]:
                if slot_name in config.slots and not config.slots[slot_name].locked:
                    config.slots[slot_name].value = None
                    config.slots[slot_name].value_id = None

    def _apply_lower_body_leg_logic(self, config: GeneratorConfig) -> None:
        """
        If lower_body is an item that covers legs, clear legs slot value.
        """
        lower = config.slots.get("lower_body")
        legs = config.slots.get("legs")
        if not lower or not legs:
            return
        if not lower.enabled or not lower.value:
            return
        if self.lower_body_value_covers_legs(lower.value):
            legs.value = None
            legs.value_id = None
    
    def build_prompt(self, config: GeneratorConfig) -> str:
        """Build the final prompt string from configuration."""
        parts = []
        
        # Always start with "1girl"
        parts.append("1girl")
        
        # Define slot order for prompt building
        slot_order = [
            # Appearance first
            "hair_color", "hair_length", "hair_style", "hair_texture",
            "eye_color", "eye_expression_quality", "eye_shape", "eye_pupil_state",
            "eye_state", "eye_accessories",
            # Body features
            "body_type", "height", "skin", "age_appearance", "special_features",
            # Expression
            "expression",
            # Clothing (specific order)
            "full_body", "head", "neck", "upper_body", "waist", "lower_body",
            "outerwear", "hands", "legs", "feet", "accessory",
            # Pose
            "view_angle", "pose", "gesture",
            # Background
            "background"
        ]

        lower_body_covers_legs = False
        lower_body_slot = config.slots.get("lower_body")
        if lower_body_slot and lower_body_slot.enabled and lower_body_slot.value:
            lower_body_covers_legs = self.lower_body_value_covers_legs(lower_body_slot.value)
        
        for slot_name in slot_order:
            if slot_name not in config.slots:
                continue
            
            slot = config.slots[slot_name]
            if not slot.enabled or not slot.value:
                continue
            
            # Skip upper/lower body if full_body is active (unless they have values set)
            if config.full_body_mode and slot_name in ["upper_body", "lower_body"]:
                full_body_slot = config.slots.get("full_body")
                if full_body_slot and full_body_slot.enabled and full_body_slot.value:
                    # Skip if not explicitly overridden
                    continue

            # If lower body covers legs, skip legs slot to avoid overlap.
            if slot_name == "legs" and lower_body_covers_legs:
                continue
            
            # Build the prompt part
            prompt_part = ""
            
            # Add color if enabled
            if slot.color_enabled and slot.color:
                prompt_part = f"{slot.color} {slot.value}"
            else:
                prompt_part = slot.value
            
            # Add weight if not default
            if slot.weight != 1.0:
                prompt_part = f"({prompt_part}:{slot.weight:.1f})"
            
            parts.append(prompt_part)
        
        return ", ".join(parts)
    
    def save_config(self, config: GeneratorConfig, filepath: Path) -> None:
        """Save configuration to a JSON file."""
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(config.to_dict(), f, indent=2, ensure_ascii=False)
    
    def load_config(self, filepath: Path) -> GeneratorConfig:
        """Load configuration from a JSON file."""
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        return GeneratorConfig.from_dict(data)
    
    def list_saved_configs(self, configs_dir: Optional[Path] = None) -> List[str]:
        """List all saved configuration files."""
        if configs_dir is None:
            configs_dir = self.data_dir / "configs"
        
        if not configs_dir.exists():
            return []
        
        return [f.stem for f in configs_dir.glob("*.json")]
    
    def get_slots_by_category(self, category: str) -> List[str]:
        """Get all slot names for a category."""
        return [
            name for name, defn in self.SLOT_DEFINITIONS.items()
            if defn["category"] == category
        ]
