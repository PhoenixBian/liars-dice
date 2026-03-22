"""AI opponent strategies for Liar's Dice.

Three personality types with configurable difficulty:
- Conservative: plays safe, rarely bluffs
- Aggressive: pushes hard, jump-bids, uses zhai as weapon
- Fox: adapts, baits, controlled bluffing
"""
import random

from .probability import (
    expected_count, dice_probability
)


class AIStrategy:
    """Base class for AI decision making."""

    def __init__(self, difficulty: float = 0.5):
        """
        Args:
            difficulty: 0.0 (easy/makes mistakes) to 1.0 (optimal play).
        """
        self.difficulty = difficulty

    def decide(self, game_state: dict, my_dice: list[int],
               rules_wild: bool, rules_zhai: bool, zhai_active: bool) -> dict:
        """Decide what to do: bid or challenge.

        Returns:
            {"action": "bid", "quantity": N, "face": F, "is_zhai": bool}
            or {"action": "challenge"}
        """
        raise NotImplementedError

    def _my_counts(self, my_dice: list[int], wild: bool, zhai: bool) -> dict[int, int]:
        """Count effective dice per face."""
        raw = {}
        for d in my_dice:
            raw[d] = raw.get(d, 0) + 1
        ones = raw.get(1, 0)
        counts = {}
        for face in range(1, 7):
            base = raw.get(face, 0)
            if wild and not zhai and face != 1:
                counts[face] = base + ones
            else:
                counts[face] = base
        return counts

    def _expected(self, total_dice: int, my_count: int, wild: bool, zhai: bool) -> float:
        unknown = max(0, total_dice - len([]))  # placeholder
        p = dice_probability(wild, zhai)
        return my_count + max(0, total_dice - 5) * p

    def _strongest_face(self, counts: dict[int, int]) -> int:
        """Find the face I have the most of."""
        return max(counts, key=counts.get)

    def _add_noise(self, value: float, scale: float = 1.0) -> float:
        """Add decision noise inversely proportional to difficulty."""
        noise_level = (1 - self.difficulty) * scale
        return value + random.gauss(0, noise_level)


class ConservativeAI(AIStrategy):
    """Plays safe. Only bids within expected range. Challenges when clearly over.

    ELO range: 800-1000.
    """

    def decide(self, game_state: dict, my_dice: list[int],
               rules_wild: bool, rules_zhai: bool, zhai_active: bool) -> dict:
        total = game_state["total_dice"]
        current_bid = game_state.get("current_bid")
        counts = self._my_counts(my_dice, rules_wild, zhai_active)

        if current_bid is None:
            # Opening bid: my strongest, low quantity
            best_face = self._strongest_face(counts)
            my_c = counts[best_face]
            exp = expected_count(total, my_c, rules_wild, zhai_active)
            qty = max(1, int(exp - 1.5))
            return {"action": "bid", "quantity": qty, "face": best_face, "is_zhai": False}

        bid_qty = current_bid["quantity"]
        bid_face = current_bid["face"]
        my_c = counts.get(bid_face, 0)
        exp = expected_count(total, my_c, rules_wild, zhai_active)

        # Challenge if bid is significantly over expected
        threshold = self._add_noise(1.5, scale=0.5)
        if bid_qty > exp + threshold:
            return {"action": "challenge"}

        # Try to bid on my strongest face
        best_face = self._strongest_face(counts)
        best_c = counts[best_face]
        best_exp = expected_count(total, best_c, rules_wild, zhai_active)

        # Conservative: bid at expected - 1
        safe_qty = max(1, int(best_exp - self._add_noise(0.5, 0.3)))

        if best_face > bid_face and safe_qty >= bid_qty:
            return {"action": "bid", "quantity": bid_qty, "face": best_face, "is_zhai": False}
        elif safe_qty > bid_qty:
            return {"action": "bid", "quantity": bid_qty + 1, "face": best_face, "is_zhai": False}
        else:
            # Can't bid safely, challenge
            return {"action": "challenge"}


class AggressiveAI(AIStrategy):
    """Pushes hard. Jump-bids. Uses zhai as weapon. Bluffs 30% of the time.

    ELO range: 900-1200.
    """

    def decide(self, game_state: dict, my_dice: list[int],
               rules_wild: bool, rules_zhai: bool, zhai_active: bool) -> dict:
        total = game_state["total_dice"]
        current_bid = game_state.get("current_bid")
        counts = self._my_counts(my_dice, rules_wild, zhai_active)

        if current_bid is None:
            best_face = self._strongest_face(counts)
            my_c = counts[best_face]
            exp = expected_count(total, my_c, rules_wild, zhai_active)
            # Aggressive: bid close to expected, sometimes over
            qty = max(1, int(exp - self._add_noise(0.3, 0.5)))
            return {"action": "bid", "quantity": qty, "face": best_face, "is_zhai": False}

        bid_qty = current_bid["quantity"]
        bid_face = current_bid["face"]

        # Consider zhai as weapon: if I have lots of natives and few 1s
        ones = sum(1 for d in my_dice if d == 1)
        if (rules_zhai and not zhai_active and ones <= 1
                and self.difficulty > 0.4 and random.random() < 0.3):
            best_face = self._strongest_face(counts)
            native = sum(1 for d in my_dice if d == best_face)
            if native >= 3:
                zhai_qty = max(1, (bid_qty + 1) // 2)
                return {"action": "bid", "quantity": zhai_qty, "face": best_face, "is_zhai": True}

        my_c = counts.get(bid_face, 0)
        exp = expected_count(total, my_c, rules_wild, zhai_active)

        # Challenge threshold: more aggressive (lower threshold)
        threshold = self._add_noise(0.8, scale=0.3)
        if bid_qty > exp + threshold:
            return {"action": "challenge"}

        # Bluff sometimes (30%)
        bluff = random.random() < 0.3 * self.difficulty

        best_face = self._strongest_face(counts)
        best_c = counts[best_face]
        best_exp = expected_count(total, best_c, rules_wild, zhai_active)

        if bluff:
            # Jump bid on strongest face
            jump = random.randint(2, 3)
            qty = bid_qty + jump
            if qty <= total:
                return {"action": "bid", "quantity": qty, "face": best_face, "is_zhai": False}

        # Normal raise
        if best_face > bid_face:
            return {"action": "bid", "quantity": bid_qty, "face": best_face, "is_zhai": False}
        return {"action": "bid", "quantity": bid_qty + 1, "face": best_face, "is_zhai": False}


class FoxAI(AIStrategy):
    """Adaptive player. Baits opponents. Controlled bluffing. Reads patterns.

    ELO range: 1100-1500.
    """

    def __init__(self, difficulty: float = 0.8):
        super().__init__(difficulty)
        self.opponent_bid_history: list[dict] = []

    def decide(self, game_state: dict, my_dice: list[int],
               rules_wild: bool, rules_zhai: bool, zhai_active: bool) -> dict:
        total = game_state["total_dice"]
        current_bid = game_state.get("current_bid")
        counts = self._my_counts(my_dice, rules_wild, zhai_active)
        bid_history = game_state.get("bid_history", [])

        if current_bid is None:
            # Fishing: bid low on strong face to bait challenges
            best_face = self._strongest_face(counts)
            my_c = counts[best_face]
            exp = expected_count(total, my_c, rules_wild, zhai_active)
            # Deliberately low — looks weak but I'm strong
            qty = max(1, int(exp - 2.5))
            return {"action": "bid", "quantity": qty, "face": best_face, "is_zhai": False}

        bid_qty = current_bid["quantity"]
        bid_face = current_bid["face"]
        bidder = current_bid.get("bidder", "")

        my_c = counts.get(bid_face, 0)
        exp = expected_count(total, my_c, rules_wild, zhai_active)

        # Read opponent patterns from bid history
        opponent_aggressive = self._detect_aggression(bid_history, bidder)

        # Adjust challenge threshold based on opponent read
        base_threshold = 1.0
        if opponent_aggressive:
            base_threshold = 0.5  # More willing to challenge aggressive players
        else:
            base_threshold = 1.5

        if bid_qty > exp + base_threshold:
            return {"action": "challenge"}

        # Zhai as tactical weapon
        ones = sum(1 for d in my_dice if d == 1)
        if (rules_zhai and not zhai_active and ones == 0
                and random.random() < 0.4 * self.difficulty):
            best_face = self._strongest_face(counts)
            native = sum(1 for d in my_dice if d == best_face)
            if native >= 2:
                zhai_qty = max(1, (bid_qty + 1) // 2)
                return {"action": "bid", "quantity": zhai_qty, "face": best_face, "is_zhai": True}

        # Controlled bluff (15% but well-timed)
        best_face = self._strongest_face(counts)
        best_c = counts[best_face]
        best_exp = expected_count(total, best_c, rules_wild, zhai_active)

        if random.random() < 0.15 * self.difficulty and total >= 8:
            # Bluff on a face I have some of, not zero
            if best_c >= 2:
                qty = min(bid_qty + 2, int(best_exp + 1))
                return {"action": "bid", "quantity": qty, "face": best_face, "is_zhai": False}

        # Normal play: efficient raise
        if best_face > bid_face and bid_qty <= best_exp:
            return {"action": "bid", "quantity": bid_qty, "face": best_face, "is_zhai": False}

        raise_qty = bid_qty + 1
        if raise_qty <= best_exp + 0.5:
            return {"action": "bid", "quantity": raise_qty, "face": best_face, "is_zhai": False}

        return {"action": "challenge"}

    def _detect_aggression(self, bid_history: list[dict], player_name: str) -> bool:
        """Heuristic: is this player bidding aggressively?"""
        player_bids = [b for b in bid_history if b.get("player") == player_name]
        if len(player_bids) < 2:
            return False
        # Check for jump bids (quantity increase > 1)
        for i in range(1, len(player_bids)):
            if player_bids[i]["quantity"] - player_bids[i-1]["quantity"] > 1:
                return True
        return False


def create_ai(style: str, difficulty: float) -> AIStrategy:
    """Factory for AI opponents."""
    styles = {
        "conservative": ConservativeAI,
        "aggressive": AggressiveAI,
        "fox": FoxAI,
    }
    cls = styles.get(style, ConservativeAI)
    return cls(difficulty=difficulty)


def ai_decide(game, player_idx: int) -> dict:
    """Get AI decision for a given player in a game.

    Convenience wrapper that extracts the right state and calls the AI.
    """
    player = game.players[player_idx]
    if not player.is_ai:
        raise ValueError(f"{player.name} is not an AI player.")

    difficulty_map = {
        "conservative": max(0.3, min(1.0, 0.5 + game.round_number * 0.02)),
        "aggressive": max(0.4, min(1.0, 0.6 + game.round_number * 0.02)),
        "fox": max(0.6, min(1.0, 0.7 + game.round_number * 0.02)),
    }
    difficulty = difficulty_map.get(player.ai_style, 0.5)

    ai = create_ai(player.ai_style, difficulty)
    state = game.get_state_for_player(player_idx)

    return ai.decide(
        game_state=state,
        my_dice=player.dice,
        rules_wild=game.rules.wild_ones,
        rules_zhai=game.rules.zhai_enabled,
        zhai_active=game.zhai_active,
    )
