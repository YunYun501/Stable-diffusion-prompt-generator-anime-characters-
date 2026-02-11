"""
Slot-related API routes: definitions, options, randomization.
"""

import random
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
        "icon": "\U0001f464",
        "slots": ["hair_style", "hair_length", "hair_color", "hair_texture",
                  "eye_color", "eye_style"],
    },
    "body": {
        "label": "Body / Expression / Pose",
        "icon": "\U0001f9cd",
        "slots": ["body_type", "height", "skin", "age_appearance",
                  "special_features", "expression", "pose", "gesture"],
    },
    "clothing": {
        "label": "Clothing & Background",
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
        options = gen.get_slot_option_names(name)
        slots[name] = {
            "category": defn["category"],
            "has_color": defn.get("has_color", False),
            "options": options,
        }
    return {"slots": slots, "sections": SECTION_LAYOUT}


class RandomizeRequest(BaseModel):
    slot_names: List[str]
    locked: Dict[str, bool] = {}
    color_mode: str = "none"           # "none" | "palette" | "random"
    palette_id: Optional[str] = None
    full_body_mode: bool = True
    current_values: Dict[str, Optional[str]] = {}


@router.post("/randomize")
async def randomize_slots(req: RandomizeRequest):
    """Randomize specific slots. Returns {slot_name: {value, color}}."""
    results = {}
    full_body_value = req.current_values.get("full_body")

    for name in req.slot_names:
        if name not in gen.SLOT_DEFINITIONS:
            continue
        if req.locked.get(name, False):
            continue

        item = gen.sample_slot(name)
        value = item.get("name") if item else None

        if name == "full_body":
            full_body_value = value

        # Full-body override
        if (req.full_body_mode and name in ("upper_body", "lower_body")
                and full_body_value):
            value = None

        color = None
        if gen.SLOT_DEFINITIONS[name].get("has_color", False):
            if req.color_mode == "palette" and req.palette_id:
                color = gen.sample_color_from_palette(req.palette_id)
            elif req.color_mode == "random":
                color = gen.sample_random_color()

        results[name] = {"value": value, "color": color}

    return {"results": results}


class RandomizeAllRequest(BaseModel):
    locked: Dict[str, bool] = {}
    color_mode: str = "none"
    palette_id: Optional[str] = None
    full_body_mode: bool = True


@router.post("/randomize-all")
async def randomize_all(req: RandomizeAllRequest):
    """Randomize every non-locked slot. Returns full state."""
    results = {}
    full_body_value = None

    for name in gen.SLOT_DEFINITIONS:
        if req.locked.get(name, False):
            continue

        item = gen.sample_slot(name)
        value = item.get("name") if item else None

        if name == "full_body":
            full_body_value = value

        color = None
        if gen.SLOT_DEFINITIONS[name].get("has_color", False):
            if req.color_mode == "palette" and req.palette_id:
                color = gen.sample_color_from_palette(req.palette_id)
            elif req.color_mode == "random":
                color = gen.sample_random_color()

        results[name] = {"value": value, "color": color}

    # Apply full-body override
    if req.full_body_mode and full_body_value:
        for name in ("upper_body", "lower_body"):
            if name in results and not req.locked.get(name, False):
                results[name]["value"] = None

    return {"results": results}
