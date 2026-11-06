# QuantumKnight

A from-scratch chess engine in a single C++17 file. UCI-compatible, perft-verified,
and strong enough to beat Stockfish up to skill level 6.

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
At equal search depth, versus Stockfish skill levels:

| Opponent          | Result |
|-------------------|--------|
| Stockfish skill 0 | win    |
| Stockfish skill 3 | win    |
| Stockfish skill 5 | win    |
| Stockfish skill 6 | win    |
| Stockfish skill 7 | draw   |
| Stockfish skill 8 | loss   |

See `RESULTS.md` for the full ladder.

## Testing
- `perft_key.json` — Stockfish-verified perft counts
- `game.py <skill> <depth>` — play a game vs Stockfish (needs `python-chess` + Stockfish)
- `gym.py <rounds>` — self-improvement loop that proposes, gates, and ranks evaluation changes
