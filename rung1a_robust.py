import re, subprocess, sys, os
sys.path.insert(0, "/home/user/nikc/leverage-ai")
os.chdir("/home/user/chess")
from leverage_ai.state import load_state
from leverage_ai.delegation import delegate

KEY = {
 "8/8/8/8/3N4/8/8/k6K w - - 0 1": {1: 11, 2: 33, 3: 366},
 "N6n/8/8/8/8/8/8/k6K w - - 0 1": {1: 5, 2: 25, 3: 210},
 "8/8/8/3nN3/8/8/k6K/8 w - - 0 1": {1: 13, 2: 166, 3: 2011},
}

BASE_TASK = '''Write a COMPLETE single-file C++17 program (standard library only).
Interface:  ./engine perft "<FEN>" <depth>   -> prints the perft leaf-node count (final line).
SCOPE: positions contain ONLY kings and knights. Implement FEN parse (board + side),
legal move gen for KNIGHT (8 L-jumps) and KING (1 step; may NOT move into check; the two
kings may NEVER be adjacent; a move is illegal if it leaves your own king attacked),
make/unmake, and perft(depth) counting LEGAL-move leaf nodes.
Compile: g++ -O2 -std=c++17 -o engine engine.cpp.  Reply with EXACTLY one ```cpp block, no prose.'''

HEADERS = "#include <bits/stdc++.h>\n#include <cstdint>\n"

def build_and_grade():
    c = subprocess.run(["g++","-O2","-std=c++17","-o","engine","engine.cpp"],
                       capture_output=True, text=True, timeout=200)
    if c.returncode != 0:
        return False, "COMPILE_FAILED (fix these):\n" + c.stderr[-1200:]
    fails = []
    for fen, dd in KEY.items():
        for d, exp in sorted(dd.items()):
            r = subprocess.run(["./engine","perft",fen,str(d)], capture_output=True, text=True, timeout=60)
            nums = [int(x) for x in r.stdout.split() if x.lstrip("-").isdigit()]
            got = nums[-1] if nums else None
            if got != exp:
                fails.append(f"{fen}  perft {d}: got {got}, expected {exp}")
    if fails:
        return False, "PERFT_WRONG (your move-gen logic has a bug):\n" + "\n".join(fails)
    return True, "all rung-1a perft correct"

state = load_state()
N, prev, passed, att = 6, None, False, 0
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
    code = blocks[-1]
    open("engine.cpp","w").write(code)   # no header crutch — kid must include correctly; compile error teaches it
    ok, report = build_and_grade()
    print(("  PASS: " if ok else "  FAIL: ") + report[:700], flush=True)
    if ok:
        passed = True; break
    prev = report

print(f"\n==== RUNG 1a {'PASSED' if passed else 'NOT PASSED'} in {att} attempt(s) ====")
open("GROWTH.md","a").write(
    f"rung 1a  knight+king movegen  {'PASS' if passed else 'FAIL'}  {att} attempts (auto-header-fix)  single\n")
