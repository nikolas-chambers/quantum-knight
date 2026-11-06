# QuantumKnight — Results

Match results against [Stockfish](https://stockfishchess.org/) at various skill levels.
QuantumKnight plays White; both engines search to the same fixed depth.

## Strength ladder

| Opponent          | Result | Outcome                   | Moves |
|-------------------|:------:|---------------------------|:-----:|
| Stockfish skill 0 | ✅ Win  | checkmate                 |  93   |
| Stockfish skill 3 | ✅ Win  | checkmate                 |  59   |
| Stockfish skill 5 | ✅ Win  | checkmate                 |  73   |
| Stockfish skill 6 | ✅ Win  | checkmate                 |  27   |
| Stockfish skill 7 | 🤝 Draw | fivefold repetition       | 213   |
| Stockfish skill 8 | ❌ Loss | checkmate                 | 192   |

**Current ceiling:** beats Stockfish up to skill 6, holds skill 7 to a draw.

## Progress over versions

| Milestone                                   | Best result        |
|---------------------------------------------|--------------------|
| Base engine (alpha-beta)                    | beats skill 0      |
| + piece-square tables                       | beats skill 3      |
| + quiescence search                         | beats skill 5      |
| + transposition table, MVV-LVA, killers     | beats skill 6, draws skill 7 |

The transposition table + move ordering also turned the skill-8 game from a
70-move loss into a 192-move loss — the engine now holds far longer under pressure.

## Reproduce

```sh
g++ -O2 -std=c++17 -o engine chess.cpp
python game.py stockfish --skill 6 --depth 5
```
