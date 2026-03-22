"""Drill/training question generator with difficulty ladder.

Levels:
1. Basic probability (should I challenge? N/3)
2. Opening bid (what should I call?)
3. Zhai scenarios (N/6, break-zhai)
4. Mixed (all of the above, harder numbers)
5. Multi-round strategy (position, reading bids)
"""
import random
from .probability import (
    expected_count, bid_probability, count_my_effective
)


def generate_drill(level: int, seed: int = None) -> dict:
    """Generate a training question at the given difficulty level.

    Returns dict with:
    - scenario: text description
    - question: what to answer
    - my_dice: list of ints
    - total_dice: int
    - current_bid: (qty, face) or None
    - zhai_active: bool
    - correct_answer: the mathematically correct answer
    - explanation: step-by-step explanation
    - shortcut: the N/3 or N/6 mental math
    """
    if seed is not None:
        random.seed(seed)

    generators = {
        1: _level1_basic_challenge,
        2: _level2_opening_bid,
        3: _level3_zhai,
        4: _level4_mixed,
        5: _level5_strategy,
    }
    gen = generators.get(min(level, 5), _level1_basic_challenge)
    return gen()


def _roll_dice(n: int = 5) -> list[int]:
    return sorted([random.randint(1, 6) for _ in range(n)])


def _level1_basic_challenge() -> dict:
    """Should you challenge this bid? (No zhai)"""
    total = random.choice([10, 12, 15, 18, 20])
    my_dice = _roll_dice()
    bid_face = random.randint(2, 6)

    my_count = count_my_effective(my_dice, bid_face, wild_ones=True, zhai=False)
    exp = expected_count(total, my_count, wild_ones=True, zhai=False)

    # Generate a bid that's sometimes over, sometimes under expected
    offset = random.choice([-1, 0, 1, 2, 3])
    bid_qty = max(1, int(exp + offset))

    prob = bid_probability(total, my_count, bid_qty, wild_ones=True, zhai=False)
    should_challenge = prob < 0.5

    # Shortcut calculation
    ones = sum(1 for d in my_dice if d == 1)
    native = sum(1 for d in my_dice if d == bid_face)
    unknown = total - 5
    shortcut = f"{unknown}/3 + {native} + {ones} = {unknown/3:.1f} + {native + ones} = {exp:.1f}"

    return {
        "level": 1,
        "scenario": f"Total dice: {total}. Your dice: {my_dice}. Someone bids {bid_qty}x{bid_face}.",
        "question": "Challenge (kai) or let it pass?",
        "my_dice": my_dice,
        "total_dice": total,
        "current_bid": (bid_qty, bid_face),
        "zhai_active": False,
        "correct_answer": "challenge" if should_challenge else "pass",
        "correct_answer_display": "KAI (challenge)" if should_challenge else "PASS (don't challenge)",
        "probability": prob,
        "expected": exp,
        "explanation": (
            f"Your {bid_face}s: {native} native + {ones} wild 1s = {my_count} effective.\n"
            f"Shortcut: {shortcut}\n"
            f"Expected total: {exp:.1f}. Bid is {bid_qty}.\n"
            f"P(bid is true) = {prob:.0%}.\n"
            f"{'Bid exceeds expected — challenge.' if should_challenge else 'Bid is within expected — let it pass.'}"
        ),
    }


def _level2_opening_bid() -> dict:
    """What should you bid to open?"""
    total = random.choice([10, 12, 15, 18, 20, 22])
    my_dice = _roll_dice()

    # Find strongest face
    counts = {}
    ones = sum(1 for d in my_dice if d == 1)
    for face in range(2, 7):
        native = sum(1 for d in my_dice if d == face)
        counts[face] = native + ones

    best_face = max(counts, key=counts.get)
    my_count = counts[best_face]
    exp = expected_count(total, my_count, wild_ones=True, zhai=False)
    native = sum(1 for d in my_dice if d == best_face)

    # Good opening: somewhat below expected
    good_qty = max(1, int(exp - 1.5))

    unknown = total - 5
    shortcut = f"{unknown}/3 + {native} + {ones} = {unknown/3:.1f} + {native + ones} = {exp:.1f}"

    return {
        "level": 2,
        "scenario": f"Total dice: {total}. Your dice: {my_dice}. You go first.",
        "question": "What do you bid?",
        "my_dice": my_dice,
        "total_dice": total,
        "current_bid": None,
        "zhai_active": False,
        "correct_answer": f"{good_qty}x{best_face}",
        "correct_answer_display": f"{good_qty}x{best_face} (or close)",
        "best_face": best_face,
        "expected": exp,
        "explanation": (
            f"Your strongest: {best_face}s ({native} native + {ones} wild = {my_count}).\n"
            f"Shortcut: {shortcut}\n"
            f"Expected total: {exp:.1f}.\n"
            f"Good opening: {good_qty}x{best_face} — leaves room to raise later."
        ),
    }


def _level3_zhai() -> dict:
    """Zhai scenario: N/6, break-zhai decisions."""
    total = random.choice([12, 14, 16, 18, 20])
    my_dice = _roll_dice()

    scenario_type = random.choice(["should_zhai", "under_zhai", "break_zhai"])

    if scenario_type == "should_zhai":
        # Do I have enough natives to benefit from calling zhai?
        counts_native = {}
        for face in range(2, 7):
            counts_native[face] = sum(1 for d in my_dice if d == face)
        best_face = max(counts_native, key=counts_native.get)
        native = counts_native[best_face]
        ones = sum(1 for d in my_dice if d == 1)

        exp_normal = expected_count(total, native + ones, True, False)
        exp_zhai = expected_count(total, native, True, True)

        should_zhai = native >= 3 and ones <= 1
        zhai_qty = max(1, int(exp_zhai - 0.5))

        unknown = total - 5
        return {
            "level": 3,
            "scenario": f"Total dice: {total}. Your dice: {my_dice}. Previous bid: {int(exp_normal - 1)}x{best_face}.",
            "question": "Should you call zhai? If yes, what bid?",
            "my_dice": my_dice,
            "total_dice": total,
            "current_bid": (int(exp_normal - 1), best_face),
            "zhai_active": False,
            "correct_answer": f"zhai {zhai_qty}x{best_face}" if should_zhai else "no zhai",
            "correct_answer_display": f"YES, zhai {zhai_qty}x{best_face}" if should_zhai else "NO — your 1s are too valuable",
            "expected_normal": exp_normal,
            "expected_zhai": exp_zhai,
            "explanation": (
                f"Natives of {best_face}: {native}. Wild 1s: {ones}.\n"
                f"Normal expected: {exp_normal:.1f}. Zhai expected ({unknown}/6 + {native}): {exp_zhai:.1f}.\n"
                f"{'Calling zhai: your 3+ natives stay, others lose their wilds. Advantage.' if should_zhai else 'Your 1s are working for you — zhai hurts you more than them.'}"
            ),
        }

    elif scenario_type == "under_zhai":
        # Someone called zhai. Should I challenge or bid?
        bid_face = random.randint(2, 6)
        native = sum(1 for d in my_dice if d == bid_face)
        exp = expected_count(total, native, True, True)

        offset = random.choice([0, 1, 2])
        bid_qty = max(1, int(exp + offset))
        prob = bid_probability(total, native, bid_qty, True, True)
        should_challenge = prob < 0.5

        unknown = total - 5
        return {
            "level": 3,
            "scenario": f"Total dice: {total}. Your dice: {my_dice}. ZHAI is active. Bid: {bid_qty}x{bid_face}.",
            "question": "Challenge or pass? (Remember: 1s are NOT wild under zhai)",
            "my_dice": my_dice,
            "total_dice": total,
            "current_bid": (bid_qty, bid_face),
            "zhai_active": True,
            "correct_answer": "challenge" if should_challenge else "pass",
            "correct_answer_display": "KAI" if should_challenge else "PASS",
            "probability": prob,
            "expected": exp,
            "explanation": (
                f"ZHAI active — 1s are just 1s, not wild.\n"
                f"Your {bid_face}s: {native} native only (1s don't count).\n"
                f"Expected ({unknown}/6 + {native}): {exp:.1f}. Bid is {bid_qty}.\n"
                f"P(bid true) = {prob:.0%}."
            ),
        }

    else:  # break_zhai
        bid_face = random.randint(2, 6)
        native = sum(1 for d in my_dice if d == bid_face)
        ones = sum(1 for d in my_dice if d == 1)

        prev_qty = random.randint(2, 4)
        break_qty = prev_qty + 2

        exp_zhai = expected_count(total, native, True, True)
        exp_normal = expected_count(total, native + ones, True, False)

        prob_break = bid_probability(total, native + ones, break_qty, True, False)
        should_break = prob_break > 0.5 and ones >= 2

        return {
            "level": 3,
            "scenario": f"Total dice: {total}. Your dice: {my_dice}. ZHAI active. Bid: {prev_qty}x{bid_face}. Break-zhai needs {break_qty}+.",
            "question": f"Break zhai with {break_qty}x{bid_face} (1s become wild again), or challenge?",
            "my_dice": my_dice,
            "total_dice": total,
            "current_bid": (prev_qty, bid_face),
            "zhai_active": True,
            "correct_answer": f"break {break_qty}x{bid_face}" if should_break else "challenge",
            "correct_answer_display": f"BREAK — {break_qty}x{bid_face}" if should_break else "KAI (challenge)",
            "probability": prob_break,
            "expected_after_break": exp_normal,
            "explanation": (
                f"Under zhai: {native} natives, expected {exp_zhai:.1f}.\n"
                f"If break: {native} + {ones} wilds = {native + ones}, expected {exp_normal:.1f}.\n"
                f"Need {break_qty}. P(>={break_qty} after break) = {prob_break:.0%}.\n"
                f"{'Your 1s come back to life — break is the counter-attack.' if should_break else 'Even with wilds back, the number is too high.'}"
            ),
        }


def _level4_mixed() -> dict:
    """Random mix of all previous levels with harder parameters."""
    level = random.choice([1, 1, 2, 3, 3])
    drill = generate_drill(level)
    drill["level"] = 4
    return drill


def _level5_strategy() -> dict:
    """Multi-round thinking: position and bid reading."""
    total = random.choice([15, 18, 20, 22])
    my_dice = _roll_dice()
    num_players = random.choice([3, 4, 5])

    # Simulate a bid history
    bids = []
    face = random.randint(2, 6)
    qty = random.randint(2, 4)
    players = [f"Player {i+1}" for i in range(num_players - 1)] + ["You"]

    for i in range(random.randint(2, 4)):
        p = players[i % len(players)]
        if p != "You":
            bids.append({"player": p, "quantity": qty, "face": face})
            if random.random() < 0.4:
                face = random.randint(2, 6)
            else:
                qty += 1

    my_count = count_my_effective(my_dice, face, True, False)
    exp = expected_count(total, my_count, True, False)
    prob = bid_probability(total, my_count, qty, True, False)

    bid_str = " -> ".join([f"{b['player']}: {b['quantity']}x{b['face']}" for b in bids])

    return {
        "level": 5,
        "scenario": f"{num_players} players, {total} total dice. Your dice: {my_dice}.\nBid history: {bid_str}\nCurrent bid: {qty}x{face}.",
        "question": "Your turn. What do you do and why?",
        "my_dice": my_dice,
        "total_dice": total,
        "current_bid": (qty, face),
        "zhai_active": False,
        "bid_history": bids,
        "correct_answer": "open-ended",
        "correct_answer_display": f"Expected {face}s: {exp:.1f}. P(bid true): {prob:.0%}.",
        "expected": exp,
        "probability": prob,
        "explanation": (
            f"Analysis:\n"
            f"Your {face}s: {my_count}. Expected total: {exp:.1f}. Current bid: {qty}.\n"
            f"P(bid true) = {prob:.0%}.\n"
            f"Read the bids: did anyone switch faces (weak on the old face)?\n"
            f"Did anyone jump (bluffing or strong)?\n"
            f"Your position matters — being after a potential bluffer is an advantage."
        ),
    }


def evaluate_answer(drill: dict, user_answer: str) -> dict:
    """Evaluate user's answer against the correct answer.

    Returns:
    - correct: bool
    - feedback: str
    """
    answer = user_answer.strip().lower()
    correct = drill["correct_answer"]

    if correct == "open-ended":
        return {
            "correct": None,
            "feedback": drill["explanation"],
        }

    if correct in ("challenge", "pass"):
        is_correct = (
            (correct == "challenge" and answer in ("challenge", "kai", "open", "call"))
            or (correct == "pass" and answer in ("pass", "no", "let"))
        )
    else:
        # For bids, be lenient with format
        is_correct = (
            answer.replace(" ", "").replace("x", "")
            in correct.replace(" ", "").replace("x", "").lower()
        ) or answer in correct.lower()

    return {
        "correct": is_correct,
        "feedback": drill["explanation"],
    }
