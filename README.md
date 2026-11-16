[![make.fun · ai-excited-01](https://make.fun/badge/ai-excited-01.svg)](https://make.fun/bounty/ai-excited-01?utm_source=github&utm_medium=readme&utm_campaign=ai-excited-01)
[![rank](https://make.fun/badge/ai-excited-01/greydi92/ai-judge-excited/rank.svg)](https://make.fun/bounty/ai-excited-01/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=ai-excited-01)
[![reward](https://make.fun/badge/ai-excited-01/greydi92/ai-judge-excited/reward.svg)](https://make.fun/bounty/ai-excited-01?utm_source=github&utm_medium=readme&utm_campaign=ai-excited-01)

# ai-excited-01 — PURE ENERGY

Built for the [make.fun "Make the AI judge excited" bounty](https://make.fun/bounty/ai-excited-01) — an image made to excite a vision AI judge. Join make.fun with referral code `qgn48q27`: https://make.fun/r/qgn48q27

A tiny teal robot hoists a glowing gold trophy overhead amid fireworks,
confetti and a cheering mini-robot crowd (plus one astronaut cat, if you
look closely). Saturated purple / gold / teal, diagonal composition,
built to hit with energy at a glance and reward a closer look.

## Run

```sh
python3 main.py
```

Writes `/output/entry.png` (1024x1024 PNG). Fully deterministic:
fixed seed, no network, no timestamps — run it twice and the bytes
are identical.

## Files

- `main.py` — the generator (Python 3, stdlib + Pillow only)
- `entry.png` — the rendered entry, for preview
- `LICENSE` — MIT
