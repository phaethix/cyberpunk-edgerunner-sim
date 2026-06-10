#!/usr/bin/env python3
"""Utility helper functions.

This module contains various helper functions used throughout the application.
"""
from ..config.constants import HUMANITY_COLOR_ORDER


def clamp(lo: int, hi: int, val: int) -> int:
    """Return *val* clamped to the inclusive range [lo, hi]."""
    return max(lo, min(hi, val))


def humanity_color_css(h: float) -> str:
    """Return the CSS hex color for a given humanity value.

    Colours: green (>70), yellow (>40), red (<=40).
    """
    for threshold, color, _ in HUMANITY_COLOR_ORDER:
        if h > threshold:
            return color
    return HUMANITY_COLOR_ORDER[-1][1]
