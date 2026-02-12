"""
ComfyUI node implementation for Random Character Prompt Generator.
"""

import random
from pathlib import Path
from .prompt_generator import PromptGenerator


class RandomCharacterPromptNode:
    """
    Generates random anime character prompts for Stable Diffusion.
    Outputs a STRING that can be previewed, edited, then connected to CLIP Text Encode.
    """

    def __init__(self):
        self.gen = None
        self._palette_list = None

    def _ensure_generator(self):
        """Lazy-load the generator to avoid slow startup."""
        if self.gen is None:
            self.gen = PromptGenerator()
            self._palette_list = ["none"] + [p["id"] for p in self.gen.get_palette_list()]

    @classmethod
    def INPUT_TYPES(cls):
        """Define node inputs."""
        # We need to instantiate temporarily to get palette list
        temp_gen = PromptGenerator()
        palette_ids = ["none"] + [p["id"] for p in temp_gen.get_palette_list()]

        return {
            "required": {
                "seed": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 0xffffffffffffffff,
                    "tooltip": "Random seed for reproducible results. Use 'control after generate: randomize' for new character each run."
                }),
                "language": (["en", "zh"], {
                    "default": "en",
                    "tooltip": "Output language for prompt text"
                }),
                "palette": (palette_ids, {
                    "default": "none",
                    "tooltip": "Color palette for clothing items"
                }),
                "full_body_mode": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "When enabled with full_body outfit, skips upper/lower body"
                }),
                "upper_body_mode": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "Skip lower body, legs, feet slots"
                }),
            },
            "optional": {
                "prefix": ("STRING", {
                    "default": "",
                    "multiline": True,
                    "tooltip": "Text to prepend to generated prompt (e.g., quality tags)"
                }),
                # Hair locks
                "lock_hair_style": ("STRING", {"default": "", "tooltip": "Lock hair style (e.g., 'ponytail', 'twintails')"}),
                "lock_hair_length": ("STRING", {"default": "", "tooltip": "Lock hair length (e.g., 'long hair', 'short hair')"}),
                "lock_hair_color": ("STRING", {"default": "", "tooltip": "Lock hair color (e.g., 'blonde hair', 'pink hair')"}),
                "lock_hair_texture": ("STRING", {"default": "", "tooltip": "Lock hair texture (e.g., 'wavy hair', 'straight hair')"}),
                # Eye locks
                "lock_eye_color": ("STRING", {"default": "", "tooltip": "Lock eye color (e.g., 'blue eyes', 'red eyes')"}),
                "lock_eye_expression_quality": ("STRING", {"default": "", "tooltip": "Lock eye expression/quality"}),
                "lock_eye_shape": ("STRING", {"default": "", "tooltip": "Lock eye shape"}),
                "lock_eye_pupil_state": ("STRING", {"default": "", "tooltip": "Lock pupil state"}),
                "lock_eye_state": ("STRING", {"default": "", "tooltip": "Lock eye state"}),
                "lock_eye_accessories": ("STRING", {"default": "", "tooltip": "Lock eye accessories (e.g., 'glasses')"}),
                # Body locks
                "lock_body_type": ("STRING", {"default": "", "tooltip": "Lock body type (e.g., 'slim', 'petite')"}),
                "lock_height": ("STRING", {"default": "", "tooltip": "Lock height (e.g., 'tall', 'short')"}),
                "lock_skin": ("STRING", {"default": "", "tooltip": "Lock skin (e.g., 'pale skin', 'tan')"}),
                "lock_age_appearance": ("STRING", {"default": "", "tooltip": "Lock age appearance"}),
                "lock_special_features": ("STRING", {"default": "", "tooltip": "Lock special features (e.g., 'elf ears', 'horns')"}),
                # Expression
                "lock_expression": ("STRING", {"default": "", "tooltip": "Lock expression (e.g., 'smile', 'serious')"}),
                # Clothing locks
                "lock_head": ("STRING", {"default": "", "tooltip": "Lock head item (e.g., 'hair ribbon', 'crown')"}),
                "lock_neck": ("STRING", {"default": "", "tooltip": "Lock neck item (e.g., 'choker', 'scarf')"}),
                "lock_upper_body": ("STRING", {"default": "", "tooltip": "Lock upper body (e.g., 'shirt', 'blouse')"}),
                "lock_waist": ("STRING", {"default": "", "tooltip": "Lock waist item (e.g., 'belt', 'sash')"}),
                "lock_lower_body": ("STRING", {"default": "", "tooltip": "Lock lower body (e.g., 'skirt', 'pants')"}),
                "lock_full_body": ("STRING", {"default": "", "tooltip": "Lock full body outfit (e.g., 'dress', 'jumpsuit')"}),
                "lock_outerwear": ("STRING", {"default": "", "tooltip": "Lock outerwear (e.g., 'jacket', 'coat')"}),
                "lock_hands": ("STRING", {"default": "", "tooltip": "Lock hands item (e.g., 'gloves', 'bracelet')"}),
                "lock_legs": ("STRING", {"default": "", "tooltip": "Lock legs item (e.g., 'thighhighs', 'stockings')"}),
                "lock_feet": ("STRING", {"default": "", "tooltip": "Lock feet item (e.g., 'boots', 'heels')"}),
                "lock_accessory": ("STRING", {"default": "", "tooltip": "Lock accessory (e.g., 'bag', 'weapon')"}),
                # Pose locks
                "lock_pose": ("STRING", {"default": "", "tooltip": "Lock pose (e.g., 'standing', 'sitting')"}),
                "lock_gesture": ("STRING", {"default": "", "tooltip": "Lock gesture/hand action (e.g., 'peace sign', 'hand on hip')"}),
                "lock_view_angle": ("STRING", {"default": "", "tooltip": "Lock view angle (e.g., 'from above', 'from side')"}),
                # Background
                "lock_background": ("STRING", {"default": "", "tooltip": "Lock background (e.g., 'outdoor', 'bedroom')"}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("prompt",)
    FUNCTION = "generate"
    CATEGORY = "prompt"
    OUTPUT_NODE = True  # Allows showing output in node

    def generate(self, seed, language, palette, full_body_mode, upper_body_mode,
                 prefix="",
                 lock_hair_style="", lock_hair_length="", lock_hair_color="", lock_hair_texture="",
                 lock_eye_color="", lock_eye_expression_quality="", lock_eye_shape="",
                 lock_eye_pupil_state="", lock_eye_state="", lock_eye_accessories="",
                 lock_body_type="", lock_height="", lock_skin="", lock_age_appearance="", lock_special_features="",
                 lock_expression="",
                 lock_head="", lock_neck="", lock_upper_body="", lock_waist="", lock_lower_body="",
                 lock_full_body="", lock_outerwear="", lock_hands="", lock_legs="", lock_feet="", lock_accessory="",
                 lock_pose="", lock_gesture="", lock_view_angle="",
                 lock_background=""):
        """Generate a random character prompt and encode it with CLIP."""
        self._ensure_generator()

        # Set random seed for reproducibility
        random.seed(seed)

        # Create config and randomize
        config = self.gen.create_default_config()
        config.full_body_mode = full_body_mode

        # Determine palette
        palette_id = palette if palette != "none" else None
        include_color = palette_id is not None

        # Randomize all slots
        self.gen.randomize_all(config, include_color=include_color, palette_id=palette_id)

        # Apply upper body mode (disable lower body slots)
        if upper_body_mode:
            for slot_name in ["waist", "lower_body", "full_body", "legs", "feet"]:
                if slot_name in config.slots:
                    config.slots[slot_name].enabled = False

        # Apply all locks (override randomized values)
        locks = {
            # Hair
            "hair_style": lock_hair_style,
            "hair_length": lock_hair_length,
            "hair_color": lock_hair_color,
            "hair_texture": lock_hair_texture,
            # Eyes
            "eye_color": lock_eye_color,
            "eye_expression_quality": lock_eye_expression_quality,
            "eye_shape": lock_eye_shape,
            "eye_pupil_state": lock_eye_pupil_state,
            "eye_state": lock_eye_state,
            "eye_accessories": lock_eye_accessories,
            # Body
            "body_type": lock_body_type,
            "height": lock_height,
            "skin": lock_skin,
            "age_appearance": lock_age_appearance,
            "special_features": lock_special_features,
            # Expression
            "expression": lock_expression,
            # Clothing
            "head": lock_head,
            "neck": lock_neck,
            "upper_body": lock_upper_body,
            "waist": lock_waist,
            "lower_body": lock_lower_body,
            "full_body": lock_full_body,
            "outerwear": lock_outerwear,
            "hands": lock_hands,
            "legs": lock_legs,
            "feet": lock_feet,
            "accessory": lock_accessory,
            # Pose
            "pose": lock_pose,
            "gesture": lock_gesture,
            "view_angle": lock_view_angle,
            # Background
            "background": lock_background,
        }

        for slot_name, locked_value in locks.items():
            if locked_value and locked_value.strip():
                if slot_name in config.slots:
                    config.slots[slot_name].value = locked_value.strip()
                    config.slots[slot_name].value_id = locked_value.strip()

        # Build the prompt with localization
        prompt = self._build_prompt_localized(config, language)

        # Add prefix if provided
        if prefix and prefix.strip():
            prompt = f"{prefix.strip()}, {prompt}"

        # Return prompt and display it on the node
        return {"ui": {"text": [prompt]}, "result": (prompt,)}

    def _build_prompt_localized(self, config, language: str) -> str:
        """Build prompt with localized item names."""
        parts = ["1girl"]

        slot_order = [
            "hair_color", "hair_length", "hair_style", "hair_texture",
            "eye_color", "eye_expression_quality", "eye_shape", "eye_pupil_state",
            "eye_state", "eye_accessories",
            "body_type", "height", "skin", "age_appearance", "special_features",
            "expression",
            "full_body", "head", "neck", "upper_body", "waist", "lower_body",
            "outerwear", "hands", "legs", "feet", "accessory",
            "view_angle", "pose", "gesture",
            "background"
        ]

        # Check if lower body covers legs
        lower_body_covers_legs = False
        lower_slot = config.slots.get("lower_body")
        if lower_slot and lower_slot.enabled and lower_slot.value_id:
            lower_body_covers_legs = self.gen.lower_body_id_covers_legs(lower_slot.value_id)

        for slot_name in slot_order:
            if slot_name not in config.slots:
                continue

            slot = config.slots[slot_name]
            if not slot.enabled or not slot.value_id:
                continue

            # Full body mode logic
            if config.full_body_mode and slot_name in ["upper_body", "lower_body"]:
                full_body_slot = config.slots.get("full_body")
                if full_body_slot and full_body_slot.enabled and full_body_slot.value_id:
                    continue

            # Skip legs if lower body covers them
            if slot_name == "legs" and lower_body_covers_legs:
                continue

            # Get localized name
            localized_name = self.gen.resolve_slot_value_name(
                slot_name, slot.value_id, slot.value, language
            )
            if not localized_name:
                localized_name = slot.value or slot.value_id

            # Build prompt part with optional color
            if slot.color_enabled and slot.color:
                color_text = self.gen.localize_color_token(slot.color, language) or slot.color
                prompt_part = f"{color_text} {localized_name}"
            else:
                prompt_part = localized_name

            # Apply weight
            if slot.weight != 1.0:
                prompt_part = f"({prompt_part}:{slot.weight:.1f})"

            parts.append(prompt_part)

        return ", ".join(parts)
