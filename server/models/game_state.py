#!/usr/bin/env python3
"""Game state model.

This module contains the GameState class which manages the player's state,
including health, money, humanity, and cyberware.
"""
from __future__ import annotations

import random
from typing import Any

from ..config.constants import HEAL_COST, REST_COST
from ..config.data import CYBERWARE, JOBS
from ..utils.helpers import clamp, humanity_color_css


class GameState:
    """Mutable session state for a single player.

    Attributes:
        money:          Current eddies.
        hp:             Health points (0-100).
        humanity:       Humanity level (0.0-100.0).
        combat_bonus:   Aggregate cyberware combat bonus.
        owned:          Installed cyberware as ``[(uid, name), ...]``.
        day:            In-game day counter.
        _game_over:     Whether the session has ended.
        _game_over_reason: Reason text for the game-over screen.
    """

    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        """Restore the state to initial values."""
        self.money: int = 1000
        self.hp: int = 100
        self.humanity: float = 100.0
        self.combat_bonus: int = 0
        self.owned: list[tuple[str, str]] = []
        self.day: int = 1
        self._game_over: bool = False
        self._game_over_reason: str = ""

    # Serialisation

    def status_dict(self) -> dict[str, Any]:
        """Return a serialisable snapshot of the current state."""
        return {
            "money": self.money,
            "hp": self.hp,
            "humanity": round(self.humanity, 1),
            "combat_bonus": self.combat_bonus,
            "owned": [{"id": uid, "name": name} for uid, name in self.owned],
            "day": self.day,
            "game_over": self._game_over,
            "game_over_reason": self._game_over_reason,
            "humanity_color": humanity_color_css(self.humanity),
            "hp_color": "green"
            if self.hp > 50
            else ("yellow" if self.hp > 20 else "red"),
        }

    # Internal

    def _check_game_over(self) -> None:
        """Set ``_game_over`` and a reason if either stat hits zero."""
        if self._game_over:
            return
        if self.humanity <= 0:
            self._game_over = True
            self._game_over_reason = (
                "Your humanity has evaporated. The chrome owns you now. "
                "You are a cyberpsycho — a hollow shell of metal and rage. "
                "The Fixer's people will find you before sunrise."
            )
        elif self.hp <= 0:
            self._game_over = True
            self._game_over_reason = (
                "You flatlined in a back-alley safehouse. "
                "Your body is gone, but the chrome keeps running — "
                "a ghost in the machine, forever hunting."
            )

    def _game_over_response(self) -> dict[str, Any] | None:
        """Return a failure response if the current session has already ended."""
        if not self._game_over:
            return None
        return {
            "success": False,
            "message": self._game_over_reason or "Game over. Start a new game to continue.",
            "state": self.status_dict(),
        }

    # Player actions

    def buy(self, uid: str) -> dict[str, Any]:
        """Install a piece of cyberware.

        Returns:
            A result dict with ``success``, ``message``, and the updated
            ``state`` (or just ``success``/``message`` on failure).
        """
        if uid not in CYBERWARE:
            return {"success": False, "message": f"Unknown cyberware: '{uid}'.", "state": self.status_dict()}

        if response := self._game_over_response():
            return response

        item = CYBERWARE[uid]

        if uid in [x[0] for x in self.owned]:
            return {"success": False, "message": f"You already have {item['name']} installed.", "state": self.status_dict()}

        if self.money < item["price"]:
            return {
                "success": False,
                "message": f"Not enough eddies. Need ${item['price']:,}, have ${self.money:,}.",
                "state": self.status_dict(),
            }

        # Apply purchase
        self.money -= item["price"]
        self.combat_bonus += item["combat_bonus"]
        self.owned.append((uid, item["name"]))

        # Cyberpsychosis cost — scales with price
        base_cost = max(1, item["price"] // 300)
        cost = random.randint(max(1, base_cost - 2), base_cost + 2)
        self.humanity = max(0.0, self.humanity - cost)
        self._check_game_over()

        return {
            "success": True,
            "message": (
                f"Installed {item['name']} for ${item['price']:,}. "
                f"Combat bonus +{item['combat_bonus']}. "
                f"Humanity -{cost}%."
            ),
            "state": self.status_dict(),
        }

    def uninstall(self, uid: str) -> dict[str, Any]:
        """Remove a piece of cyberware at 50% refund.

        Returns:
            A result dict with ``success``, ``message``, and updated ``state``.
        """
        if uid not in CYBERWARE:
            return {"success": False, "message": f"Unknown cyberware: '{uid}'.", "state": self.status_dict()}

        if response := self._game_over_response():
            return response

        if uid not in [x[0] for x in self.owned]:
            return {
                "success": False,
                "message": f"You don't have {CYBERWARE[uid]['name']} installed.",
                "state": self.status_dict(),
            }

        item = CYBERWARE[uid]
        sell_price = item["price"] // 2

        self.money += sell_price
        self.combat_bonus = max(0, self.combat_bonus - item["combat_bonus"])
        self.owned = [(u, n) for u, n in self.owned if u != uid]
        self.humanity = min(100.0, self.humanity + 1.5)
        self._check_game_over()

        return {
            "success": True,
            "message": (
                f"Uninstalled {item['name']} for ${sell_price:,}. "
                f"Combat bonus -{item['combat_bonus']}. "
                f"Humanity +1.5%."
            ),
            "state": self.status_dict(),
        }

    def execute_job(self, job_id: str) -> dict[str, Any]:
        """Roll for a gig and update state accordingly.

        Args:
            job_id: Unique identifier from the ``JOBS`` list.

        Returns:
            A result dict with ``success``, ``message``, and the current
            ``state``. Successful job runs also include ``job_result``.
        """
        job = next((j for j in JOBS if j["id"] == job_id), None)
        if not job:
            return {"success": False, "message": f"Unknown gig ID: '{job_id}'.", "state": self.status_dict()}

        if response := self._game_over_response():
            return response

        self.day += 1
        diff = job["base_difficulty"]
        effective_diff = max(5, diff - self.combat_bonus)
        success_chance = clamp(15, 90, 50 + self.combat_bonus * 2 - diff // 2)

        roll = random.randint(1, 100)
        success = roll <= success_chance

        if success:
            reward = random.randint(*job["reward_range"])
            humanity_cost = random.randint(*job["humanity_cost"])
            self.money += reward
            self.humanity = max(0.0, self.humanity - humanity_cost)
            self._check_game_over()

            return {
                "success": True,
                "message": f"MISSION COMPLETE: {job['name']}!",
                "state": self.status_dict(),
                "job_result": {
                    "success": True,
                    "job_name": job["name"],
                    "reward": reward,
                    "humanity_cost": humanity_cost,
                    "roll": roll,
                    "effective_diff": effective_diff,
                    "success_chance": success_chance,
                    "description": job["description"],
                    "risk_level": job["risk_level"],
                },
            }

        # Failure
        loss = random.randint(100, 400)
        h_loss = random.randint(3, 8)
        hp_loss = random.randint(5, 15)
        self.money = max(0, self.money - loss)
        self.humanity = max(0.0, self.humanity - h_loss)
        self.hp = max(0, self.hp - hp_loss)
        self._check_game_over()

        return {
            "success": True,
            "message": f"MISSION FAILED: {job['name']}!",
            "state": self.status_dict(),
            "job_result": {
                "success": False,
                "job_name": job["name"],
                "loss": loss,
                "humanity_cost": h_loss,
                "hp_cost": hp_loss,
                "roll": roll,
                "effective_diff": effective_diff,
                "success_chance": success_chance,
                "description": job["description"],
                "risk_level": job["risk_level"],
            },
        }

    def heal(self) -> dict[str, Any]:
        """Call Trauma Team for emergency extraction ($500).

        Restores HP to full and recovers 10-20% humanity.
        """
        if response := self._game_over_response():
            return response

        if self.money < HEAL_COST:
            return {
                "success": False,
                "message": (
                    f"Trauma Team costs ${HEAL_COST:,} for emergency extraction. "
                    f"You only have ${self.money:,}."
                ),
                "state": self.status_dict(),
            }

        if self.humanity >= 100.0 and self.hp >= 100:
            return {"success": False, "message": "You're already at full health.", "state": self.status_dict()}

        self.money -= HEAL_COST
        recovery_h = random.randint(10, 20)
        self.humanity = min(100.0, self.humanity + recovery_h)
        self.hp = min(100, self.hp + 100 - self.hp)
        self._check_game_over()

        return {
            "success": True,
            "message": (
                f"Trauma Team extraction complete. "
                f"HP fully restored. "
                f"Humanity recovered: +{recovery_h}%."
            ),
            "state": self.status_dict(),
        }

    def rest(self) -> dict[str, Any]:
        """Rest at a safehouse ($150) to recover humanity (5-12%).

        Does not restore HP.
        """
        if response := self._game_over_response():
            return response

        if self.money < REST_COST:
            return {
                "success": False,
                "message": (
                    f"A night at the safehouse costs ${REST_COST:,}, "
                    f"but you only have ${self.money:,}."
                ),
                "state": self.status_dict(),
            }

        if self.humanity >= 100.0:
            return {"success": False, "message": "Your humanity is already at maximum.", "state": self.status_dict()}

        self.money -= REST_COST
        self.day += 1
        recovery = random.randint(5, 12)
        self.humanity = min(100.0, self.humanity + recovery)
        self._check_game_over()

        return {
            "success": True,
            "message": (
                f"Rested at the safehouse for ${REST_COST:,}. "
                f"Humanity recovered: +{recovery}%."
            ),
            "state": self.status_dict(),
        }
