"""5-step tutorial engine for Liar's Dice beginners.

Extracted from the training conversation that validated this learning sequence:
Step 1: Rules (30s) -> Step 2: N/3 shortcut (2min) -> Step 3: Practice (3min)
-> Step 4: Zhai (2min) -> Step 5: First game vs Easy AI
"""


STEPS = {
    1: {
        "title": "The Rules (30 seconds)",
        "content": """
Liar's Dice is a bluffing game with dice.

SETUP: Everyone has 5 dice in a cup. Shake, peek at your own dice secretly.

PLAY: Take turns making bids about ALL dice on the table (not just yours).
A bid is "I think there are at least X dice showing Y across everyone."
Example: "5 threes" means you think there are at least 5 dice showing 3.

1s ARE WILD -- they count as whatever number is being bid.

Each bid must be HIGHER than the last:
- More dice of the same face (5 threes -> 6 threes)
- Same quantity but higher face (5 threes -> 5 fours)
- Or both

CHALLENGE (KAI): Instead of bidding higher, you can call "kai!" (open).
Everyone reveals their dice. Count the actual total.
- If the bid is met (actual >= bid): challenger loses a die.
- If the bid is NOT met (actual < bid): bidder loses a die.

Lose all your dice = you're out. Last person standing wins.
""",
        "question": "Got it? Say 'next' to learn the secret weapon -- instant probability math.",
        "expected": "next",
    },
    2: {
        "title": "The N/3 Shortcut (the only math you need)",
        "content": """
Here's the one formula that changes everything:

    Expected count of any face = (unknown dice) / 3 + your count

Why /3? Each unknown die has a 2/6 = 1/3 chance of being your target
(1/6 for the face itself + 1/6 for wild 1s).

EXAMPLE: 15 total dice. You have: [3, 3, 1, 5, 6]
- How many 3s total? Unknown = 15 - 5 = 10. Your 3s = 2 native + 1 wild = 3.
- Expected: 10/3 + 3 = 3.3 + 3 = 6.3

If someone bids "7 threes" -- that's above 6.3. Risky bid. Consider challenging.
If someone bids "5 threes" -- that's below 6.3. Safe bid. Don't challenge.

THE SHORTCUT IN YOUR HEAD:
1. Total dice minus 5 = unknown
2. Unknown divided by 3 = expected from others
3. Add your count (natives + wild 1s)
4. Compare to the bid. Above expected = consider challenging.
""",
        "question": "Let's try one. 18 total dice. Your dice: [2, 2, 1, 4, 6]. How many 2s expected?",
        "expected_answer_hint": "Unknown = 13. 13/3 = 4.3. Your 2s = 2 + 1 wild = 3. Total: 7.3",
    },
    3: {
        "title": "Practice Problems",
        "content": "Time to drill. I'll give you 3 scenarios, you decide: challenge or pass.",
        "drills": True,
        "num_drills": 3,
        "drill_level": 1,
    },
    4: {
        "title": "Zhai -- Stripping Wildcards",
        "content": """
ZHAI (literally "fasting" / stripping away):
A player can call zhai to REMOVE 1s as wildcards. After zhai, 1 is just 1.

THE MATH CHANGES:
- Normal: expected = unknown / 3 + (natives + wilds)
- Zhai:   expected = unknown / 6 + natives only

That's it -- denominator goes from 3 to 6. Expected count is roughly HALVED.

WHEN TO CALL ZHAI:
- You have many natives (3+) and few 1s (0-1)
- Zhai kills everyone else's wild 1s but your natives stay strong

WHEN NOT TO CALL ZHAI:
- You have lots of 1s -- they're working for you, don't kill them

BREAKING ZHAI:
- Add 2 to the quantity to break zhai. 1s become wild again.
- This is a counter-attack: if you have lots of 1s, breaking zhai brings them back.
""",
        "question": "One zhai drill to make sure you've got it.",
        "drills": True,
        "num_drills": 1,
        "drill_level": 3,
    },
    5: {
        "title": "Your First Game",
        "content": """
You know the rules, you can calculate expected values, you understand zhai.
Time to play. I'll be your opponent -- an Easy AI to start.

Remember:
- Calculate N/3 before every decision
- Bid on your strongest face
- Challenge when the bid exceeds your expected count
- Have fun. The math becomes automatic with practice.
""",
        "starts_game": True,
        "game_config": {
            "opponent_style": "conservative",
            "opponent_difficulty": "easy",
            "players": 2,
        },
    },
}


def get_step(step_number: int) -> dict:
    """Get tutorial step content."""
    return STEPS.get(step_number, STEPS[1])


def total_steps() -> int:
    return len(STEPS)


def format_step(step_number: int) -> str:
    """Format a tutorial step for display."""
    step = get_step(step_number)
    header = f"--- TUTORIAL Step {step_number}/{total_steps()}: {step['title']} ---"
    content = step.get("content", "")
    question = step.get("question", "")

    parts = [header, content]
    if question:
        parts.append(question)

    return "\n".join(parts)
