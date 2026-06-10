#!/usr/bin/env python3
"""Cyberpunk Edge-Runner Simulator — FastAPI web application.

A cyberpunk-themed single-page application (SPA) built with FastAPI on the
backend and vanilla JavaScript (Tailwind CSS) on the frontend.  The game
logic is ported directly from the original terminal-only version.

Usage::

    python -m server.main
    # → http://localhost:8000
"""
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from server.api.routes import router as api_router, set_game_state
from server.config.constants import WEB_DIR
from server.models.game_state import GameState
from server.utils.template_loader import load_html_template


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize game state on startup."""
    set_game_state(GameState())
    yield


app = FastAPI(
    title="Cyberpunk: Edge-Runner Simulator",
    version="1.0.0",
    lifespan=lifespan,
)

# Static files
app.mount("/static", StaticFiles(directory=str(WEB_DIR)), name="static")

# API routes
app.include_router(api_router)


@app.get("/", response_class=HTMLResponse)
def root() -> HTMLResponse:
    """Serve the main SPA page with game data injected inline."""
    return HTMLResponse(content=load_html_template())


if __name__ == "__main__":
    print("Starting Cyberpunk: Edge-Runner Simulator on http://0.0.0.0:8000")
    print("Press Ctrl+C to stop.")
    uvicorn.run(app, host="0.0.0.0", port=8000)
