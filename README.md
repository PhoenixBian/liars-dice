# liars-dice

I'm a 25-year-old creator building in public. This is my first open-source project.

It started with a conversation. I was chatting with Claude about Liar's Dice — the drinking game where you shake dice in a cup and bluff about what's on the table. I wanted to get better at it. Not "read a strategy guide" better. Actually better. The kind of better where you're three beers in and still calculating faster than everyone at the table.

So Claude taught me. And somewhere in that conversation, something clicked.

**There is exactly one formula that separates winners from losers in Liar's Dice:**

```
Expected count = (unknown dice) / 3 + your count
```

That's it. Every decision in the game — bid, challenge, bluff, zhai — flows from this one number. Unknown dice divided by 3, plus what you already have. You can do it drunk. You can do it in two seconds. And once you can, you're not guessing anymore. You're calculating while everyone else is vibing.

I went from not knowing this formula to solving probability drills in my head in about 20 minutes. Then I thought: **this entire learning path — the formula, the drills, the practice games — could be a tool.**

So I built it.

## What this is

A [Claude Code](https://docs.anthropic.com/en/docs/claude-code) skill that turns your terminal into a Liar's Dice training ground. No app to download, no website to visit. You type `/liars-dice` in Claude Code and start playing.

Four modes:

**Tutorial** — Learn from zero in 5 minutes. I extracted the exact teaching sequence from my own training conversation: rules, the N/3 shortcut, three practice problems, zhai mechanics, then your first real game. This sequence works because I was the test subject.

**Drill** — "15 total dice, your hand is [1, 3, 3, 5, 6], someone bids 7x3. Challenge or pass?" You answer, it tells you if you're right, shows the full math, tracks your accuracy. Five difficulty levels that auto-advance when you hit 80%. The goal is to make the math feel like breathing.

**Play** — Full games against AI opponents with actual personalities:

| | Conservative | Aggressive | Fox |
|---|---|---|---|
| **Vibe** | Your cautious friend | The guy who slams the table | The one who smiles before winning |
| **Bluff rate** | 0% | 30% | 15% but surgically precise |
| **Zhai usage** | Almost never | Weaponized | Tactical |
| **ELO range** | 800-1000 | 900-1200 | 1100-1500 |

2-6 players. Auto-matchmaking based on your ELO. The Fox will read your bidding patterns and exploit them. Good luck.

**Review** — Post-game breakdown of every decision you made. "You challenged 7x3. Expected was 6.3. Challenge was correct, 56% win probability. But you could have raised to 7x5 — your strongest face — with 71% safety margin." This is where you actually get better.

## The origin story (for real)

Here's the actual conversation flow that became this tool:

1. I asked Claude to teach me Liar's Dice probability
2. Claude gave me the N/3 formula
3. I solved 6 practice problems and the shortcut became automatic
4. Claude taught me zhai (the Chinese variant where 1s stop being wild)
5. I learned aggressive strategies — jump-bidding, fishing, zhai as a weapon
6. I asked "can we simulate a game?"
7. Then I realized: **this entire sequence is the product**

The tutorial isn't designed by a game designer. It's extracted from a real learning session. Every step exists because it worked on me.

## Chinese rules: Zhai

Most Liar's Dice implementations only cover Western rules. This one supports the Chinese variant — **zhai** (literally "fasting"):

**Normal:** 1s are wild. Expected count = N/3. You're counting natives + wilds.

**Zhai:** Someone strips the wildcards. 1s become just 1s. Expected count drops to N/6. Everything you thought you knew about the board just got cut in half.

**Break-zhai:** Add 2 to the quantity. 1s come back to life. This is the counter-attack — if you have three 1s that just got killed by zhai, breaking it brings your army back.

**When to call zhai:** You have 3+ natives of one face and 0-1 ones. Your opponents' wilds die but your natives don't care.

**When NOT to call zhai:** You have lots of 1s. You'd be shooting yourself.

This mechanic adds an entire layer of strategy that doesn't exist in the Western version. It's the reason Chinese Liar's Dice is a deeper game.

## ELO tracking

You start at 1000. Every game adjusts your rating based on the AI's difficulty. Beat a Fox at Hard? Big gains. Lose to a Conservative at Easy? Big drop. K-factor starts at 32 for your first 50 games, drops to 16 after.

Your progress persists across sessions in `~/.liars-dice/progress.json`. Watch yourself go from 1000 to 1200+ over a week of practice.

## Install

**Requirements:** [Claude Code](https://docs.anthropic.com/en/docs/claude-code), Python 3.8+

```bash
git clone https://github.com/PhoenixBian/liars-dice.git ~/.claude/skills/liars-dice
cd ~/.claude/skills/liars-dice && chmod +x setup && ./setup
```

Type `/liars-dice` or `/bluff` in Claude Code. That's it.

Updates: the skill checks for new versions automatically. Or `cd ~/.claude/skills/liars-dice && git pull`.

## Under the hood

Pure Python, zero external dependencies. Everything runs on Python 3 stdlib.

```
engine/
  probability.py   — Exact binomial distribution (the N/3 shortcut is for humans;
                      the engine uses real math to grade your answers)
  game.py          — Full state machine: 2-6 players, zhai/break-zhai,
                      serializable to JSON for mid-game saves
  ai_opponents.py  — Three personalities with tunable difficulty and
                      controlled imperfection (perfect AI isn't fun to play)
  trainer.py       — Drill generator, 5 difficulty levels, auto-progression
  elo.py           — Rating system, match history, progress curves
  tutorial.py      — The 5-step learning flow, extracted verbatim from
                      the conversation that started all of this
```

No network calls. No telemetry. No accounts. Your data stays on your machine.

## Why Building in Public

I'm building my AI-augmented life in public. This is project #1.

The thesis: **AI doesn't replace skill — it compresses the learning curve.** I went from "I don't know the math" to "I can calculate expected values while holding a beer" in one conversation. Then I turned that conversation into a tool that lets anyone else do the same thing.

Every project I ship will follow this pattern: learn something with AI, extract the learning into a reusable tool, open-source it. The AI did the teaching. I did the learning. Now the tool does both.

Follow the journey: [@PhoenixBian](https://github.com/PhoenixBian)

## License

MIT. Fork it, improve it, bring it to your next game night.

---

**The AI that taught me to count dice now teaches you.**

---

# liars-dice (Chinese)

AI 吹牛骰子训练器。

这个项目的起点是一次对话。我跟 Claude 聊吹牛骰子，想搞明白概率怎么算。结果 20 分钟之内，我从完全不会算变成了能秒算期望值。然后我意识到：这个学习路径本身就是产品。

## 核心公式

```
期望值 = (未知骰子数) / 3 + 你手上的数量
```

正常情况除以 3，斋了之后除以 6。一个公式，所有决策的基础。

## 安装

```bash
git clone https://github.com/PhoenixBian/liars-dice.git ~/.claude/skills/liars-dice
cd ~/.claude/skills/liars-dice && chmod +x setup && ./setup
```

在 Claude Code 里输入 `/liars-dice` 或 `/bluff`。

## 四种模式

**教学** — 5 分钟从零学会。规则 -> N/3 公式 -> 做题 -> 斋 -> 第一局实战。

**训练** — 出题、做题、讲解。5 个难度梯度，正确率到 80% 自动升级。目标：让概率计算变成条件反射。

**对局** — 三种 AI 性格：保守（从不虚张声势）、激进（爱跳叫、会叫斋、30% 概率吹牛）、老狐狸（会钓鱼、会读你的出价模式、15% 精准虚张声势）。2-6 人，按 ELO 自动匹配。

**复盘** — 逐手分析。你的选择 vs 数学最优解 vs AI 的选择。每一手都算期望值和胜率。

## 斋

大部分吹牛骰子工具只支持西方规则。这个支持中国规则——斋。

- **叫斋**：1 不再万能，期望值从 N/3 砍到 N/6
- **破斋**：加 2，1 恢复万能
- **什么时候叫**：手上本体多（3+）、1 少（0-1）
- **什么时候不叫**：手上 1 多，叫了等于自杀

斋让吹牛骰子多了一整层博弈。这是中国版本比西方版本更深的原因。

## Building in Public

这是我的第一个开源项目。核心逻辑：**AI 不替代技能，AI 压缩学习曲线。** 用 AI 学会一样东西，把学习过程提取成工具，开源。AI 做教学，我做学习，工具做两者。
