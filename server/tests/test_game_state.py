#!/usr/bin/env python3
"""Tests for server.models.game_state.GameState."""

from unittest.mock import patch

import pytest

from server.models.game_state import GameState


# ── reset / status_dict ──────────────────────────────────────────────


class TestReset:
    """Tests for GameState.reset()."""

    def test_initial_money(self, fresh_game: GameState) -> None:
        assert fresh_game.money == 1000

    def test_initial_hp(self, fresh_game: GameState) -> None:
        assert fresh_game.hp == 100

    def test_initial_humanity(self, fresh_game: GameState) -> None:
        assert fresh_game.humanity == 100.0

    def test_initial_combat_bonus(self, fresh_game: GameState) -> None:
        assert fresh_game.combat_bonus == 0

    def test_initial_owned(self, fresh_game: GameState) -> None:
        assert fresh_game.owned == []

    def test_initial_day(self, fresh_game: GameState) -> None:
        assert fresh_game.day == 1

    def test_initial_game_over(self, fresh_game: GameState) -> None:
        assert fresh_game._game_over is False
        assert fresh_game._game_over_reason == ""


class TestStatusDict:
    """Tests for GameState.status_dict()."""

    def test_returns_all_keys(self, fresh_game: GameState) -> None:
        keys = {"money", "hp", "humanity", "combat_bonus", "owned",
                "day", "game_over", "game_over_reason",
                "humanity_color", "hp_color"}
        assert set(fresh_game.status_dict().keys()) == keys

    def test_values_match_state(self, fresh_game: GameState) -> None:
        d = fresh_game.status_dict()
        assert d["money"] == 1000
        assert d["hp"] == 100
        assert d["humanity"] == 100.0
        assert d["combat_bonus"] == 0
        assert d["owned"] == []
        assert d["day"] == 1
        assert d["game_over"] is False
        assert d["game_over_reason"] == ""

    def test_colors_initial(self, fresh_game: GameState) -> None:
        d = fresh_game.status_dict()
        assert d["humanity_color"] == "#00ff88"   # green hex
        assert d["hp_color"] == "green"

    def test_hp_color_yellow(self, fresh_game: GameState) -> None:
        fresh_game.hp = 50
        assert fresh_game.status_dict()["hp_color"] == "yellow"

    def test_hp_color_red(self, fresh_game: GameState) -> None:
        fresh_game.hp = 20
        assert fresh_game.status_dict()["hp_color"] == "red"

    def test_owned_serialised_as_dicts(self, fresh_game: GameState) -> None:
        fresh_game.buy("optic_zoom")
        owned = fresh_game.status_dict()["owned"]
        assert owned == [{"id": "optic_zoom", "name": "Optical Zoom Implants"}]


# ── buy ──────────────────────────────────────────────────────────────

# Real values from server/config/data.py:
#   optic_zoom:    price=800, combat_bonus=5
#   chrome_skull:  price=4000, combat_bonus=25
#
# Cyberpsychosis cost formula:
#   base_cost = max(1, price // 300)
#   cost = random.randint(max(1, base_cost - 2), base_cost + 2)
# With mock (always returns lower bound):
#   optic_zoom:    base_cost=2, cost=randint(1, 4)=1
#   chrome_skull:  base_cost=13, cost=randint(11, 15)=11


class TestBuy:
    """Tests for GameState.buy()."""

    def test_buy_success(self, fresh_game: GameState) -> None:
        result = fresh_game.buy("optic_zoom")
        assert result["success"] is True
        assert fresh_game.money == 200             # 1000 - 800
        assert fresh_game.combat_bonus == 5
        assert ("optic_zoom", "Optical Zoom Implants") in fresh_game.owned

    def test_buy_unknown_uid(self, fresh_game: GameState) -> None:
        result = fresh_game.buy("nonexistent")
        assert result["success"] is False
        assert "Unknown cyberware" in result["message"]
        assert fresh_game.money == 1000            # unchanged

    def test_buy_already_owned(self, fresh_game: GameState) -> None:
        fresh_game.buy("optic_zoom")
        result = fresh_game.buy("optic_zoom")
        assert result["success"] is False
        assert "already have" in result["message"]

    def test_buy_insufficient_funds(self, fresh_game: GameState) -> None:
        # chrome_skull costs 4000
        result = fresh_game.buy("chrome_skull")
        assert result["success"] is False
        assert "Not enough eddies" in result["message"]

    def test_buy_reduces_humanity(self, fresh_game: GameState) -> None:
        before = fresh_game.humanity
        fresh_game.buy("optic_zoom")
        # base_cost=2, cost=randint(1, 4)=1
        assert fresh_game.humanity == before - 1

    def test_buy_sets_game_over_on_humanity(self, fresh_game: GameState) -> None:
        fresh_game.humanity = 0.5
        fresh_game.buy("optic_zoom")
        assert fresh_game._game_over is True
        assert "cyberpsycho" in fresh_game._game_over_reason

    def test_expensive_buy_depletes_humanity(self, fresh_game: GameState) -> None:
        """Buying chrome_skull costs 11 humanity (deterministic with mock)."""
        fresh_game.money = 10000
        fresh_game.buy("chrome_skull")
        # base_cost=13, cost=randint(11, 15)=11
        assert fresh_game.humanity == 89.0         # 100 - 11


# ── uninstall ────────────────────────────────────────────────────────


class TestUninstall:
    """Tests for GameState.uninstall()."""

    def test_uninstall_success(self, fresh_game: GameState) -> None:
        fresh_game.buy("optic_zoom")
        before = fresh_game.money
        result = fresh_game.uninstall("optic_zoom")
        assert result["success"] is True
        # refund = 800 // 2 = 400
        assert fresh_game.money == before + 400
        assert fresh_game.combat_bonus == 0
        # humanity was 99.0 (after buy cost), +1.5 → 100.5 capped at 100.0
        assert fresh_game.humanity == 100.0

    def test_uninstall_unknown_uid(self, fresh_game: GameState) -> None:
        result = fresh_game.uninstall("nonexistent")
        assert result["success"] is False
        assert "Unknown cyberware" in result["message"]

    def test_uninstall_not_owned(self, fresh_game: GameState) -> None:
        result = fresh_game.uninstall("optic_zoom")
        assert result["success"] is False
        assert "don't have" in result["message"]

    def test_uninstall_caps_humanity_at_100(self, fresh_game: GameState) -> None:
        fresh_game.money = 5000
        fresh_game.buy("optic_zoom")
        fresh_game.humanity = 100.0
        fresh_game.uninstall("optic_zoom")
        assert fresh_game.humanity == 100.0  # capped


# ── execute_job ──────────────────────────────────────────────────────

# Real job IDs from data.py: courier_run, street_brawl, runner_escort,
# data_heist, gang_cleanup, black_market_sabotage, corporate_espionage,
# cyberpsych_hunt
#
# courier_run: base_difficulty=15, reward=(100,300), humanity_cost=(1,3),
#              failure_money=(50,200), failure_hp=(3,8), failure_hum=(2,5)


class TestExecuteJob:
    """Tests for GameState.execute_job()."""

    def test_unknown_job(self, fresh_game: GameState) -> None:
        result = fresh_game.execute_job("no_such_job")
        assert result["success"] is False
        assert "Unknown gig ID" in result["message"]

    def test_success_path(self, fresh_game: GameState) -> None:
        result = fresh_game.execute_job("courier_run")
        assert result["success"] is True
        assert "MISSION COMPLETE" in result["message"]
        # roll=randint(1,100)=1, diff=15, effective=max(5,15)=15
        # chance = clamp(15,90, 50+0-15//2) = clamp(15,90,42) = 42
        # reward=randint(100,300)=100, hum_cost=randint(1,3)=1
        assert fresh_game.money == 1100
        assert fresh_game.humanity == 99.0
        assert fresh_game.day == 2

    def test_failure_path(self, fresh_game: GameState,
                          monkeypatch: pytest.MonkeyPatch) -> None:
        # Force roll=100 so it always fails (success_chance ~42 for courier_run)
        def custom_randint(a: int, b: int) -> int:
            if a == 1 and b == 100:
                return 100
            return a
        monkeypatch.setattr("server.models.game_state.random.randint",
                            custom_randint)
        result = fresh_game.execute_job("courier_run")
        assert result["success"] is True          # action completed
        assert "MISSION FAILED" in result["message"]
        assert "job_result" in result
        assert result["job_result"]["success"] is False

    def test_job_includes_job_result(self, fresh_game: GameState) -> None:
        result = fresh_game.execute_job("courier_run")
        jr = result["job_result"]
        for key in ("success", "job_name", "roll", "effective_diff",
                     "success_chance", "reward", "humanity_cost"):
            assert key in jr, f"Missing key: {key}"

    def test_job_increases_day(self, fresh_game: GameState) -> None:
        fresh_game.execute_job("courier_run")
        assert fresh_game.day == 2

    def test_job_reduces_humanity_on_success(self, fresh_game: GameState) -> None:
        before = fresh_game.humanity
        fresh_game.execute_job("courier_run")
        # humanity_cost=randint(1,3)=1
        assert fresh_game.humanity == before - 1


# ── heal ─────────────────────────────────────────────────────────────


class TestHeal:
    """Tests for GameState.heal()."""

    def test_heal_success(self, fresh_game: GameState) -> None:
        fresh_game.hp = 50
        before = fresh_game.money
        result = fresh_game.heal()
        assert result["success"] is True
        assert fresh_game.hp == 100
        assert fresh_game.money == before - 500
        # recovery=randint(10,20)=10 → 110, capped at 100
        assert fresh_game.humanity == 100.0

    def test_heal_success_partial_humanity(self, fresh_game: GameState) -> None:
        fresh_game.hp = 50
        fresh_game.humanity = 80.0
        fresh_game.heal()
        # recovery=10 → 90, not capped
        assert fresh_game.humanity == 90.0

    def test_heal_insufficient_funds(self, fresh_game: GameState) -> None:
        fresh_game.money = 100
        result = fresh_game.heal()
        assert result["success"] is False
        assert "Trauma Team costs" in result["message"]

    def test_heal_already_full(self, fresh_game: GameState) -> None:
        fresh_game.hp = 100
        fresh_game.humanity = 100.0
        result = fresh_game.heal()
        assert result["success"] is False
        assert "already at full health" in result["message"]


# ── rest ─────────────────────────────────────────────────────────────


class TestRest:
    """Tests for GameState.rest()."""

    def test_rest_success(self, fresh_game: GameState) -> None:
        fresh_game.humanity = 50.0
        before = fresh_game.money
        result = fresh_game.rest()
        assert result["success"] is True
        assert fresh_game.money == before - 150
        assert fresh_game.day == 2
        # recovery=randint(5,12)=5
        assert fresh_game.humanity == 55.0

    def test_rest_does_not_restore_hp(self, fresh_game: GameState) -> None:
        fresh_game.hp = 30
        fresh_game.rest()
        assert fresh_game.hp == 30

    def test_rest_insufficient_funds(self, fresh_game: GameState) -> None:
        fresh_game.money = 50
        result = fresh_game.rest()
        assert result["success"] is False
        assert "safehouse costs" in result["message"]

    def test_rest_humanity_already_max(self, fresh_game: GameState) -> None:
        fresh_game.humanity = 100.0
        result = fresh_game.rest()
        assert result["success"] is False
        assert "already at maximum" in result["message"]


# ── game-over guard ──────────────────────────────────────────────────


class TestGameOverGuard:
    """Actions should fail after game over."""

    def test_buy_after_game_over(self, fresh_game: GameState) -> None:
        fresh_game.humanity = 0.5
        fresh_game.buy("optic_zoom")  # triggers game over
        result = fresh_game.buy("chrome_skull")
        assert result["success"] is False
        # The response contains the game-over reason text
        assert "cyberpsycho" in result["message"] or "Game over" in result["message"]

    def test_heal_after_game_over(self, fresh_game: GameState) -> None:
        # Trigger game over by setting game-over state directly
        fresh_game._game_over = True
        fresh_game._game_over_reason = "flatlined"
        result = fresh_game.heal()
        assert result["success"] is False
        assert result["message"] == "flatlined"

    def test_rest_after_game_over(self, fresh_game: GameState) -> None:
        fresh_game.hp = 0
        fresh_game.rest()  # triggers game over
        result = fresh_game.rest()
        assert result["success"] is False

    def test_execute_job_after_game_over(self, fresh_game: GameState) -> None:
        # Force game-over state directly to test the guard
        fresh_game._game_over = True
        fresh_game._game_over_reason = "flatlined"
        result = fresh_game.execute_job("street_brawl")
        assert result["success"] is False
        assert result["message"] == "flatlined"
