# Liar's Dice Trainer

Train your Liar's Dice skills with AI. Calculate probabilities instantly, play against opponents with different personalities, track your ELO rating, and dominate game night.

A [Claude Code](https://docs.anthropic.com/en/docs/claude-code) skill. No web UI, no app — just you and Claude in the terminal.

## What is Liar's Dice?

A bluffing game with dice. Everyone shakes a cup, peeks at their own dice secretly, and takes turns bidding on how many of a certain number exist across ALL players' dice. Bid higher or call "bullshit." Whoever is wrong loses a die. Last player standing wins.

Popular at bars, parties, and poker tables. Featured in Pirates of the Caribbean. Known as "Chui Niu" in Chinese.

## Why a trainer?

The difference between losing and winning is one formula: **N/3**. Expected count of any face = (unknown dice) / 3 + your count. Once you internalize this, you stop guessing and start calculating — in seconds, while everyone else is going on vibes.

This skill teaches you that formula, drills it until it's automatic, then throws you into games against AI opponents who bluff, bait, and punish mistakes.

## Install (30 seconds)

**Requirements:** [Claude Code](https://docs.anthropic.com/en/docs/claude-code), Python 3.8+

```bash
git clone https://github.com/PhoenixBian/liars-dice.git ~/.claude/skills/liars-dice
cd ~/.claude/skills/liars-dice && chmod +x setup && ./setup
```

Then in Claude Code, type `/liars-dice` or `/bluff`.

## Modes

### Tutorial (5 min)
Learn from zero. Rules, the N/3 shortcut, practice problems, zhai mechanics, first game.

### Drill
Timed probability questions. "15 total dice, your hand is [1,3,3,5,6], someone bids 7x3. Challenge or pass?" Instant feedback with full math breakdown. Difficulty auto-scales as you improve.

**5 levels:** Basic challenge -> Opening bids -> Zhai scenarios -> Mixed -> Multi-round strategy

### Play
Full games against AI opponents:

| Style | Personality | ELO Range |
|-------|-------------|-----------|
| Conservative | Plays safe, rarely bluffs | 800-1000 |
| Aggressive | Jump-bids, uses zhai as weapon, bluffs 30% | 900-1200 |
| Fox | Adapts, baits, controlled bluffing, reads your patterns | 1100-1500 |

Supports 2-6 players (you + AI opponents). Auto-matchmaking by your ELO.

### Review
Post-game analysis. Every round, every decision:
- Your play vs. mathematically optimal play
- Expected values at each decision point
- Critical mistakes that decided the outcome

## ELO System

Start at 1000. Win against harder opponents = bigger gains. K-factor: 32 (first 50 games), 16 after. Track your progress over time.

## Chinese Rules (Zhai)

This trainer supports the Chinese variant rules:

- **Zhai** (literally "fasting"): Strip 1s as wildcards. Changes expected value from N/3 to N/6.
- **Break-zhai**: Add 2 to break zhai and restore 1s as wild.
- **When to zhai**: You have 3+ natives and few 1s. Your opponents' wilds die but your natives stay.
- **When to break**: You have lots of 1s. Breaking brings your wilds back to life.

## How it works

Pure Python engine, no dependencies beyond Python 3 stdlib:

- `engine/probability.py` — Exact binomial distribution. The N/3 shortcut is for humans; the engine uses real math.
- `engine/game.py` — Full game state machine. 2-6 players, zhai/break-zhai, serializable to JSON.
- `engine/ai_opponents.py` — Three AI personalities with configurable difficulty and controlled imperfection.
- `engine/trainer.py` — Drill generator with 5 difficulty levels and auto-progression.
- `engine/elo.py` — ELO rating, progress tracking, match history.
- `engine/tutorial.py` — 5-step learning flow extracted from a real training conversation.

All state persists to `~/.liars-dice/progress.json`. No network calls, no telemetry, no accounts.

## Auto-update

The skill checks for updates once per hour (when invoked). To update manually:

```bash
cd ~/.claude/skills/liars-dice && git pull
```

## License

MIT

---

Built with Claude Code. The AI that taught me to count dice now teaches you.

---

# Liar's Dice Trainer (Chinese)

AI 吹牛骰子训练器。学概率、练计算、打 AI、涨 ELO。

## 安装

```bash
git clone https://github.com/PhoenixBian/liars-dice.git ~/.claude/skills/liars-dice
cd ~/.claude/skills/liars-dice && chmod +x setup && ./setup
```

在 Claude Code 里输入 `/liars-dice` 或 `/bluff`。

## 核心公式

**期望值 = (未知骰子数) / 3 + 你手上的数量**

正常情况除以 3（每颗骰子 2/6 概率），斋了之后除以 6（1 不再万能）。

## 四种模式

- **教学**：5 分钟从零学会
- **训练**：做题练速算，5 个难度梯度，正确率 80% 自动升级
- **对局**：打 AI（保守/激进/老狐狸），2-6 人，按 ELO 自动匹配
- **复盘**：逐手分析，你的选择 vs 数学最优解

## 斋的规则

- 叫斋：1 不再万能，期望值砍半（N/6）
- 破斋：加 2 恢复万能
- 什么时候叫斋：手上本体多、1 少
- 什么时候破斋：手上 1 多，破了之后 1 复活
