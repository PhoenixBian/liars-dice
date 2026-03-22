"""ELO rating system for Liar's Dice.

Tracks player rating, match history, and progress curves.
All data persists to ~/.liars-dice/progress.json.
"""
import json
from datetime import datetime, timezone
from pathlib import Path


STATE_DIR = Path.home() / ".liars-dice"
PROGRESS_FILE = STATE_DIR / "progress.json"

# AI opponent ELO by style and difficulty
AI_ELO = {
    "conservative": {"easy": 800, "medium": 900, "hard": 1000},
    "aggressive": {"easy": 900, "medium": 1050, "hard": 1200},
    "fox": {"easy": 1100, "medium": 1300, "hard": 1500},
}


def load_progress() -> dict:
    """Load progress from disk."""
    if PROGRESS_FILE.exists():
        with open(PROGRESS_FILE) as f:
            return json.load(f)
    return _default_progress()


def save_progress(progress: dict):
    """Save progress to disk."""
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    with open(PROGRESS_FILE, "w") as f:
        json.dump(progress, f, indent=2, ensure_ascii=False)


def _default_progress() -> dict:
    return {
        "elo": 1000,
        "elo_history": [{"elo": 1000, "timestamp": _now(), "event": "init"}],
        "games_played": 0,
        "games_won": 0,
        "drills_completed": 0,
        "drills_correct": 0,
        "tutorial_completed": False,
        "current_drill_level": 1,
        "match_history": [],
    }


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def calculate_elo_change(player_elo: int, opponent_elo: int, won: bool,
                         k_factor: int = None) -> int:
    """Calculate ELO change after a match.

    Args:
        player_elo: Current player ELO.
        opponent_elo: Opponent ELO (for AI, use AI_ELO map).
        won: Whether the player won.
        k_factor: Override K-factor (default: 32 for <50 games, 16 after).
    """
    if k_factor is None:
        progress = load_progress()
        k_factor = 32 if progress["games_played"] < 50 else 16

    expected = 1 / (1 + 10 ** ((opponent_elo - player_elo) / 400))
    actual = 1.0 if won else 0.0
    change = round(k_factor * (actual - expected))
    return change


def calculate_multiplayer_elo(player_elo: int, opponents: list[dict],
                               finish_position: int, total_players: int) -> int:
    """Calculate ELO change for multiplayer games.

    Args:
        player_elo: Current player ELO.
        opponents: List of {"elo": int, "name": str} for each AI.
        finish_position: 1 = winner, 2 = second, etc.
        total_players: Total players in the game.

    Returns:
        Total ELO change.
    """
    avg_opponent_elo = sum(o["elo"] for o in opponents) / len(opponents) if opponents else 1000

    # Score based on position: 1st = 1.0, last = 0.0
    score = (total_players - finish_position) / (total_players - 1) if total_players > 1 else 0.5

    progress = load_progress()
    k = 32 if progress["games_played"] < 50 else 16

    expected = 1 / (1 + 10 ** ((avg_opponent_elo - player_elo) / 400))
    change = round(k * (score - expected))
    return change


def record_game(won: bool, opponent_style: str, opponent_difficulty: str,
                rounds: int, multiplayer: bool = False,
                finish_position: int = 1, total_players: int = 2,
                opponents: list[dict] = None) -> dict:
    """Record a completed game and update ELO.

    Returns dict with elo_before, elo_after, elo_change.
    """
    progress = load_progress()
    elo_before = progress["elo"]

    if multiplayer and opponents:
        change = calculate_multiplayer_elo(
            elo_before, opponents, finish_position, total_players)
    else:
        opponent_elo = AI_ELO.get(opponent_style, {}).get(opponent_difficulty, 1000)
        change = calculate_elo_change(elo_before, opponent_elo, won)

    new_elo = max(100, elo_before + change)  # Floor at 100

    progress["elo"] = new_elo
    progress["games_played"] += 1
    if won:
        progress["games_won"] += 1

    progress["elo_history"].append({
        "elo": new_elo,
        "timestamp": _now(),
        "event": "game",
        "result": "win" if won else "loss",
        "opponent": opponent_style,
        "change": change,
    })

    progress["match_history"].append({
        "timestamp": _now(),
        "result": "win" if won else "loss",
        "opponent_style": opponent_style,
        "opponent_difficulty": opponent_difficulty,
        "rounds": rounds,
        "elo_before": elo_before,
        "elo_after": new_elo,
        "multiplayer": multiplayer,
    })

    # Keep last 100 matches
    if len(progress["match_history"]) > 100:
        progress["match_history"] = progress["match_history"][-100:]

    save_progress(progress)

    return {
        "elo_before": elo_before,
        "elo_after": new_elo,
        "elo_change": change,
    }


def record_drill(correct: bool, level: int) -> dict:
    """Record a drill result and potentially advance level."""
    progress = load_progress()
    progress["drills_completed"] += 1
    if correct:
        progress["drills_correct"] += 1

    # Check for level advancement: 80% accuracy over last 10 drills
    accuracy = progress["drills_correct"] / max(1, progress["drills_completed"])
    recent_threshold = min(10, progress["drills_completed"])

    if progress["drills_completed"] >= 5 and accuracy >= 0.8:
        if progress["current_drill_level"] < 5:
            progress["current_drill_level"] += 1

    save_progress(progress)

    return {
        "drills_completed": progress["drills_completed"],
        "accuracy": accuracy,
        "current_level": progress["current_drill_level"],
    }


def get_stats() -> dict:
    """Get player statistics summary."""
    progress = load_progress()
    games = progress["games_played"]
    wins = progress["games_won"]

    return {
        "elo": progress["elo"],
        "games_played": games,
        "win_rate": wins / max(1, games),
        "drills_completed": progress["drills_completed"],
        "drill_accuracy": progress["drills_correct"] / max(1, progress["drills_completed"]),
        "current_drill_level": progress["current_drill_level"],
        "tutorial_completed": progress["tutorial_completed"],
        "elo_history": progress["elo_history"][-20:],  # Last 20 entries
    }


def get_ai_difficulty_for_elo(player_elo: int) -> tuple[str, str]:
    """Auto-select AI opponent based on player ELO.

    Returns (style, difficulty).
    """
    if player_elo < 900:
        return "conservative", "easy"
    elif player_elo < 1000:
        return "conservative", "hard"
    elif player_elo < 1100:
        return "aggressive", "easy"
    elif player_elo < 1200:
        return "aggressive", "hard"
    elif player_elo < 1350:
        return "fox", "easy"
    else:
        return "fox", "hard"


def generate_bip_content(progress: dict = None) -> str:
    """Generate Building in Public content from recent games.

    Returns markdown-formatted content ready to post.
    """
    if progress is None:
        progress = load_progress()

    stats = get_stats()
    recent = progress["match_history"][-5:] if progress["match_history"] else []

    if not recent:
        return "No games played yet. Start with `/liars-dice play` to begin!"

    wins = sum(1 for m in recent if m["result"] == "win")
    losses = len(recent) - wins

    elo_start = recent[0]["elo_before"]
    elo_end = recent[-1]["elo_after"]
    delta = elo_end - elo_start
    arrow = "+" if delta >= 0 else ""

    content = f"""Liar's Dice AI Training Update

ELO: {elo_start} -> {elo_end} ({arrow}{delta})
Recent: {wins}W {losses}L
Drill accuracy: {stats['drill_accuracy']:.0%}

"""

    # Best moment from recent games
    if recent:
        last = recent[-1]
        content += f"Last match: vs {last['opponent_style'].title()} AI ({last['opponent_difficulty']}) — {'Won' if last['result'] == 'win' else 'Lost'} in {last['rounds']} rounds.\n\n"

    content += "Training with Claude Code. Skill: github.com/PJBian1/liars-dice"

    return content
