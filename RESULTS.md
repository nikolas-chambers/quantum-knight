# QuantumKnight — Results

## Estimated strength: ≈ 2000 Elo

Measured with a **250-game match** against [Stockfish 17.1](https://stockfishchess.org/)
running in calibrated limited-strength mode (`UCI_LimitStrength=true`, `UCI_Elo=2000`),
time control 10+0.1, openings from the UHO_4060_v2 book, run with
[fastchess](https://github.com/Disservin/fastchess).

| Metric            | Value                         |
|-------------------|-------------------------------|
| Score             | **50.8%** (112 W / 108 L / 30 D) |
| Elo vs opponent   | **+5.6 ± 37**                 |
| Estimated Elo     | **≈ 2000 (±37)**              |

Essentially even with a calibrated 2000-rated opponent. (Stockfish's `UCI_Elo` scale
is approximate, so treat this as a ballpark — strong club level.)

## Skill-level ladder

8-game matches at fixed depth 5, colors alternated, vs Stockfish 17.1 skill levels:

| Opponent          | Score | W–D–L |
|-------------------|:-----:|:-----:|
| Stockfish skill 6 | 4.0/8 | 2–4–2 |
| Stockfish skill 7 | 5.5/8 | 5–1–2 |

Single games at these skill levels are noisy (Stockfish plays randomized sub-optimal
moves), so strength is reported as multi-game match scores.

## How it got here

| Milestone                                   | Gain                         |
|---------------------------------------------|------------------------------|
| Base engine (alpha-beta)                    | plays legal, perft-correct   |
| + piece-square tables                       | positional sense             |
| + quiescence search                         | no horizon blunders          |
| + transposition table, MVV-LVA, killers     | deeper, sharper search       |
| + richer evaluation                         | ≈ 2000 Elo                   |

Movegen stays **perft-verified at 25/25** through every change.

## Reproduce

```sh
g++ -O2 -std=c++17 -o engine chess.cpp
# quick skill-ladder game:
python game.py stockfish --skill 7 --depth 5
# full Elo match (needs fastchess + an opening book):
fastchess \
  -engine cmd=./engine name=QuantumKnight \
  -engine cmd=stockfish name=SF-2000 option.UCI_LimitStrength=true option.UCI_Elo=2000 \
  -each tc=10+0.1 -rounds 125 -games 2 -repeat -concurrency 4 \
  -openings file=UHO_4060_v2.epd format=epd order=random
```

## Credits & tooling

- [Stockfish](https://stockfishchess.org/) — opponent and perft oracle for verifying move generation
- [fastchess](https://github.com/Disservin/fastchess) — tournament runner for the Elo match
- [UHO_4060_v2 opening book](https://github.com/official-stockfish/books) — opening positions for match variety

QuantumKnight is an independent engine; the tools above are used only for testing and rating.
