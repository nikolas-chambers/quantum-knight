# QuantumKnight

A from-scratch chess engine in a single C++17 file. UCI-compatible, perft-verified,
and rated **≈ 2000 Elo** (estimated).

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
**≈ 2000 Elo** — scored 50.8% (112–108–30) over a 250-game match vs Stockfish 17.1
in calibrated limited-strength mode (`UCI_Elo=2000`), TC 10+0.1, with an opening book.

| Opponent             | Score  | Note              |
|----------------------|:------:|-------------------|
| Stockfish `UCI_Elo=2000` | 50.8% | 250 games → ≈2000 Elo |
| Stockfish skill 7    | 5.5/8  | winning record    |
| Stockfish skill 6    | 4.0/8  | ~even             |

See `RESULTS.md` for full method and numbers.

## Testing
- `perft_key.json` — Stockfish-verified perft counts
- `game.py <opponent> [--skill N] [--time MS|--depth N]` — play vs any UCI engine (needs `python-chess`)

## Credits & tooling
QuantumKnight is an independent engine. These tools are used only for testing and rating:
- [Stockfish](https://stockfishchess.org/) — opponent and perft oracle
- [fastchess](https://github.com/Disservin/fastchess) — tournament runner
- [UHO opening book](https://github.com/official-stockfish/books) — match openings
