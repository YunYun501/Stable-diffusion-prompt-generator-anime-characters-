"""
Save / Load configuration routes.
"""

import json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

router = APIRouter()

CONFIGS_DIR = Path(__file__).parent.parent.parent / "configs"
CONFIGS_DIR.mkdir(exist_ok=True)


class SaveConfigRequest(BaseModel):
    name: str
    data: Dict[str, Any]


@router.get("/configs")
async def list_configs():
    """List all saved configuration names."""
    names = [f.stem for f in CONFIGS_DIR.glob("*.json")]
    return {"configs": sorted(names)}


@router.get("/configs/{name}")
async def load_config(name: str):
    """Load a saved configuration."""
    filepath = CONFIGS_DIR / f"{name}.json"
    if not filepath.exists():
        raise HTTPException(status_code=404, detail=f"Config '{name}' not found")
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    return {"name": name, "data": data}


@router.post("/configs/{name}")
async def save_config(name: str, req: SaveConfigRequest):
    """Save a configuration."""
    filepath = CONFIGS_DIR / f"{name}.json"
    payload = {
        "name": name,
        "created_at": datetime.now().isoformat(),
        **req.data,
    }
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    return {"status": "ok", "name": name}
