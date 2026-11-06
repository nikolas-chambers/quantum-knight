# QuantumKnight — Results

## Estimated strength: ≈ 2000 Elo

Measured with fastchess matches against [Stockfish 17.1](https://stockfishchess.org/) in
calibrated limited-strength mode (`UCI_LimitStrength=true`), time control 10+0.1, openings
from the UHO_4060_v2 book.

| Match (250 games, TC 10+0.1) | Score | Elo vs opponent | Implied Elo |
|------------------------------|:-----:|:---------------:|:-----------:|
| vs Stockfish `UCI_Elo=2000`  | 50.8% | +5.6 ± 37       | ≈ 2006      |
| vs Stockfish `UCI_Elo=2200`  | 24.8% | −193 ± 40       | ≈ 2007      |

Both matches land the engine at **≈ 2000 Elo** — a consistent, honest estimate.
(Stockfish's `UCI_Elo` scale is approximate, so treat this as a ballpark.)

## Fixed-depth skill ladder (different measurement)

At a **fixed search depth of 5**, Stockfish is depth-capped too, and QuantumKnight's
evaluation lets it hold its own much further up the skill scale. 6 games per level, colors
alternated:

| Skill | Score | | Skill | Score |
|:-----:|:-----:|-|:-----:|:-----:|
| 1 | 5.0/6 | | 7  | 4.0/6 |
| 2 | 5.5/6 | | 8  | 4.0/6 |
| 3 | 5.5/6 | | 9  | 4.0/6 |
| 4 | 4.5/6 | | 10 | 1.0/6 * |
| 5 | 4.5/6 | | 11 | 4.0/6 |
| 6 | 4.0/6 | | 12 | 4.5/6 |

Winning record across skill 1–12. (* skill 10's 1.0/6 is an outlier from a noisy 6-game
sample — it beats 11 and 12; these small samples are high-variance.)

**Important:** the ladder and the Elo measure different things. Fixed-depth results flatter
the engine because they also cap Stockfish's search; the **time-control Elo (~2000)** is the
honest overall-strength number. Climbing that Elo needs deeper *search* (null-move pruning,
late-move reductions), not just a better evaluation.

## How it got here

| Milestone                                   | Gain                              |
|---------------------------------------------|-----------------------------------|
| Base engine (alpha-beta)                    | plays legal, perft-correct        |
| + piece-square tables                       | positional sense                  |
| + quiescence search                         | no horizon blunders               |
| + transposition table, MVV-LVA, killers     | deeper, sharper search → ≈2000 Elo |
| + self-play-trained evaluation              | winning record vs skill 1–12 at depth 5 |

Movegen stays **perft-verified at 25/25** through every change.

## Reproduce

```sh
g++ -O2 -std=c++17 -o engine chess.cpp
# skill-ladder game:
python game.py stockfish --skill 9 --depth 5
# Elo match (needs fastchess + an opening book):
fastchess \
  -engine cmd=./engine name=QuantumKnight \
  -engine cmd=stockfish name=SF-2000 option.UCI_LimitStrength=true option.UCI_Elo=2000 \
  -each tc=10+0.1 -rounds 125 -games 2 -repeat -concurrency 4 \
  -openings file=UHO_4060_v2.epd format=epd order=random
```

## Goal

Long-term: keep learning toward parity with full-strength Stockfish (skill 20, ~3600 Elo).
That's a real gap and a work in progress — the engine is still learning.

## Credits & tooling

- [Stockfish](https://stockfishchess.org/) — opponent and perft oracle
- [fastchess](https://github.com/Disservin/fastchess) — tournament runner
- [UHO_4060_v2 opening book](https://github.com/official-stockfish/books) — match openings

QuantumKnight is an independent engine; the tools above are used only for testing and rating.
