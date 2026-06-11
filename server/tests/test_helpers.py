#!/usr/bin/env python3
"""Tests for server.utils.helpers."""

import pytest

from server.utils.helpers import clamp, humanity_color_css


class TestClamp:
    """Tests for the clamp() function."""

    def test_below_range(self):
        assert clamp(0, 100, -5) == 0

    def test_above_range(self):
        assert clamp(0, 100, 200) == 100

    def test_inside_range(self):
        assert clamp(0, 100, 50) == 50

    def test_at_boundaries(self):
        assert clamp(0, 100, 0) == 0
        assert clamp(0, 100, 100) == 100

    def test_equal_bounds(self):
        assert clamp(10, 10, 5) == 10
        assert clamp(10, 10, 15) == 10


class TestHumanityColorCss:
    """Tests for the humanity_color_css() function.

    Returns CSS hex colours based on thresholds in HUMANITY_COLOR_ORDER:
    - > 70  → #00ff88 (green)
    - > 40  → #fbbf24 (yellow)
    - <= 40 → #ff0044 (red)
    """

    def test_high_humanity(self):
        """Humanity > 70 → green hex."""
        assert humanity_color_css(100.0) == "#00ff88"
        assert humanity_color_css(71) == "#00ff88"

    def test_boundary_70(self):
        """Humanity == 70 → yellow (not > 70)."""
        assert humanity_color_css(70) == "#fbbf24"

    def test_mid_humanity(self):
        """Humanity in (40, 70] → yellow."""
        assert humanity_color_css(41) == "#fbbf24"
        assert humanity_color_css(55) == "#fbbf24"

    def test_boundary_40(self):
        """Humanity == 40 → red (not > 40)."""
        assert humanity_color_css(40) == "#ff0044"

    def test_low_humanity(self):
        """Humanity < 40 → red."""
        assert humanity_color_css(0) == "#ff0044"
        assert humanity_color_css(25) == "#ff0044"
