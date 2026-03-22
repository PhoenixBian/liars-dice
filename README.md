# liars-dice

我 25 岁，正在 Building in Public。这是第一个项目。

I'm 25, building in public. This is project #1.

---

起点是一次对话。我跟 Claude 聊吹牛骰子——就是酒桌上摇骰子猜大小那个游戏。我想变强，不是"看了攻略觉得自己变强了"那种，是三杯啤酒下肚还能比所有人算得快那种。

It started with a conversation. I was chatting with Claude about Liar's Dice — the drinking game where you shake dice and bluff. I wanted to actually get better. Three beers in, still calculating faster than everyone at the table better.

Claude 教了我。20 分钟之内，有个东西 click 了。

Claude taught me. In 20 minutes, something clicked.

**吹牛骰子里，赢和输之间只隔着一个公式：**

**There is exactly one formula that separates winners from losers:**

```
期望值 = (未知骰子数) / 3 + 你手上的数量
Expected count = (unknown dice) / 3 + your count
```

就这一个。叫、开、吹牛、斋——所有决策都从这个数字出发。未知骰子除以 3，加上你手上有的。喝醉了也能算。两秒钟能算完。算得出来之后，你就不是在猜了——你在算，而别人在猜。

That's it. Every decision — bid, challenge, bluff, zhai — flows from this number. You can do it drunk. You can do it in two seconds. Once you can, you're not guessing anymore. You're calculating while everyone else is vibing.

我从完全不会这个公式到脑子里秒算概率，花了大概 20 分钟。然后我想：**这个学习路径本身——公式、做题、打 AI——就是一个产品。**

I went from not knowing this formula to solving drills in my head in 20 minutes. Then I thought: **the entire learning path — formula, drills, games — is the product.**

于是我把它做出来了。

So I built it.

## 这是什么 / What this is

一个 [Claude Code](https://docs.anthropic.com/en/docs/claude-code) 技能。在终端里输入 `/liars-dice` 就能开始训练。不用下载 app，不用注册账号。

A Claude Code skill. Type `/liars-dice` in your terminal and start training. No app, no account.

四种模式 / Four modes:

**教学 Tutorial** — 5 分钟从零学会。教学顺序是从我自己的学习过程里直接提取的：规则 → N/3 公式 → 三道练习题 → 斋 → 第一局实战。这个顺序有效，因为我就是用这个顺序学会的。

Learn from zero in 5 minutes. The teaching sequence is extracted from my own training conversation. It works because I was the test subject.

**训练 Drill** — "全场 15 颗骰子，你的骰子是 [1, 3, 3, 5, 6]，有人叫 7 个 3。开不开？" 你回答，它告诉你对不对，展示完整计算过程，追踪正确率。5 个难度梯度，正确率到 80% 自动升级。目标：让概率计算变成条件反射。

Answer probability questions with instant feedback and full math breakdowns. 5 difficulty levels, auto-advance at 80% accuracy. Goal: make the math feel like breathing.

**对局 Play** — 打 AI。三种性格：

Full games against AI opponents with actual personalities:

| | 保守 Conservative | 激进 Aggressive | 老狐狸 Fox |
|---|---|---|---|
| **气质** Vibe | 你那个谨慎的朋友 | 拍桌子那个 | 赢之前先笑一下的那个 |
| **吹牛率** Bluff | 0% | 30% | 15%，但刀刀见血 |
| **斋的使用** Zhai | 几乎不叫 | 当武器用 | 战术性叫 |
| **ELO** | 800-1000 | 900-1200 | 1100-1500 |

2-6 人，按 ELO 自动匹配。老狐狸会读你的出价模式然后针对你。祝好运。

2-6 players. Auto-matchmaking by ELO. The Fox reads your bidding patterns and exploits them. Good luck.

**复盘 Review** — 逐手分析你的每个决策。"你开了 7 个 3。期望值是 6.3。开对了，胜率 56%。但你其实可以叫 7 个 5——你最强的牌——安全边际 71%。" 这才是真正涨水平的地方。

Post-game breakdown of every decision. This is where you actually get better.

## 起源故事 / The origin story

这个工具是怎么来的——就是下面这 7 步：

1. 我让 Claude 教我吹牛骰子的概率 / I asked Claude to teach me probability
2. Claude 给了我 N/3 公式 / Claude gave me the N/3 formula
3. 我做了 6 道题，公式变成了条件反射 / I solved 6 problems, the shortcut became automatic
4. Claude 教了我斋（1 不再万能的中国规则）/ Claude taught me zhai
5. 我学了进攻策略——跳叫、钓鱼、斋作武器 / I learned aggressive strategies
6. 我说"来模拟一局？" / I said "can we simulate a game?"
7. 然后我意识到：**这整个学习过程就是产品** / Then I realized: **the entire sequence is the product**

教学不是游戏设计师设计的。是从一次真实的学习对话里提取的。每一步都存在，是因为它在我身上验证过。

The tutorial isn't designed by a game designer. It's extracted from a real learning session. Every step exists because it worked on me.

## 斋 / Zhai — 中国吹牛的灵魂

大部分吹牛骰子的工具只支持西方规则。这个支持中国规则——**斋**。

Most Liar's Dice tools only cover Western rules. This one supports the Chinese variant — **zhai** (literally "fasting"):

**正常 Normal：** 1 是万能的，期望值 = N/3。你数的是本体 + 万能 1。

1s are wild. Expected count = N/3. You count natives + wilds.

**叫斋 Zhai：** 有人宣布 1 不再万能。期望值从 N/3 直接砍到 N/6。你以为你知道的牌面，突然砍半了。

Someone strips wildcards. Expected count drops from N/3 to N/6. Everything you knew about the board just got halved.

**破斋 Break-zhai：** 数量加 2，1 重新变成万能。这是反杀——如果你手上三个 1 刚被斋杀了，破斋让你的军队原地复活。

Add 2 to quantity, 1s come back to life. Counter-attack — your dead wilds resurrect.

**什么时候叫斋：** 手上某个点数本体 3 个以上，1 只有 0-1 个。对手的万能 1 全死了，你的本体纹丝不动。

**什么时候不叫：** 手上 1 很多。叫了等于自杀。

斋让吹牛骰子多了一整层博弈。这是中国吹牛比西方版本更深的原因。

This mechanic adds an entire layer of strategy. It's why Chinese Liar's Dice is a deeper game.

## ELO 评分 / ELO Rating

起始 1000。打赢强的涨得多，输给弱的跌得多。前 50 局 K=32（涨跌快），之后 K=16（趋于稳定）。进度保存在 `~/.liars-dice/progress.json`，跨对话持久化。看着自己从 1000 爬到 1200+。

Start at 1000. Beat harder opponents for bigger gains. K=32 for first 50 games, then 16. Progress persists across sessions.

## 安装 / Install

**需要 Requirements：** [Claude Code](https://docs.anthropic.com/en/docs/claude-code)，Python 3.8+

```bash
git clone https://github.com/PhoenixBian/liars-dice.git ~/.claude/skills/liars-dice
cd ~/.claude/skills/liars-dice && chmod +x setup && ./setup
```

在 Claude Code 里输入 `/liars-dice` 或 `/bluff`。就这样。

Type `/liars-dice` or `/bluff` in Claude Code. That's it.

更新：技能会自动检查新版本。或者手动 `cd ~/.claude/skills/liars-dice && git pull`。

## 技术细节 / Under the hood

纯 Python，零外部依赖。只用 Python 3 标准库。

Pure Python, zero external dependencies.

```
engine/
  probability.py   — 精确二项分布（N/3 是给人用的速算；引擎用真数学来判你的答案对不对）
                      Exact binomial distribution (N/3 is for humans; engine uses real math)
  game.py          — 完整状态机：2-6 人，斋/破斋，可序列化 JSON 存档
                      Full state machine: 2-6 players, zhai/break-zhai, JSON serializable
  ai_opponents.py  — 三种性格，可调难度，有控制地犯错（完美 AI 不好玩）
                      Three personalities, tunable difficulty, controlled imperfection
  trainer.py       — 训练题生成器，5 个难度，自动升级
                      Drill generator, 5 levels, auto-progression
  elo.py           — ELO 评分，对局历史，进步曲线
                      Rating system, match history, progress curves
  tutorial.py      — 5 步教学流程，从那次对话里逐字提取的
                      5-step learning flow, extracted verbatim from the original conversation
```

没有网络请求。没有遥测。没有账号。你的数据留在你的机器上。

No network calls. No telemetry. No accounts. Your data stays on your machine.

## 为什么 Building in Public

这是我的第一个开源项目。

核心命题：**AI 不替代技能，AI 压缩学习曲线。**

我从"不知道怎么算"到"拿着啤酒还能秒算期望值"，只用了一次对话。然后我把这次对话变成了工具，让任何人都能做同样的事。

以后每个项目都会走这个模式：用 AI 学会一样东西 → 把学习过程提取成工具 → 开源。AI 做教学，我做学习，工具做两者。

This is project #1. The thesis: **AI doesn't replace skill — it compresses the learning curve.** Learn something with AI, extract the learning into a tool, open-source it. The AI teaches. I learn. The tool does both.

关注这个旅程 / Follow the journey: [@PhoenixBian](https://github.com/PhoenixBian)

## License

MIT。Fork 它，改它，带到下一次酒局。

MIT. Fork it, improve it, bring it to your next game night.

---

**教我算骰子的 AI，现在教你。**

**The AI that taught me to count dice now teaches you.**
