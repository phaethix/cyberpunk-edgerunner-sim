""#!/usr/bin/env python3
"""Game constants and configuration.

This module contains all constant values used throughout the application,
including healing costs, color mappings, and other configuration parameters.
"""

# Paths
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
WEB_DIR = BASE_DIR / "web"

# Costs
HEAL_COST = 500
"""Cost for Trauma Team emergency extraction."""

REST_COST = 150
"""Cost for safehouse rest at the netrunner den."""

# Humanity color thresholds
HUMANITY_COLOR_ORDER: list[tuple[float, str, str]] = [
    (70.0, "#00ff88", "green"),
    (40.0, "#fbbf24", "yellow"),
    (0.0, "#ff0044", "red"),
]
"""Humanity threshold → (min_value, CSS_hex, label) for the HUD color."""
""