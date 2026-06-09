#!/usr/bin/env python3
"""Cyberpunk Edge-Runner Simulator — a single-file terminal text RPG."""
from __future__ import annotations

import random
import sys
import time

# ── Color constants (ANSI) ────────────────────────────────────────────
BOLD      = "\033[1m"
DIM       = "\033[2m"
UNDERLINE = "\033[4m"
RESET     = "\033[0m"
RED       = "\033[31m"
GREEN     = "\033[32m"
YELLOW    = "\033[33m"
BLUE      = "\033[34m"
MAGENTA   = "\033[35m"
CYAN      = "\033[36m"
WHITE     = "\033[37m"

# ── Game data ─────────────────────────────────────────────────────────
CYBERWARE = {
    "optic_zoom": {
        "name": "Optical Zoom Implants",
        "price": 800,
        "combat_bonus": 5,
        "description": "Enhanced vision for precision targeting.",
    },
    "subdermal_armor": {
        "name": "Subdermal Armor Weave",
        "price": 1500,
        "combat_bonus": 10,
        "description": "Reinforced under-skin plating for damage resistance.",
    },
    "neural_boost": {
        "name": "Neural Processing Unit",
        "price": 2200,
        "combat_bonus": 15,
        "description": "Cognitive overclock for faster reaction times.",
    },
    "synth_muscle": {
        "name": "Synth-Muscle Fibers",
        "price": 1800,
        "combat_bonus": 12,
        "description": "Artificial fibers for superhuman strength.",
    },
    "combat_reflex_tank": {
        "name": "Combat Reflex Tank",
        "price": 3500,
        "combat_bonus": 20,
        "description": "Emergency adrenal boost system for burst combat speed.",
    },
    "chrome_skull": {
        "name": "Chrome Skull Plate",
        "price": 4000,
        "combat_bonus": 25,
        "description": "Titanium-reinforced cranial housing.",
    },
}

JOBS = [
    {
        "name": "Data Heist",
        "base_difficulty": 40,
        "reward_range": (600, 1200),
        "humanity_cost": (3, 7),
        "risk_level": "medium",
        "description": "Break into a corporate data vault and extract encrypted files.",
    },
    {
        "name": "Street Brawl Enforcer",
        "base_difficulty": 25,
        "reward_range": (200, 500),
        "humanity_cost": (5, 12),
        "risk_level": "low",
        "description": "Beat the competition in an underground fighting ring.",
    },
    {
        "name": "Corporate Espionage",
        "base_difficulty": 55,
        "reward_range": (1500, 3000),
        "humanity_cost": (8, 15),
        "risk_level": "high",
        "description": "Infiltrate a rival corp's R&D lab and steal schematics.",
    },
    {
        "name": "Runner Escort",
        "base_difficulty": 30,
        "reward_range": (400, 900),
        "humanity_cost": (2, 5),
        "risk_level": "low",
        "description": "Safely escort a fixer through hostile gang territory.",
    },
    {
        "name": "Black Market Sabotage",
        "base_difficulty": 50,
        "reward_range": (1000, 2500),
        "humanity_cost": (6, 14),
        "risk_level": "high",
        "description": "Destroy a rival dealer's shipment before it moves.",
    },
    {
        "name": "Cyberpsych Hunt",
        "base_difficulty": 70,
        "reward_range": (3000, 5000),
        "humanity_cost": (10, 20),
        "risk_level": "extreme",
        "description": "Track down and neutralize a rogue cyberpsycho before they hurt innocents.",
    },
    {
        "name": "Courier Run",
        "base_difficulty": 15,
        "reward_range": (100, 300),
        "humanity_cost": (1, 3),
        "risk_level": "low",
        "description": "Deliver a package across the city. Simple, fast, low risk.",
    },
    {
        "name": "Gang War Cleanup",
        "base_difficulty": 45,
        "reward_range": (700, 1800),
        "humanity_cost": (5, 10),
        "risk_level": "medium",
        "description": "Clean up territory disputes between warring street gangs.",
    },
]

HEADER = f"""
{YELLOW}{BOLD}
 ╔══════════════════════════════════════════════════════════╗
 ║                                                          ║
 ║    ██████╗ ██╗     ██╗███╗   ██╗████████╗███████╗██████╗  ║
 ║    ██╔══██╗██║     ██║████╗  ██║╚══██╔══╝██╔════╝██╔══██╗ ║
 ║    ██████╔╝██║     ██║██╔██╗ ██║   ██║   █████╗  ██████╔╝ ║
 ║    ██╔══██╗██║     ██║██║╚██╗██║   ██║   ██╔══╝  ██╔══██╗ ║
 ║    ██████╔╝███████╗██║██║ ╚████║   ██║   ███████╗██║  ██║ ║
 ║    ╚═════╝ ╚══════╝╚═╝╚═╝  ╚═══╝   ╚═╝   ╚══════╝╚═╝  ╚═╝ ║
 ║                                                          ║
 ║              E D G E - R U N N E R                       ║
 ║                                                          ║
 ║         {DIM}Live fast. Modify everything. Don't lose yourself.{RESET}
 ║                                                          ║
 ║══════════════════════════════════════════════════════════║
{RESET}
"""

BORDER = "═" * 56
THIN     = "─" * 56


def cls():
    """Clear the terminal screen."""
    print("\033[2J\033[H", end="")


def slow_print(text: str, speed: float = 0.015, **color):
    """Stream text char-by-char with optional ANSI color for cinematic effect."""
    for ch in text:
        sys.stdout.write(ch)
        sys.stdout.flush()
        time.sleep(speed)
    print()


def draw_section(title: str, lines: list[str], color: str = DIM):
    """Print a bordered section with title and body lines."""
    print(f"{color}{BORDER}{RESET}")
    print(f"{color}{title:^56}{RESET}")
    print(f"{color}{BORDER}{RESET}")
    for line in lines:
        print(f"{color}  {line:<50}{RESET}")
    print(f"{color}{BORDER}{RESET}")


def draw_header(stats: dict):
    """Print the persistent HUD header."""
    money   = f"${stats['money']}"
    human   = f"{stats['humanity']:.1f}%"
    bonus   = stats["combat_bonus"]
    print(f"  {YELLOW}{BOLD}◈ {money:>8}     ◈ Humanity: {human:<8} ◈ Combat Bonus: +{bonus:<3} ◈{RESET}")


def show_status(stats: dict):
    """Print current player status."""
    lines = [
        f"Money:         {YELLOW}${stats['money']:>7,}{RESET}",
        f"Humanity:      {humanity_color(stats['humanity'])}{stats['humanity']:.1f}%{RESET}",
        f"Combat Bonus:  {GREEN}+{stats['combat_bonus']:<4}{RESET}",
        "Installed Cyberware:",
    ]
    if stats["owned"]:
        for uid, name in stats["owned"]:
            lines.append(f"  └─ {CYAN}{name}{RESET}")
    else:
        lines.append(f"  └─ {DIM}None{RESET}")
    draw_section(f"{YELLOW}STATUS{DIM} ─ Overview", lines)


def show_shop(stats: dict):
    """Print the cyberware shop menu."""
    lines = []
    for uid, item in CYBERWARE.items():
        can_buy = stats["money"] >= item["price"]
        owned   = uid in [item[0] for item in stats["owned"]]
        if owned:
            tag = f"  {GREEN}[OWNED]{RESET}"
        elif can_buy:
            tag = f"  {YELLOW}can buy{RESET}"
        else:
            tag = f"  {RED}need ${item['price']:,}{RESET}"
        lines.append(
            f"  {CYAN}{uid:<20}{RESET}  {tag:<25} +{item['combat_bonus']:<3} combat"
        )

    detail_lines = []
    if stats.get("shop_detail"):
        item = CYBERWARE[stats["shop_detail"]]
        detail_lines = [
            f"  Selected: {CYAN}{item['name']}{RESET}",
            f"  {item['description']}",
            f"  Price: {YELLOW}${item['price']:,}{RESET}  Combat: +{item['combat_bonus']}",
        ]

    draw_section(f"{GREEN}CYBERWARE SHOP{DIM} ─ 'q' to return", lines, color=GREEN)
    if detail_lines:
        draw_section("DETAIL", detail_lines, color=DIM)


def buy_cyberware(stats: dict, uid: str) -> dict | None:
    """Attempt to buy a piece of cyberware. Returns the new item or None."""
    if uid not in CYBERWARE:
        return None
    item = CYBERWARE[uid]
    if uid in [item[0] for item in stats["owned"]]:
        print(f"\n  {YELLOW}You already have {item['name']} installed.{RESET}")
        return None
    if stats["money"] < item["price"]:
        print(f"\n  {RED}Not enough money. Need ${item['price']:,}, have ${stats['money']:,}.{RESET}")
        return None
    # Buy it
    stats["money"] -= item["price"]
    stats["combat_bonus"] += item["combat_bonus"]
    stats["owned"].append((uid, item["name"]))
    # Cyberpsychosis: each purchase costs humanity (1-3% + price factor)
    base_cost = max(1, item["price"] // 300)
    cost = random.randint(max(1, base_cost - 2), base_cost + 2)
    stats["humanity"] = max(0.0, stats["humanity"] - cost)
    print(f"\n  {GREEN}Installed {item['name']} for ${item['price']:,}.{RESET}")
    print(f"  {DIM}Combat bonus +{item['combat_bonus']}. Humanity -{cost}%{RESET}")
    return item


def sell_cyberware(stats: dict, uid: str) -> bool:
    """Attempt to sell a piece of cyberware. Returns True if sold."""
    if uid not in CYBERWARE:
        return False
    if uid not in [item[0] for item in stats["owned"]]:
        print(f"\n  {RED}You don't have {CYBERWARE[uid]['name']}.{RESET}")
        return False
    item = CYBERWARE[uid]
    sell_price = item["price"] // 2
    stats["money"] += sell_price
    stats["combat_bonus"] = max(0, stats["combat_bonus"] - item["combat_bonus"])
    stats["owned"] = [(u, n) for u, n in stats["owned"] if u != uid]
    # Selling gives back a little humanity
    stats["humanity"] = min(100.0, stats["humanity"] + 1.5)
    print(f"\n  {YELLOW}Sold {item['name']} for ${sell_price:,}.{RESET}")
    print(f"  {DIM}Combat bonus -{item['combat_bonus']}. Humanity +1.5%{RESET}")
    return True


def job_menu(stats: dict) -> dict | None:
    """Print job list, return the selected job dict or None."""
    lines = []
    for i, job in enumerate(JOBS, start=1):
        lines.append(
            f"  {YELLOW}{i:>2}{RESET}. {job['name']:<30} [{job['risk_level']:^8}] "
            f"${job['reward_range'][0]:>4,}-${job['reward_range'][1]:>4,}"
        )
    lines.append("")
    lines.append(f"  {DIM}Difficulty varies. Your combat bonus improves odds.{RESET}")
    draw_section(f"{BLUE}AVAILABLE JOBS{DIM} ─ Enter number or 'q'{BLUE}", lines)
    return None  # caller handles input


def pick_job() -> dict:
    """Prompt user to pick a job by number. Loops until valid."""
    while True:
        draw_section(f"{BLUE}AVAILABLE JOBS{DIM} ─ Enter number or 'q'{BLUE}", [
            f"  {DIM}{'='*50}{RESET}",
        ] + [
            f"  {YELLOW}{i:>2}{RESET}. {job['name']:<30} [{job['risk_level']:^8}] "
            f"${job['reward_range'][0]:>4,}-${job['reward_range'][1]:>4,}"
            for i, job in enumerate(JOBS, start=1)
        ] + [
            f"  {DIM}Difficulty varies. Your combat bonus improves odds.{RESET}",
            f"  {DIM}{'='*50}{RESET}",
        ])
        raw = input(f"  {YELLOW}Choose a job (1-{len(JOBS)}) or 'q': {RESET}").strip().lower()
        if raw == "q":
            return None
        try:
            idx = int(raw)
            if 1 <= idx <= len(JOBS):
                return JOBS[idx - 1]
        except ValueError:
            pass
        print(f"  {RED}Invalid choice. Enter 1-{len(JOBS)} or 'q'.{RESET}")


def execute_job(stats: dict, job: dict) -> bool:
    """Run a job combat encounter. Returns True on success."""
    diff = job["base_difficulty"]
    # Difficulty scales slightly with combat bonus (higher bonus = easier)
    effective_diff = max(5, diff - stats["combat_bonus"])
    success_chance = clamp(15, 90, 50 + stats["combat_bonus"] * 2 - diff // 2)

    cls()
    slow_print(
        f"{BLUE}JOB: {BOLD}{job['name']}{RESET}\n"
        f"{DIM}{job['description']}{RESET}\n"
        f"{DIM}Risk: {job['risk_level']} | Difficulty: {diff} "
        f"(effective: {effective_diff}) | Your chance: {success_chance}%{RESET}",
        speed=0.02,
    )
    input(f"\n  {DIM}{BLUE}[Press Enter to begin]{RESET}")

    roll = random.randint(1, 100)
    success = roll <= success_chance

    slow_print(f"\n  {DIM}Rolling... you got {roll}.{'Success!' if success else 'Failed.'}{RESET}", speed=0.025)

    if success:
        reward = random.randint(*job["reward_range"])
        humanity_cost = random.randint(*job["humanity_cost"])
        stats["money"] += reward
        stats["humanity"] = max(0.0, stats["humanity"] - humanity_cost)
        slow_print(
            f"\n  {GREEN}{BOLD}MISSION COMPLETE!{RESET}\n"
            f"  {GREEN}Reward: ${reward:,}{RESET}\n"
            f"  {RED}Humanity: -{humanity_cost}%{RESET}\n"
            f"  {DIM}{RED}Your soul takes another hit...{RESET}",
            speed=0.02,
        )
    else:
        # Failure: lose some money and humanity
        loss = random.randint(100, 400)
        h_loss = random.randint(3, 8)
        stats["money"] = max(0, stats["money"] - loss)
        stats["humanity"] = max(0.0, stats["humanity"] - h_loss)
        slow_print(
            f"\n  {RED}{BOLD}MISSION FAILED!{RESET}\n"
            f"  {RED}You lost ${loss:,}{RESET}\n"
            f"  {RED}Humanity: -{h_loss}%{RESET}\n"
            f"  {DIM}The streets remember your weakness.{RESET}",
            speed=0.02,
        )

    input(f"\n  {DIM}[Press Enter to continue]{RESET}")
    return success


def clamp(lo: int, hi: int, val: int) -> int:
    return max(lo, min(hi, val))


def humanity_color(h: float) -> str:
    if h > 70:
        return GREEN
    if h > 40:
        return YELLOW
    return RED


def print_game_over(stats: dict, reason: str):
    """Display the game-over screen."""
    cls()
    print(
        f"""
{RED}{BOLD}
 ╔══════════════════════════════════════════════════════════╗
 ║                                                          ║
 ║    ██████╗ ██████╗  █████╗ ██████╗ ██╗   ██╗███████╗     ║
 ║    ██╔══██╗██╔══██╗██╔══██╗██╔══██╗██║   ██║██╔════╝     ║
 ║    ██████╔╝██████╔╝███████║██║  ██║██║   ██║███████╗     ║
 ║    ██╔═══╝ ██╔══██╗██╔══██║██║  ██║██║   ██║╚════██║     ║
 ║    ██║     ██║  ██║██║  ██║██████╔╝╚██████╔╝███████║     ║
 ║    ╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝  ╚═════╝ ╚══════╝     ║
 ║                                                          ║
 ║              G A M E   O V E R                           ║
 ║                                                          ║
 ╚══════════════════════════════════════════════════════════╝
{RESET}
{YELLOW}{BOLD}Reason: {reason}{RESET}

{DIM}Final Stats:{RESET}
  Money:       ${stats['money']:,}
  Humanity:    {stats['humanity']:.1f}%
  Combat Bonus:+{stats['combat_bonus']}
  Cyberware:   {', '.join(n for _, n in stats['owned']) or 'None'}

{DIM}The streets don't forgive. They absorb you.{RESET}
{DIM}— thanks for playing —{RESET}
"""
    )


def main_menu() -> str:
    """Print the main menu, return the user's choice string."""
    cls()
    print(HEADER)
    print(f"\n  {DIM}{'─' * 56}{RESET}\n")
    print(f"  1. {GREEN}Status{RESET}          — Check your stats and cyberware")
    print(f"  2. {BLUE}Shop{RESET}            — Buy / Sell cyberware")
    print(f"  3. {YELLOW}Take a Job{RESET}     — Find work (risky)")
    print(f"  4. {DIM}Rest{RESET}            — Sleep, recover humanity")
    print(f"  5. {RED}Quit{RESET}            — Walk away from the game\n")
    print(f"  {DIM}{'─' * 56}{RESET}")
    return input(f"  {YELLOW}Choose (1-5): {RESET}").strip()


def rest(stats: dict):
    """Rest to recover humanity at a netrunners den."""
    cost = 150
    if stats["money"] < cost:
        print(f"\n  {RED}A night at the netrunner den costs ${cost}, but you only have ${stats['money']:,}.{RESET}")
        input(f"\n  {DIM}[Press Enter to continue]{RESET}")
        return
    if stats["humanity"] >= 100.0:
        print(f"\n  {GREEN}Your humanity is already at maximum.{RESET}")
        input(f"\n  {DIM}[Press Enter to continue]{RESET}")
        return
    stats["money"] -= cost
    recovery = random.randint(5, 12)
    stats["humanity"] = min(100.0, stats["humanity"] + recovery)
    print(f"\n  {GREEN}Rested at the netrunner den for ${cost:,}.{RESET}")
    print(f"  {GREEN}Humanity recovered: +{recovery}%{RESET}")
    input(f"\n  {DIM}[Press Enter to continue]{RESET}")


def handle_shop(stats: dict):
    """Enter the shop sub-menu for buying and selling."""
    while True:
        cls()
        draw_header(stats)
        show_shop(stats)
        choice = input(f"\n  {YELLOW}Action: [b]uy [s]ell [d]etail <name> [q]uit: {RESET}").strip().lower()

        if choice in ("q", "quit", ""):
            break
        elif choice in ("b", "buy"):
            uid = input(f"  {YELLOW}Cyberware ID (e.g. optic_zoom): {RESET}").strip().lower()
            if uid:
                item = buy_cyberware(stats, uid)
                if item is None and uid not in CYBERWARE:
                    print(f"  {RED}Unknown item '{uid}'.{RESET}")
        elif choice in ("s", "sell"):
            uid = input(f"  {YELLOW}Cyberware ID to sell: {RESET}").strip().lower()
            if uid:
                sell_cyberware(stats, uid)
        elif choice in ("d", "detail"):
            name = input(f"  {YELLOW}Cyberware ID for details: {RESET}").strip().lower()
            if name in CYBERWARE:
                stats["shop_detail"] = name
            else:
                print(f"  {RED}Unknown item '{name}'.{RESET}")
        else:
            print(f"  {RED}Invalid action. Try buy, sell, detail, or quit.{RESET}")


def game_loop():
    """Main game loop."""
    stats = {
        "money": 1000,
        "humanity": 100.0,
        "combat_bonus": 0,
        "owned": [],
        "shop_detail": None,
    }

    cls()
    slow_print(
        f"  {CYAN}Year 2089. Night City sprawls like a circuit board possessed.{RESET}\n\n"
        f"  {CYAN}You're an edge-runner — part merc, part ghost.{RESET}\n"
        f"  {CYAN}You start with {YELLOW}${stats['money']:,}{RESET}, "
        f"{GREEN}{stats['humanity']:.0f}% humanity{RESET},\n"
        f"  {CYAN}and a body that's still mostly your own.\n\n"
        f"  {YELLOW}Use the streets. Buy upgrades. Take jobs.\n"
        f"  {RED}But watch your humanity — hit zero and the chrome takes over.{RESET}",
        speed=0.018,
    )
    print()
    input(f"  {DIM}{BLUE}[Press Enter to enter Night City]{RESET}")

    while True:
        # Check humanity death
        if stats["humanity"] <= 0:
            print_game_over(
                stats,
                "Your humanity has evaporated. The chrome owns you now. "
                "You are a cyberpsycho — a hollow shell of metal and rage.\n"
                "The Fixer's people will find you before sunrise.",
            )
            break

        action = main_menu()

        if action == "1":
            show_status(stats)
            input(f"\n  {DIM}[Press Enter to continue]{RESET}")
        elif action == "2":
            handle_shop(stats)
        elif action == "3":
            job = pick_job()
            if job:
                execute_job(stats, job)
            # else: user hit 'q', loop back to main menu
        elif action == "4":
            rest(stats)
        elif action in ("5", "quit", "q", "exit"):
            cls()
            print(
                f"\n  {DIM}Walking away from the edge...\n"
                f"  Money:    ${stats['money']:,}\n"
                f"  Humanity: {stats['humanity']:.1f}%\n\n"
                f"  {DIM}— thanks for playing —{RESET}\n"
            )
            raise SystemExit(0)
        else:
            print(f"\n  {RED}Invalid choice. Enter 1-5.{RESET}")
            input(f"\n  {DIM}[Press Enter to continue]{RESET}")


if __name__ == "__main__":
    try:
        game_loop()
    except (KeyboardInterrupt, EOFError):
        print(f"\n\n  {DIM}— interrupted. Stay human. —{RESET}\n")
        sys.exit(0)
