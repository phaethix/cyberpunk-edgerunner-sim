#!/usr/bin/env python3
"""Pydantic schemas for request/response validation.

This module contains all Pydantic models used for API input validation
and response serialization.
"""
from typing import Optional, Union

from pydantic import BaseModel


class IdRequest(BaseModel):
    """Request body containing a single identifier."""
    id: str


class GameStateResponse(BaseModel):
    """Response schema for game state."""
    money: int
    hp: int
    humanity: float
    combat_bonus: int
    owned: list[dict[str, str]]
    day: int
    game_over: bool
    game_over_reason: str
    humanity_color: str
    hp_color: str


class JobResult(BaseModel):
    """Schema for job execution result details."""
    success: bool
    job_name: str
    reward: Optional[int] = None
    humanity_cost: Optional[int] = None
    loss: Optional[int] = None
    hp_cost: Optional[int] = None
    roll: int
    effective_diff: int
    success_chance: int
    description: str
    risk_level: str


class ApiResponse(BaseModel):
    """Generic API response schema."""
    success: bool
    message: str
    state: Optional[GameStateResponse] = None
    job_result: Optional[JobResult] = None
