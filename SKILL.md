---
name: liars-dice
version: 0.1.0
description: |
  Liar's Dice training skill. Practice probability math, play against AI opponents
  with different personalities, track your ELO rating, and get better at the world's
  best drinking game. Supports Chinese rules including zhai (stripping wildcards)
  and break-zhai (+2 to restore).

  Four modes:
  - Tutorial: Learn from zero in 5 minutes
  - Drill: Practice probability calculations with instant feedback
  - Play: Full games against AI (Conservative/Aggressive/Fox)
  - Review: Post-game analysis of every decision

  Also: /bluff, /liars-dice
allowed-tools:
  - Bash
  - Read
  - AskUserQuestion
---

## Preamble (run first)

```bash
_LD_DIR="${LD_DIR:-$(find ~/.claude/skills -maxdepth 1 -name 'liars-dice' -type d 2>/dev/null | head -1)}"
[ -z "$_LD_DIR" ] && _LD_DIR="$(find .claude/skills -maxdepth 1 -name 'liars-dice' -type d 2>/dev/null | head -1)"
_UPD=$("$_LD_DIR/bin/ld-update-check" 2>/dev/null || true)
[ -n "$_UPD" ] && echo "$_UPD" || true
mkdir -p ~/.liars-dice/sessions
touch ~/.liars-dice/sessions/"$PPID"
find ~/.liars-dice/sessions -mmin +120 -type f -delete 2>/dev/null || true
echo "LD_DIR: $_LD_DIR"
echo "VERSION: $(cat "$_LD_DIR/VERSION" 2>/dev/null || echo unknown)"
python3 -c "
import sys; sys.path.insert(0, '$_LD_DIR')
from engine.elo import get_stats
s = get_stats()
print(f'ELO: {s[\"elo\"]} | Games: {s[\"games_played\"]} (W{s[\"games_won\"]}) | Drills: {s[\"drills_completed\"]} ({s[\"drill_accuracy\"]:.0%}) | Level: {s[\"current_drill_level\"]}')
print(f'Tutorial: {\"done\" if s[\"tutorial_completed\"] else \"not started\"}')" 2>/dev/null || echo "Engine not ready — run setup"
```

If output shows `UPGRADE_AVAILABLE <old> <new>`: tell user "liars-dice v{new} is available (you're on v{old}). Run `cd ~/.claude/skills/liars-dice && git pull` to update."

## Mode Routing

Detect user intent and route to the appropriate mode:

| User says | Mode |
|-----------|------|
| "tutorial", "learn", "teach me", "how to play" | TUTORIAL |
| "drill", "practice", "train", "quiz" | DRILL |
| "play", "game", "match", "let's go", "deal" | PLAY |
| "review", "analyze", "what happened", "replay" | REVIEW |
| "stats", "elo", "progress", "how am I doing" | STATS |
| "bip", "building in public", "content" | BIP |
| Just `/liars-dice` or `/bluff` with no args | Show menu via AskUserQuestion |

When routing is ambiguous, show the menu:

```
Welcome to Liar's Dice Trainer!

Your stats: ELO {elo} | {games} games | {win_rate}% win rate

What do you want to do?
A) Tutorial — Learn from zero (5 min)
B) Drill — Practice probability math
C) Play — Game against AI
D) Stats — See your progress
```

## TUTORIAL Mode

Run the 5-step tutorial from `engine/tutorial.py`:

```bash
python3 -c "
import sys; sys.path.insert(0, '$_LD_DIR')
from engine.tutorial import format_step
print(format_step(STEP_NUMBER))
"
```

For each step:
1. Display the step content using `format_step(N)`
2. If the step has `drills: True`, generate drills using `engine/trainer.py` at the specified level
3. If the step has `starts_game: True`, transition to PLAY mode with the specified config
4. Wait for user response before advancing

After Step 5 (first game), mark tutorial complete:
```bash
python3 -c "
import sys; sys.path.insert(0, '$_LD_DIR')
from engine.elo import load_progress, save_progress
p = load_progress(); p['tutorial_completed'] = True; save_progress(p)
"
```

## DRILL Mode

Generate and present training questions:

```bash
python3 -c "
import sys, json; sys.path.insert(0, '$_LD_DIR')
from engine.trainer import generate_drill
from engine.elo import load_progress
p = load_progress()
drill = generate_drill(p['current_drill_level'])
print(json.dumps(drill, ensure_ascii=False, indent=2))
"
```

Flow:
1. Generate a drill at the user's current level
2. Present the scenario and question to the user
3. Wait for their answer
4. Evaluate and show feedback:

```bash
python3 -c "
import sys, json; sys.path.insert(0, '$_LD_DIR')
from engine.trainer import generate_drill, evaluate_answer
from engine.elo import record_drill
drill = json.loads('''DRILL_JSON''')
result = evaluate_answer(drill, 'USER_ANSWER')
record = record_drill(result['correct'], drill['level'])
print(json.dumps({'result': result, 'progress': record}, ensure_ascii=False, indent=2))
"
```

5. Show whether they were correct, the full explanation, and their updated accuracy
6. Ask if they want another drill or want to switch modes

Present drills conversationally, not as raw JSON. Example:

> **Drill (Level 1)**
> Total dice: 15. Your dice: [1, 2, 2, 3, 6]. Someone bids 7x2.
> Challenge or pass?

After their answer:

> **Correct!** Your 2s: 2 native + 1 wild = 3. Expected: 10/3 + 3 = 6.3.
> Bid of 7 exceeds expected. Challenge wins ~56% of the time.
> Accuracy: 80% (4/5) | Level 1

## PLAY Mode

### Setup

Ask user preferences via AskUserQuestion:
- Number of players (2-6)
- AI difficulty (auto-match by ELO, or manual: easy/medium/hard)
- AI style (conservative/aggressive/fox, or "surprise me")
- Rules (standard with zhai, or customize)

If "auto-match" or no preference, use `get_ai_difficulty_for_elo()`.

### Game Loop

```bash
python3 -c "
import sys, json; sys.path.insert(0, '$_LD_DIR')
from engine.game import Game, Player, Rules

# Create game (example: 1v1 vs conservative)
players = [
    Player('You'),
    Player('Bot', is_ai=True, ai_style='conservative'),
]
game = Game(players)
game.start_round()
state = game.get_state_for_player(0)
print(json.dumps(state, ensure_ascii=False, indent=2))
"
```

Each round:
1. Show the user their dice and game state
2. If it's the user's turn: ask for their bid or challenge
3. If it's an AI's turn: run `ai_decide()` and narrate the AI's action
4. On challenge: show all dice, who lost, update scores
5. If game over: record result with `record_game()`

Present the game conversationally. Example:

> **Round 3** | Total dice: 8 (You: 4, Bot: 4)
> Your dice: [1, 3, 3, 5]
>
> Bot bids: 3x5
>
> Your turn. Bid higher or challenge (kai)?

After a challenge:

> **KAI!** Everyone reveals:
> You: [1, 3, 3, 5] | Bot: [2, 5, 5, 6]
>
> Count of 5s: You have 1 (5) + 1 (wild 1) = 2. Bot has 2. Total: 4.
> Bid was 3x5. Actual is 4. Bid met — you lose a die!
>
> Score: You 3 dice, Bot 4 dice.

### AI Narration

Don't just say "Bot bids 4x3." Give personality:

- **Conservative**: "Bot cautiously raises to 4x3."
- **Aggressive**: "Bot slams the table — 7x3! Zhai!"
- **Fox**: "Bot pauses, smiles, and quietly says... 3x5."

### Game End

```bash
python3 -c "
import sys, json; sys.path.insert(0, '$_LD_DIR')
from engine.elo import record_game, get_stats
result = record_game(
    won=WON,
    opponent_style='STYLE',
    opponent_difficulty='DIFFICULTY',
    rounds=ROUNDS,
)
stats = get_stats()
print(json.dumps({**result, 'stats': stats}, ensure_ascii=False, indent=2))
"
```

Show ELO change and offer options:
- Play again (same settings)
- Play again (different opponent)
- Review this game
- Back to menu

## REVIEW Mode

After a game or on request, analyze the game round by round:

For each round in `game.round_records`:
1. Show all players' dice
2. Replay the bid sequence
3. For each bid, show:
   - The expected count at that point
   - Whether the bid was above/below expected
   - What the optimal play would have been
4. Highlight the critical mistake (if any) that decided the round

Focus on the user's decisions. For each user action:
```
YOUR PLAY: Challenge 7x3
EXPECTED:  6.3 (your 3s: 2 native + 1 wild = 3, unknown 10/3 = 3.3)
VERDICT:   Good call — bid exceeded expected by 0.7
OPTIMAL:   Challenge was correct (56% win probability)
```

## STATS Mode

Display progress dashboard:

```
=== Liar's Dice Progress ===
ELO: 1050 (+50 from start)
Games: 12 played, 7 won (58%)
Drills: 45 completed (82% accuracy)
Current Level: 3 (Zhai scenarios)

Recent ELO: 1000 -> 1020 -> 985 -> 1010 -> 1050
Best win: vs Fox AI (Hard) +24 ELO
```

## BIP (Building in Public) Mode

Generate shareable content:

```bash
python3 -c "
import sys; sys.path.insert(0, '$_LD_DIR')
from engine.elo import generate_bip_content
print(generate_bip_content())
"
```

Output ready-to-post content with ELO progress, win/loss record, and a link to the GitHub repo.

## Rules Reference (for Claude to use during games)

### Standard Rules
- Each player starts with 5 dice
- 1s are wild (count as any face)
- Bids must increase (higher quantity, or same quantity + higher face)
- Challenge (kai): if actual >= bid, challenger loses; if actual < bid, bidder loses
- Lose a die each time you lose a challenge
- Last player standing wins

### Zhai Rules
- A player may call "zhai" (strip wildcards)
- Under zhai: 1s only count as 1s, not wild
- Expected value formula changes from N/3 to N/6
- Zhai bid quantity must be at least ceil(previous_quantity / 2)

### Break-Zhai Rules
- To break zhai: add 2 to the current quantity
- After breaking: 1s become wild again, back to N/3
- This is a counter-attack for players with many 1s

### Probability Quick Reference
- Normal: expected = (total - 5) / 3 + my_count
- Zhai: expected = (total - 5) / 6 + my_natives_only
- Each die: 2/6 chance normal, 1/6 chance under zhai
