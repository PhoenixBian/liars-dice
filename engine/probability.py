"""Exact probability engine for Liar's Dice.

Uses binomial distribution for precise calculations.
The N/3 and N/6 shortcuts are teaching tools — this module is the source of truth.
"""
from math import comb


def _binomial_pmf(n: int, k: int, p: float) -> float:
    """P(X = k) for X ~ Binomial(n, p)."""
    if k < 0 or k > n:
        return 0.0
    return comb(n, k) * (p ** k) * ((1 - p) ** (n - k))


def _binomial_cdf_at_least(n: int, k: int, p: float) -> float:
    """P(X >= k) for X ~ Binomial(n, p)."""
    return sum(_binomial_pmf(n, i, p) for i in range(k, n + 1))


def dice_probability(wild_ones: bool, zhai: bool) -> float:
    """Probability that a single unknown die shows a target face value.

    Normal (wild_ones=True, zhai=False): 2/6 (target or 1)
    Zhai (zhai=True): 1/6 (only target, 1 is not wild)
    No wild ones (wild_ones=False): 1/6
    """
    if zhai or not wild_ones:
        return 1 / 6
    return 2 / 6


def expected_count(total_dice: int, my_count: int, wild_ones: bool = True,
                   zhai: bool = False) -> float:
    """Expected total count of a face value across all players.

    Args:
        total_dice: Total dice in play across all players.
        my_count: How many of the target value I have (including wild 1s if applicable).
        wild_ones: Whether 1s count as wild.
        zhai: Whether zhai is active (1s not wild).

    Returns:
        Expected total count.
    """
    unknown = total_dice - 5  # other players' dice (assuming I have 5)
    if unknown < 0:
        unknown = max(0, total_dice - my_count)
    p = dice_probability(wild_ones, zhai)
    return my_count + unknown * p


def bid_probability(total_dice: int, my_count: int, bid_quantity: int,
                    wild_ones: bool = True, zhai: bool = False) -> float:
    """Probability that a bid is true (actual count >= bid_quantity).

    Args:
        total_dice: Total dice in play.
        my_count: How many of the target I have (including applicable wilds).
        bid_quantity: The bid to evaluate.
        wild_ones: Whether 1s are wild.
        zhai: Whether zhai is active.

    Returns:
        Probability between 0.0 and 1.0.
    """
    unknown = total_dice - 5
    if unknown < 0:
        unknown = max(0, total_dice - my_count)

    needed_from_others = bid_quantity - my_count
    if needed_from_others <= 0:
        return 1.0  # I already have enough

    p = dice_probability(wild_ones, zhai)
    return _binomial_cdf_at_least(unknown, needed_from_others, p)


def optimal_decision(total_dice: int, my_dice: list[int], current_bid: tuple[int, int],
                     wild_ones: bool = True, zhai: bool = False) -> dict:
    """Analyze the optimal decision given current game state.

    Args:
        total_dice: Total dice in play.
        my_dice: List of my dice values (e.g., [1, 3, 3, 5, 6]).
        current_bid: (quantity, face_value) of the current bid.
        wild_ones: Whether 1s are wild.
        zhai: Whether zhai is active.

    Returns:
        Dict with analysis:
        - challenge_win_prob: probability of winning if I challenge
        - my_counts: dict of face -> count (with wilds applied)
        - best_raise: suggested raise if not challenging
        - expected_counts: expected total for each face
    """
    bid_qty, bid_face = current_bid

    # Count my dice
    raw_counts = {}
    for d in my_dice:
        raw_counts[d] = raw_counts.get(d, 0) + 1
    ones = raw_counts.get(1, 0)

    # Apply wilds
    my_counts = {}
    for face in range(1, 7):
        base = raw_counts.get(face, 0)
        if wild_ones and not zhai and face != 1:
            my_counts[face] = base + ones
        else:
            my_counts[face] = base

    # Probability the current bid is true
    my_count_for_bid = my_counts.get(bid_face, 0)
    bid_true_prob = bid_probability(total_dice, my_count_for_bid, bid_qty,
                                    wild_ones, zhai)
    challenge_win_prob = 1 - bid_true_prob

    # Expected counts for all faces
    expected = {}
    for face in range(1, 7):
        expected[face] = expected_count(total_dice, my_counts.get(face, 0),
                                        wild_ones, zhai)

    # Find best raise: the face where I have the most, bid just above expected
    best_raise = None
    best_margin = -999
    for face in range(1, 7):
        my_c = my_counts.get(face, 0)
        exp = expected[face]
        # Candidate bid: 1 above current if same face, or equal qty higher face
        if face == bid_face:
            raise_qty = bid_qty + 1
        elif face > bid_face:
            raise_qty = bid_qty
        else:
            raise_qty = bid_qty + 1

        margin = exp - raise_qty  # positive = safe
        if margin > best_margin:
            best_margin = margin
            best_raise = (raise_qty, face)

    return {
        "challenge_win_prob": challenge_win_prob,
        "bid_true_prob": bid_true_prob,
        "my_counts": my_counts,
        "expected_counts": expected,
        "best_raise": best_raise,
        "best_raise_margin": best_margin,
    }


def shortcut_expected(total_dice: int, my_native: int, my_wilds: int,
                      zhai: bool = False) -> float:
    """The N/3 (or N/6) shortcut for quick mental math.

    This is the teaching formula:
    - Normal: (total - 5) / 3 + my_native + my_wilds
    - Zhai:   (total - 5) / 6 + my_native

    Args:
        total_dice: Total dice in play.
        my_native: How many of the target face I have (not counting 1s).
        my_wilds: How many 1s I have (only counted if not zhai).
        zhai: Whether zhai is active.
    """
    unknown = max(0, total_dice - 5)
    if zhai:
        return unknown / 6 + my_native
    else:
        return unknown / 3 + my_native + my_wilds


def count_my_effective(my_dice: list[int], target_face: int,
                       wild_ones: bool = True, zhai: bool = False) -> int:
    """Count how many effective dice I have for a target face."""
    native = sum(1 for d in my_dice if d == target_face)
    if wild_ones and not zhai and target_face != 1:
        wilds = sum(1 for d in my_dice if d == 1)
        return native + wilds
    return native
