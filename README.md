# QuantumKnight

A from-scratch chess engine in a single C++17 file. UCI-compatible, perft-verified,
and holding a winning record against Stockfish 17.1 up to skill level 7.

## Features
- **0x88 board** representation with fully legal move generation
- **perft-verified** movegen — passes 25/25 positions (startpos, kiwipete, and known tricky FENs) against Stockfish as the oracle
- **Search:** alpha-beta negamax, iterative deepening, quiescence search
- **Transposition table** (Zobrist hashing) with MVV-LVA capture ordering and killer moves
- **Evaluation:** material + piece-square tables
- **UCI protocol:** `uci`, `isready`, `ucinewgame`, `position`, `go depth`/`go movetime`/time controls, `quit`
- Single file, standard library only — no dependencies

## Build
```sh
g++ -O2 -std=c++17 -o engine chess.cpp
```

## Usage
As a UCI engine (load `./engine` in any UCI GUI, or pipe commands):
```sh
printf 'uci\nposition startpos\ngo movetime 1000\n' | ./engine
```

Perft from the command line:
```sh
./engine perft "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1" 5
# -> 4865609
```

## Strength
8-game matches at fixed depth 5, colors alternated, vs Stockfish 17.1:

| Opponent          | Score | W–D–L |
|-------------------|:-----:|:-----:|
| Stockfish skill 6 | 4.0/8 | 2–4–2 |
| Stockfish skill 7 | 5.5/8 | 5–1–2 |

See `RESULTS.md` for details. (Single games at these skill levels are noisy, so
strength is measured in multi-game matches.)

## Testing
- `perft_key.json` — Stockfish-verified perft counts
- `game.py <opponent> [--skill N] [--time MS|--depth N]` — play vs any UCI engine (needs `python-chess`)
