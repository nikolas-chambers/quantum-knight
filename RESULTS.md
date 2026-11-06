# QuantumKnight — Results

Match results against [Stockfish 17.1](https://stockfishchess.org/) at various skill levels.
Each row is an **8-game match**, colors alternated, both engines at fixed depth 5.
Score is from QuantumKnight's view (win = 1, draw = 0.5).

## Strength ladder

| Opponent          | Score | W–D–L  | Verdict          |
|-------------------|:-----:|:------:|------------------|
| Stockfish skill 6 | 4.0/8 | 2–4–2  | ~even            |
| Stockfish skill 7 | 5.5/8 | 5–1–2  | ✅ winning record |

Single games at these skill levels are very noisy (Stockfish plays randomized
sub-optimal moves), so results are reported as multi-game match scores rather than
one-off games.

## How it got here

| Milestone                                   | Gain                         |
|---------------------------------------------|------------------------------|
| Base engine (alpha-beta)                    | plays legal, perft-correct   |
| + piece-square tables                       | positional sense             |
| + quiescence search                         | no horizon blunders          |
| + transposition table, MVV-LVA, killers     | deeper, sharper search       |
| + richer evaluation                         | winning record vs skill 7    |

Movegen stays **perft-verified at 25/25** through every change.

## Reproduce

```sh
g++ -O2 -std=c++17 -o engine chess.cpp
python game.py stockfish --skill 7 --depth 5
```
