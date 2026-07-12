#!/usr/bin/env python3
"""Cyberpunk Edge-Runner Simulator — FastAPI web application.

A cyberpunk-themed single-page application (SPA) built with FastAPI on the
backend and vanilla JavaScript (Tailwind CSS) on the frontend.  The game
logic is ported directly from the original terminal-only version.

Usage::

    python -m server.main
    # → http://localhost:8000
"""
import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from server.api.routes import router as api_router
from server.api.routes import set_game_state
from server.config.constants import WEB_DIR
from server.models.game_state import GameState
from server.utils.template_loader import load_html_template

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("cyberpunk")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize game state on startup."""
    logger.info("Initializing game state...")
    set_game_state(GameState())
    # Render the SPA shell once at startup (game data is static) and cache it,
    # so the "/" route doesn't re-read/re-serialize on every request.
    app.state.index_html = load_html_template()
    logger.info("Server is ready — welcome to Night City, choom.")
    yield
    logger.info("Server shutting down.")


app = FastAPI(
    title="Cyberpunk: Edge-Runner Simulator",
    version="1.0.0",
    lifespan=lifespan,
)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log incoming requests and their status."""
    response = await call_next(request)
    logger.info("%s %s → %d", request.method, request.url.path, response.status_code)
    return response


# Static files
app.mount("/static", StaticFiles(directory=str(WEB_DIR)), name="static")

# API routes
app.include_router(api_router)


@app.get("/", response_class=HTMLResponse)
def root() -> HTMLResponse:
    """Serve the cached SPA page (rendered once at startup)."""
    return HTMLResponse(content=app.state.index_html)


if __name__ == "__main__":
    logger.info("Starting Cyberpunk: Edge-Runner Simulator on http://0.0.0.0:8000")
    logger.info("Press Ctrl+C to stop.")
    uvicorn.run(app, host="0.0.0.0", port=8000)
