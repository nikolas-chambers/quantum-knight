import re, subprocess, sys, os
sys.path.insert(0, "/home/user/nikc/leverage-ai")
os.chdir("/home/user/chess")
from leverage_ai.state import load_state
from leverage_ai.delegation import delegate

KEY = {
 "8/8/8/8/3R4/8/8/k6K w - - 0 1": {1: 17, 2: 45, 3: 787},
 "8/8/8/8/3B4/8/8/k6K w - - 0 1": {1: 16, 2: 37, 3: 484},
 "8/8/8/3Q4/8/8/8/k6K w - - 0 1": {1: 29, 2: 59, 3: 1567},
 "8/8/3n4/3R4/8/8/8/k6K w - - 0 1": {1: 15, 2: 135, 3: 2268},
}

BASE_TASK = '''Write a COMPLETE single-file C++17 program (standard library only).
Interface:  ./engine perft "<FEN>" <depth>   -> prints the perft leaf-node count (final line).
SCOPE: positions contain ONLY kings, knights, and SLIDERS (bishop, rook, queen). No pawns,
no castling, no en passant, no promotion. Implement FEN parse (board + side), legal move gen for:
- KNIGHT (8 L-jumps), KING (1 step; not into check; kings never adjacent),
- BISHOP (diagonals), ROOK (ranks/files), QUEEN (both) -- sliders travel until blocked:
  stop before a friendly piece, capture-and-stop on an enemy piece,
- king legality: a move is illegal if it leaves your own king attacked,
make/unmake, and perft(depth) counting LEGAL-move leaf nodes.
Compile: g++ -O2 -std=c++17 -o engine engine.cpp. Reply with EXACTLY one ```cpp block, no prose.'''

def build_and_grade():
    c = subprocess.run(["g++","-O2","-std=c++17","-o","engine","engine.cpp"],
                       capture_output=True, text=True, timeout=200)
    if c.returncode != 0:
        return False, "COMPILE_FAILED (fix these, incl. any missing #include):\n" + c.stderr[-1200:]
    fails = []
    for fen, dd in KEY.items():
        for d, exp in sorted(dd.items()):
            r = subprocess.run(["./engine","perft",fen,str(d)], capture_output=True, text=True, timeout=60)
            nums = [int(x) for x in r.stdout.split() if x.lstrip("-").isdigit()]
            got = nums[-1] if nums else None
            if got != exp:
                fails.append(f"{fen}  perft {d}: got {got}, expected {exp}")
    if fails:
        return False, "PERFT_WRONG (move-gen logic bug):\n" + "\n".join(fails)
    return True, "all rung-1b perft correct"

state = load_state()
N, prev, passed, att = 7, None, False, 0
for att in range(1, N+1):
    print(f"\n===== attempt {att} =====", flush=True)
    prompt = BASE_TASK if prev is None else (
        BASE_TASK + "\n\nYOUR PREVIOUS ATTEMPT FAILED WITH:\n" + prev +
        "\n\nReturn the FULL corrected program (one ```cpp block).")
    ans = delegate(prompt, state, mode="single", task_type="chess_movegen")
    blocks = re.findall(r"```(?:cpp)?\s*\n(.*?)```", ans or "", re.S)
    if not blocks:
        prev = "No code block. Reply with ONE ```cpp block containing the full program."
        print("  no code block"); continue
    open("engine.cpp","w").write(blocks[-1])
    ok, report = build_and_grade()
    print(("  PASS: " if ok else "  FAIL: ") + report[:700], flush=True)
    if ok:
        passed = True; break
    prev = report

grade = "A" if (passed and att==1) else "B" if (passed and att<=3) else "C" if (passed and att<=6) else "F"
print(f"\n==== RUNG 1b {'PASSED' if passed else 'NOT PASSED'} in {att} attempt(s) -> grade {grade} ====")
open("GROWTH.md","a").write(f"rung 1b  sliders (B/R/Q)         {grade}   ({att} attempts)\n")
