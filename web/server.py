"""
FastAPI server for Random Character Prompt Generator.
Mounts static files and includes all API route modules.
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

from .routes import slots, prompt, configs

STATIC_DIR = Path(__file__).parent / "static"

app = FastAPI(title="Character Prompt Generator")

# Mount static assets
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Include route modules
app.include_router(slots.router, prefix="/api")
app.include_router(prompt.router, prefix="/api")
app.include_router(configs.router, prefix="/api")


@app.get("/")
async def index():
    """Serve the main HTML page."""
    return FileResponse(str(STATIC_DIR / "index.html"))
