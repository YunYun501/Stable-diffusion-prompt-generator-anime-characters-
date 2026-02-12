"""
Slot-related API routes: definitions, options, randomization.
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, List, Optional

from generator.prompt_generator import PromptGenerator

router = APIRouter()
gen = PromptGenerator()

# Section layout sent to frontend so it can build the UI dynamically
SECTION_LAYOUT = {
    "appearance": {
        "label": "Appearance",
        "label_key": "section_appearance",
        "icon": "\U0001f464",
        "slots": [
            "hair_style", "hair_length", "hair_color", "hair_texture",
            "eye_color", "eye_expression_quality", "eye_shape", "eye_pupil_state",
            "eye_state", "eye_accessories",
        ],
        "columns": [
            ["hair_style", "hair_length", "hair_color", "hair_texture"],
            ["eye_color", "eye_expression_quality", "eye_shape", "eye_pupil_state", "eye_state", "eye_accessories"],
        ],
        "column_label_keys": ["section_appearance_hair", "section_appearance_eyes"],
    },
    "body": {
        "label": "Body / Expression / Pose",
        "label_key": "section_body",
        "icon": "\U0001f9cd",
        "slots": ["body_type", "height", "skin", "age_appearance",
                  "special_features", "expression", "view_angle", "pose", "gesture"],
    },
    "clothing": {
        "label": "Clothing & Background",
        "label_key": "section_clothing",
        "icon": "\U0001f457",
        "slots": ["head", "neck", "upper_body", "waist", "lower_body",
                  "full_body", "outerwear", "hands", "legs", "feet",
                  "accessory", "background"],
        "columns": [
            ["head", "neck", "upper_body", "waist", "lower_body", "full_body"],
            ["outerwear", "hands", "legs", "feet", "accessory", "background"],
        ],
    },
}


@router.get("/slots")
async def get_slots():
    """Return slot definitions, per-slot options, and section layout."""
    slots = {}
    for name, defn in gen.SLOT_DEFINITIONS.items():
        full_options = gen.get_slot_options_localized(name)
        slots[name] = {
            "category": defn["category"],
            "has_color": defn.get("has_color", False),
            "options": full_options,
        }
    return {
        "slots": slots,
        "sections": SECTION_LAYOUT,
        "lower_body_covers_legs_by_id": gen.get_lower_body_covers_legs_by_id(),
        "pose_uses_hands_by_id": gen.get_pose_uses_hands_by_id(),
    }


class RandomizeRequest(BaseModel):
    slot_names: List[str]
    locked: Dict[str, bool] = {}
    palette_enabled: bool = True
    palette_id: Optional[str] = None
    full_body_mode: bool = False
    upper_body_mode: bool = False
    current_values: Dict[str, Optional[str]] = {}


@router.post("/randomize")
async def randomize_slots(req: RandomizeRequest):
    """Randomize specific slots. Returns {slot_name: {value_id, value, color}}."""
    results = {}
    full_body_value_id = req.current_values.get("full_body")

    for name in req.slot_names:
        if name not in gen.SLOT_DEFINITIONS:
            continue
        if req.locked.get(name, False):
            continue

        item = gen.sample_slot(name)
        value_id = item.get("id") if item else None
        value = item.get("name") if item else None

        if name == "full_body":
            full_body_value_id = value_id

        # Full-body override
        if (req.full_body_mode and name in ("upper_body", "lower_body")
                and full_body_value_id):
            value_id = None
            value = None

        color = None
        if gen.SLOT_DEFINITIONS[name].get("has_color", False):
            if req.palette_enabled and req.palette_id:
                color = gen.sample_color_from_palette(req.palette_id)

        results[name] = {"value_id": value_id, "value": value, "color": color}

    return {"results": results}


class RandomizeAllRequest(BaseModel):
    locked: Dict[str, bool] = {}
    palette_enabled: bool = True
    palette_id: Optional[str] = None
    full_body_mode: bool = False
    upper_body_mode: bool = False


@router.post("/randomize-all")
async def randomize_all(req: RandomizeAllRequest):
    """Randomize every non-locked slot. Returns full state."""
    results = {}
    full_body_value_id = None

    for name in gen.SLOT_DEFINITIONS:
        if req.locked.get(name, False):
            continue

        item = gen.sample_slot(name)
        value_id = item.get("id") if item else None
        value = item.get("name") if item else None

        if name == "full_body":
            full_body_value_id = value_id

        color = None
        if gen.SLOT_DEFINITIONS[name].get("has_color", False):
            if req.palette_enabled and req.palette_id:
                color = gen.sample_color_from_palette(req.palette_id)

        results[name] = {"value_id": value_id, "value": value, "color": color}

    # Apply full-body override
    if req.full_body_mode and full_body_value_id:
        for name in ("upper_body", "lower_body"):
            if name in results and not req.locked.get(name, False):
                results[name]["value_id"] = None
                results[name]["value"] = None

    return {"results": results}
