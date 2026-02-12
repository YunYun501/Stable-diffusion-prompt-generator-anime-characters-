"""
Prompt generation and palette application routes.
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, List, Optional

from generator.prompt_generator import PromptGenerator

router = APIRouter()
gen = PromptGenerator()

# Canonical slot order for prompt building (matches prompt_generator.py)
SLOT_ORDER = [
    "hair_color", "hair_length", "hair_style", "hair_texture",
    "eye_color", "eye_style",
    "body_type", "height", "skin", "age_appearance", "special_features",
    "expression",
    "full_body", "head", "neck", "upper_body", "waist", "lower_body",
    "outerwear", "hands", "legs", "feet", "accessory",
    "view_angle", "pose", "gesture",
    "background",
]


class SlotState(BaseModel):
    enabled: bool = True
    value_id: Optional[str] = None
    value: Optional[str] = None
    color: Optional[str] = None
    weight: float = 1.0


class GenerateRequest(BaseModel):
    slots: Dict[str, SlotState]
    full_body_mode: bool = False
    upper_body_mode: bool = False
    output_language: str = "en"


@router.post("/generate-prompt")
async def generate_prompt(req: GenerateRequest):
    """Build the prompt string from provided slot state."""
    parts = ["1girl"]

    output_language = req.output_language
    full_body_val_id = None
    fb = req.slots.get("full_body")
    if fb and fb.enabled and (fb.value_id or fb.value):
        if fb.value_id:
            full_body_val_id = fb.value_id
        else:
            item = gen.resolve_slot_item("full_body", None, fb.value)
            full_body_val_id = item.get("id") if item else None

    lower_body_covers_legs = False
    lower = req.slots.get("lower_body")
    if lower and lower.enabled and (lower.value_id or lower.value):
        if lower.value_id:
            lower_body_covers_legs = gen.lower_body_id_covers_legs(lower.value_id)
        elif lower.value:
            item = gen.resolve_slot_item("lower_body", None, lower.value)
            lower_body_covers_legs = gen.lower_body_item_covers_legs(item)
    if req.full_body_mode and full_body_val_id:
        lower_body_covers_legs = False

    for name in SLOT_ORDER:
        slot = req.slots.get(name)
        if not slot or not slot.enabled:
            continue
        if not slot.value_id and not slot.value:
            continue

        # Skip upper/lower if full_body active
        if req.full_body_mode and name in ("upper_body", "lower_body") and full_body_val_id:
            continue
        if name == "legs" and lower_body_covers_legs:
            continue

        value_name = gen.resolve_slot_value_name(name, slot.value_id, slot.value, output_language)
        if not value_name:
            continue

        color_name = gen.localize_color_token(slot.color, output_language) if slot.color else None
        part = f"{color_name} {value_name}" if color_name else value_name

        if slot.weight != 1.0:
            part = f"({part}:{slot.weight:.1f})"

        parts.append(part)

    return {"prompt": ", ".join(parts)}


class ApplyPaletteRequest(BaseModel):
    palette_id: str
    slots: Dict[str, SlotState]
    full_body_mode: bool = False
    upper_body_mode: bool = False
    output_language: str = "en"


@router.post("/apply-palette")
async def apply_palette(req: ApplyPaletteRequest):
    """Apply palette colors to all has_color slots that have a value, then regenerate prompt."""
    new_colors = {}

    for name, defn in gen.SLOT_DEFINITIONS.items():
        if not defn.get("has_color", False):
            continue
        slot = req.slots.get(name)
        if slot and slot.enabled and (slot.value_id or slot.value):
            color = gen.sample_color_from_palette(req.palette_id)
            new_colors[name] = color
            # Update the slot for prompt generation
            if name in req.slots:
                req.slots[name].color = color

    # Regenerate prompt with new colors
    gen_req = GenerateRequest(
        slots=req.slots,
        full_body_mode=req.full_body_mode,
        upper_body_mode=req.upper_body_mode,
        output_language=req.output_language,
    )
    prompt_result = await generate_prompt(gen_req)

    return {"colors": new_colors, "prompt": prompt_result["prompt"]}


@router.get("/palettes")
async def get_palettes():
    """Return all palettes and individual colors."""
    palettes = []
    for p in gen.palettes.values():
        palettes.append({
            "id": p["id"],
            "name": p.get("name", p["id"]),
            "name_i18n": p.get("name_i18n", {"en": p.get("name", p["id"]), "zh": p.get("name", p["id"])}),
            "description_i18n": p.get("description_i18n", {"en": p.get("description", ""), "zh": p.get("description", "")}),
            "colors": p.get("colors", []),
        })
    return {
        "palettes": palettes,
        "individual_colors": gen.individual_colors,
        "individual_colors_i18n": gen.color_i18n,
    }
