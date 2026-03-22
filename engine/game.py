"""Game state machine for Liar's Dice.

Supports 2-6 players, zhai/break-zhai, variable dice counts.
All game state is serializable to JSON for persistence.
"""
import json
import random
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional



class GamePhase(str, Enum):
    SETUP = "setup"
    ROLLING = "rolling"
    BIDDING = "bidding"
    CHALLENGE = "challenge"
    REVEAL = "reveal"
    SETTLE = "settle"
    ROUND_END = "round_end"
    GAME_OVER = "game_over"


@dataclass
class Player:
    name: str
    dice_count: int = 5
    dice: list[int] = field(default_factory=list)
    is_ai: bool = False
    ai_style: str = ""  # conservative, aggressive, fox
    is_active: bool = True

    def roll(self):
        self.dice = [random.randint(1, 6) for _ in range(self.dice_count)]
        self.dice.sort()


@dataclass
class Bid:
    player_index: int
    quantity: int
    face: int
    is_zhai: bool = False
    breaks_zhai: bool = False


@dataclass
class RoundRecord:
    """Record of a single round for review."""
    round_number: int
    dice_per_player: dict[str, list[int]]  # player_name -> dice
    bids: list[dict]
    challenger: str
    challenged_bid: dict
    actual_count: int
    loser: str
    total_dice: int
    zhai_active: bool


class Rules:
    def __init__(self, wild_ones: bool = True, zhai_enabled: bool = True,
                 break_zhai_rule: str = "+2", dice_per_player: int = 5,
                 start_player: str = "random"):
        self.wild_ones = wild_ones
        self.zhai_enabled = zhai_enabled
        self.break_zhai_rule = break_zhai_rule  # "+2", "double", "none"
        self.dice_per_player = dice_per_player
        self.start_player = start_player


class Game:
    def __init__(self, players: list[Player], rules: Optional[Rules] = None):
        self.players = players
        self.rules = rules or Rules()
        self.phase = GamePhase.SETUP
        self.current_player_idx = 0
        self.bids: list[Bid] = []
        self.zhai_active = False
        self.round_number = 0
        self.round_records: list[RoundRecord] = []
        self.loser_starts_next = True

    @property
    def total_dice(self) -> int:
        return sum(p.dice_count for p in self.players if p.is_active)

    @property
    def active_players(self) -> list[int]:
        return [i for i, p in enumerate(self.players) if p.is_active]

    @property
    def current_player(self) -> Player:
        return self.players[self.current_player_idx]

    @property
    def current_bid(self) -> Optional[Bid]:
        return self.bids[-1] if self.bids else None

    def start_round(self):
        """Start a new round: roll all dice, reset bids."""
        self.round_number += 1
        self.phase = GamePhase.ROLLING
        self.bids = []
        self.zhai_active = False

        for p in self.players:
            if p.is_active:
                p.roll()

        if self.round_number == 1:
            if self.rules.start_player == "random":
                self.current_player_idx = random.choice(self.active_players)
            else:
                self.current_player_idx = self.active_players[0]

        self.phase = GamePhase.BIDDING

    def validate_bid(self, quantity: int, face: int, is_zhai: bool = False) -> tuple[bool, str]:
        """Validate a bid before placing it.

        Returns (is_valid, error_message).
        """
        if face < 1 or face > 6:
            return False, "Face must be between 1 and 6."

        if quantity < 1:
            return False, "Quantity must be at least 1."

        if quantity > self.total_dice:
            return False, f"Quantity cannot exceed total dice ({self.total_dice})."

        if is_zhai and not self.rules.zhai_enabled:
            return False, "Zhai is not enabled in these rules."

        prev = self.current_bid

        if prev is None:
            # First bid of the round: anything goes
            return True, ""

        if is_zhai and not self.zhai_active:
            # Calling zhai: quantity must be >= ceil(prev.quantity / 2)
            min_qty = (prev.quantity + 1) // 2
            if quantity < min_qty:
                return False, f"Zhai bid must be at least {min_qty} (half of {prev.quantity}, rounded up)."
            self.zhai_active = True
            return True, ""

        if self.zhai_active and not is_zhai:
            # Breaking zhai: need to add 2 (or double, depending on rules)
            if self.rules.break_zhai_rule == "+2":
                min_qty = prev.quantity + 2
            elif self.rules.break_zhai_rule == "double":
                min_qty = prev.quantity * 2
            else:
                return False, "Cannot break zhai with these rules."

            if quantity < min_qty:
                return False, f"To break zhai, quantity must be at least {min_qty}."
            return True, ""

        # Normal bid: must be higher
        if quantity > prev.quantity:
            return True, ""
        if quantity == prev.quantity and face > prev.face:
            return True, ""

        return False, f"Bid must be higher than {prev.quantity}x{prev.face}."

    def place_bid(self, quantity: int, face: int, is_zhai: bool = False) -> tuple[bool, str]:
        """Place a bid for the current player.

        Returns (success, message).
        """
        valid, msg = self.validate_bid(quantity, face, is_zhai)
        if not valid:
            return False, msg

        breaks_zhai = self.zhai_active and not is_zhai
        if is_zhai:
            self.zhai_active = True
        if breaks_zhai:
            self.zhai_active = False

        bid = Bid(
            player_index=self.current_player_idx,
            quantity=quantity,
            face=face,
            is_zhai=is_zhai,
            breaks_zhai=breaks_zhai,
        )
        self.bids.append(bid)

        # Advance to next active player
        self._advance_player()
        return True, ""

    def challenge(self) -> dict:
        """Current player challenges the last bid.

        Returns dict with result details.
        """
        if not self.bids:
            return {"error": "No bid to challenge."}

        self.phase = GamePhase.CHALLENGE
        last_bid = self.current_bid
        challenger_idx = self.current_player_idx
        bidder_idx = last_bid.player_index

        # Count actual dice
        actual = self._count_all(last_bid.face)

        bid_met = actual >= last_bid.quantity
        loser_idx = challenger_idx if bid_met else bidder_idx
        loser = self.players[loser_idx]

        # Record round
        dice_snapshot = {}
        for p in self.players:
            if p.is_active:
                dice_snapshot[p.name] = list(p.dice)

        record = RoundRecord(
            round_number=self.round_number,
            dice_per_player=dice_snapshot,
            bids=[{"player": self.players[b.player_index].name,
                   "quantity": b.quantity, "face": b.face,
                   "is_zhai": b.is_zhai, "breaks_zhai": b.breaks_zhai}
                  for b in self.bids],
            challenger=self.players[challenger_idx].name,
            challenged_bid={"quantity": last_bid.quantity, "face": last_bid.face},
            actual_count=actual,
            loser=loser.name,
            total_dice=self.total_dice,
            zhai_active=self.zhai_active,
        )
        self.round_records.append(record)

        # Settle: loser loses 1 die
        loser.dice_count -= 1
        if loser.dice_count <= 0:
            loser.is_active = False

        # Check game over
        if len(self.active_players) <= 1:
            self.phase = GamePhase.GAME_OVER
            winner_idx = self.active_players[0] if self.active_players else None
            winner = self.players[winner_idx].name if winner_idx is not None else None
        else:
            self.phase = GamePhase.ROUND_END
            winner = None
            # Loser starts next round (if still active)
            if loser.is_active:
                self.current_player_idx = loser_idx
            else:
                self._advance_player()

        return {
            "challenger": self.players[challenger_idx].name,
            "bidder": self.players[bidder_idx].name,
            "bid": f"{last_bid.quantity}x{last_bid.face}",
            "actual_count": actual,
            "bid_met": bid_met,
            "loser": loser.name,
            "loser_dice_remaining": loser.dice_count,
            "all_dice": dice_snapshot,
            "game_over": self.phase == GamePhase.GAME_OVER,
            "winner": winner,
            "round_record": record,
        }

    def _count_all(self, face: int) -> int:
        """Count total dice showing a face across all active players."""
        total = 0
        for p in self.players:
            if not p.is_active:
                continue
            for d in p.dice:
                if d == face:
                    total += 1
                elif d == 1 and self.rules.wild_ones and not self.zhai_active and face != 1:
                    total += 1
        return total

    def _advance_player(self):
        """Move to the next active player."""
        active = self.active_players
        if not active:
            return
        current_pos = active.index(self.current_player_idx) if self.current_player_idx in active else 0
        next_pos = (current_pos + 1) % len(active)
        self.current_player_idx = active[next_pos]

    def get_state_for_player(self, player_idx: int) -> dict:
        """Get game state visible to a specific player."""
        p = self.players[player_idx]
        return {
            "phase": self.phase.value,
            "round": self.round_number,
            "your_dice": list(p.dice),
            "your_dice_count": p.dice_count,
            "total_dice": self.total_dice,
            "current_bid": {"quantity": self.current_bid.quantity,
                           "face": self.current_bid.face,
                           "bidder": self.players[self.current_bid.player_index].name,
                           "is_zhai": self.current_bid.is_zhai} if self.current_bid else None,
            "zhai_active": self.zhai_active,
            "is_your_turn": self.current_player_idx == player_idx,
            "players": [{"name": pl.name, "dice_count": pl.dice_count,
                        "is_active": pl.is_active} for pl in self.players],
            "bid_history": [{"player": self.players[b.player_index].name,
                            "quantity": b.quantity, "face": b.face,
                            "is_zhai": b.is_zhai} for b in self.bids],
        }

    def to_json(self) -> str:
        """Serialize game state to JSON for persistence."""
        state = {
            "players": [{"name": p.name, "dice_count": p.dice_count,
                        "dice": p.dice, "is_ai": p.is_ai,
                        "ai_style": p.ai_style, "is_active": p.is_active}
                       for p in self.players],
            "phase": self.phase.value,
            "current_player_idx": self.current_player_idx,
            "zhai_active": self.zhai_active,
            "round_number": self.round_number,
            "bids": [{"player_index": b.player_index, "quantity": b.quantity,
                      "face": b.face, "is_zhai": b.is_zhai,
                      "breaks_zhai": b.breaks_zhai} for b in self.bids],
            "rules": {
                "wild_ones": self.rules.wild_ones,
                "zhai_enabled": self.rules.zhai_enabled,
                "break_zhai_rule": self.rules.break_zhai_rule,
                "dice_per_player": self.rules.dice_per_player,
                "start_player": self.rules.start_player,
            },
        }
        return json.dumps(state, ensure_ascii=False, indent=2)

    @classmethod
    def from_json(cls, data: str) -> "Game":
        """Restore game from JSON."""
        state = json.loads(data)
        rules = Rules(**state["rules"])
        players = [Player(name=p["name"], dice_count=p["dice_count"],
                         dice=p["dice"], is_ai=p["is_ai"],
                         ai_style=p["ai_style"], is_active=p["is_active"])
                  for p in state["players"]]
        game = cls(players, rules)
        game.phase = GamePhase(state["phase"])
        game.current_player_idx = state["current_player_idx"]
        game.zhai_active = state["zhai_active"]
        game.round_number = state["round_number"]
        game.bids = [Bid(**b) for b in state["bids"]]
        return game
