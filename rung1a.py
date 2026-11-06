import re, subprocess, sys, os
sys.path.insert(0, "/home/user/nikc/leverage-ai")
os.chdir("/home/user/chess")
from leverage_ai.state import load_state
from leverage_ai.delegation import delegate

# Stockfish-verified answer key: positions with ONLY kings + knights
KEY = {
 "8/8/8/8/3N4/8/8/k6K w - - 0 1": {1: 11, 2: 33, 3: 366},
 "N6n/8/8/8/8/8/8/k6K w - - 0 1": {1: 5, 2: 25, 3: 210},
 "8/8/8/3nN3/8/8/k6K/8 w - - 0 1": {1: 13, 2: 166, 3: 2011},
}

TASK = '''Write a COMPLETE single-file C++17 program (standard library only).

Interface:  ./engine perft "<FEN>" <depth>
It prints the perft leaf-node count (legal-move tree to <depth> plies) as the final line.

SCOPE for this task: every test position contains ONLY kings and knights (no pawns, bishops,
rooks, queens; no castling, en passant, or promotion will ever appear). Implement:
- FEN parse (board + side to move),
- legal move generation for KNIGHT (the 8 L-jumps) and KING (1 step any direction),
- king legality: a king may NOT move into check and the two kings may NEVER be adjacent;
  a move is illegal if it leaves your own king attacked (here, only by the enemy knight or
  by king-adjacency),
- make/unmake move,
- perft(depth) counting legal-move leaf nodes.

Compile: g++ -O2 -std=c++17 -o engine engine.cpp
Reply with EXACTLY one ```cpp code block. No prose.'''

def grade(engine, maxd=3):
    fails = []
    for fen, dd in KEY.items():
        for d, exp in sorted(dd.items()):
            if d > maxd: continue
            try:
                r = subprocess.run([engine, "perft", fen, str(d)], capture_output=True, text=True, timeout=60)
                nums = [int(x) for x in r.stdout.split() if x.lstrip("-").isdigit()]
                got = nums[-1] if nums else None
            except Exception as e:
                got = f"ERR {e}"
            if got != exp:
                fails.append(f"{fen}  perft {d}: got {got}, expected {exp}")
    return fails

def verify(artifact):
    blocks = re.findall(r"```(?:cpp)?\s*\n(.*?)```", artifact or "", re.S)
    if not blocks:
        return False, "NO_CODE: reply with ONE ```cpp block holding the full program."
    open("engine.cpp", "w").write(blocks[-1])
    c = subprocess.run(["g++", "-O2", "-std=c++17", "-o", "engine", "engine.cpp"],
                       capture_output=True, text=True, timeout=180)
    if c.returncode != 0:
        return False, "COMPILE_FAILED (fix these):\n" + c.stderr[-1500:]
    f = grade("./engine", 3)
    if not f:
        return True, "rung 1a PASSES: knight+king perft correct to depth 3."
    return False, "PERFT_MISMATCH (move-gen bug):\n" + "\n".join(f[:6])

print(">>> KID (single mode) attempting RUNG 1a: knight + king movegen\n", flush=True)
ans = delegate(TASK, load_state(), mode="single", verifier=verify, task_type="chess_movegen")
print("\n==== FINAL GRADE OF BEST ATTEMPT ====", flush=True)
if ans:
    verify(ans)
    f = grade("./engine", 3) if os.path.exists("engine") else ["no engine binary"]
    print("PASS — rung 1a clear" if not f else "FAIL — remaining:\n" + "\n".join(f[:6]))
else:
    print("village produced nothing compilable.")
