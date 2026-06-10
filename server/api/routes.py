#!/usr/bin/env python3
"""API routes module.

This module contains all FastAPI route definitions for the game API.
"""
import threading
from typing import Optional

from fastapi import APIRouter, HTTPException

from ..models.game_state import GameState
from ..models.schemas import IdRequest

# Global game state instance
_game_state: Optional[GameState] = None
_lock = threading.Lock()

# Create router
router = APIRouter(prefix="/api", tags=["api"])


@router.get("/status")
def api_status() -> dict:
    """Return the current player state (money, hp, humanity, owned cyberware, etc.)."""
    with _lock:
        gs = _game_state
        if gs is None:
            raise HTTPException(status_code=503, detail="Server not ready")
        return gs.status_dict()


@router.post("/gig")
def api_gig(body: IdRequest) -> dict:
    """Execute a gig. Rolls the dice and updates state."""
    with _lock:
        gs = _game_state
        if gs is None:
            raise HTTPException(status_code=503, detail="Server not ready")
        return gs.execute_job(body.id)


@router.post("/buy")
def api_buy(body: IdRequest) -> dict:
    """Buy (install) a piece of cyberware."""
    with _lock:
        gs = _game_state
        if gs is None:
            raise HTTPException(status_code=503, detail="Server not ready")
        return gs.buy(body.id)


@router.post("/uninstall")
def api_uninstall(body: IdRequest) -> dict:
    """Uninstall (sell at 50%) a piece of cyberware."""
    with _lock:
        gs = _game_state
        if gs is None:
            raise HTTPException(status_code=503, detail="Server not ready")
        return gs.uninstall(body.id)


@router.post("/heal")
def api_heal() -> dict:
    """Call Trauma Team for emergency extraction ($500)."""
    with _lock:
        gs = _game_state
        if gs is None:
            raise HTTPException(status_code=503, detail="Server not ready")
        return gs.heal()


@router.post("/rest")
def api_rest() -> dict:
    """Rest at the safehouse ($150)."""
    with _lock:
        gs = _game_state
        if gs is None:
            raise HTTPException(status_code=503, detail="Server not ready")
        return gs.rest()


@router.post("/restart")
def api_restart() -> dict:
    """Reset the game to its initial state."""
    global _game_state
    with _lock:
        _game_state = GameState()
        return _game_state.status_dict()


def get_game_state() -> Optional[GameState]:
    """Get the current game state instance."""
    return _game_state


def set_game_state(state: GameState) -> None:
    """Set the game state instance."""
    global _game_state
    with _lock:
        _game_state = state
