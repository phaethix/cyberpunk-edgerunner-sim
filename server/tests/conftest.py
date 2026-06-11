#!/usr/bin/env python3
"""Pytest configuration for server tests."""

from unittest.mock import patch, MagicMock

import pytest

from server.models.game_state import GameState


@pytest.fixture
def fresh_game():
    """Return a fresh GameState instance with default values."""
    return GameState()


@pytest.fixture(autouse=True)
def _patch_random():
    """Deterministic random: always returns the first value of a predictable sequence.

    Each call to ``random.randint(a, b)`` returns ``a`` (the lowest value),
    and ``random.choice(seq)`` returns ``seq[0]``.  This makes all tests
    deterministic without requiring explicit ``monkeypatch`` calls.
    """
    mock_randint = MagicMock(side_effect=lambda a, b: a)
    mock_choice = MagicMock(side_effect=lambda seq: seq[0])
    with patch("server.models.game_state.random.randint", mock_randint):
        with patch("server.models.game_state.random.choice", mock_choice):
            yield
