"""
FastAPI server for Random Character Prompt Generator.
Mounts static files and includes all API route modules.
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware
from pathlib import Path

from .routes import slots, prompt, configs, parser

STATIC_DIR = Path(__file__).parent / "static"

app = FastAPI(title="Character Prompt Generator")


class NoCacheStaticMiddleware(BaseHTTPMiddleware):
    """Disable caching for static JS/CSS during development."""
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        if request.url.path.startswith("/static/"):
            response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        return response


app.add_middleware(NoCacheStaticMiddleware)

# Mount static assets
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Include route modules
app.include_router(slots.router, prefix="/api")
app.include_router(prompt.router, prefix="/api")
app.include_router(configs.router, prefix="/api")
app.include_router(parser.router, prefix="/api")


@app.get("/")
async def index():
    """Serve the main HTML page."""
    return FileResponse(str(STATIC_DIR / "index.html"))
