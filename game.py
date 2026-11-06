#!/usr/bin/env python3
"""Pit QuantumKnight against another UCI engine and watch it play.

Requires: python-chess  (pip install chess) and a built ./engine
          (g++ -O2 -std=c++17 -o engine chess.cpp)

Examples:
  python game.py                             # vs Stockfish, 1s/move, QuantumKnight = White
  python game.py /usr/games/stockfish        # explicit opponent path
  python game.py stockfish --skill 6         # handicap a Stockfish opponent to skill 6
  python game.py other_engine --time 2000    # 2 seconds per move
  python game.py stockfish --depth 6         # fixed depth instead of time
  python game.py stockfish --color b         # QuantumKnight plays Black
  python game.py stockfish --quiet           # print only the final result
"""
import argparse, shutil, sys
try:
    import chess, chess.engine
except ImportError:
    sys.exit("needs python-chess:  pip install chess")

p = argparse.ArgumentParser(description="QuantumKnight vs another UCI engine")
p.add_argument("opponent", nargs="?", default=shutil.which("stockfish") or "/usr/games/stockfish",
               help="path to opponent UCI engine (default: Stockfish)")
p.add_argument("--engine", default="./engine", help="path to QuantumKnight (default ./engine)")
p.add_argument("--time", type=int, default=1000, help="per-move time in ms")
p.add_argument("--depth", type=int, default=None, help="fixed depth instead of time")
p.add_argument("--skill", type=int, default=None, help="Stockfish Skill Level 0-20 for the opponent")
p.add_argument("--color", choices=["w", "b"], default="w", help="QuantumKnight's color")
p.add_argument("--fen", default=None, help="start FEN")
p.add_argument("--quiet", action="store_true", help="print only the result")
a = p.parse_args()

qk = chess.engine.SimpleEngine.popen_uci(a.engine)
opp = chess.engine.SimpleEngine.popen_uci(a.opponent)
if a.skill is not None:
    try: opp.configure({"Skill Level": a.skill})
    except Exception as e: print("skill config failed:", e)

lim = chess.engine.Limit(depth=a.depth) if a.depth else chess.engine.Limit(time=a.time / 1000.0)
board = chess.Board(a.fen) if a.fen else chess.Board()

qk_white = (a.color == "w")
players = {chess.WHITE: (qk, "QuantumKnight") if qk_white else (opp, "opponent"),
           chess.BLACK: (opp, "opponent") if qk_white else (qk, "QuantumKnight")}

opp_name = a.opponent.split("/")[-1]
qk_color = "White" if qk_white else "Black"
if not a.quiet:
    print(f"QuantumKnight ({qk_color}) vs {opp_name}"
          + (f" skill {a.skill}" if a.skill is not None else "")
          + (f"  @ depth {a.depth}" if a.depth else f"  @ {a.time}ms/move"))
    print(board.fen(), "\n")

n = 0
try:
    while not board.is_game_over(claim_draw=True) and n < 400:
        eng, who = players[board.turn]
        res = eng.play(board, lim)
        if res.move is None:
            break
        san = board.san(res.move)
        board.push(res.move)
        n += 1
        if not a.quiet:
            mover = "QK" if who == "QuantumKnight" else "  "
            print(f"{n:3}. {mover} {san}")
    oc = board.outcome(claim_draw=True)
    res = board.result(claim_draw=True)
    who_won = {"1-0": "White", "0-1": "Black", "1/2-1/2": "Draw"}.get(res, res)
    winner = ("QuantumKnight" if (who_won == "White") == qk_white else opp_name) if who_won != "Draw" else "Draw"
    print(f"\nResult: {res}  ({winner})  in {n} moves"
          + (f"  [{oc.termination.name}]" if oc else "  [move cap]"))
finally:
    qk.quit(); opp.quit()
