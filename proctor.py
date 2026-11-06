import re, subprocess, sys, os
sys.path.insert(0, "/home/user/nikc/leverage-ai")
os.chdir("/home/user/chess")
from leverage_ai.state import load_state
from leverage_ai.delegation import delegate

TASK = open("EXAM.md").read() + """

Deliver a COMPLETE single-file C++17 program (standard library only).
It must compile with:  g++ -O2 -std=c++17 -o engine engine.cpp
and run as:            ./engine perft "<FEN>" <depth>
printing the perft leaf-node count as the final line of output.
Respond with EXACTLY one ```cpp code block containing the entire program. No prose.
"""

def verify(artifact):
    blocks = re.findall(r"```(?:cpp|c\\+\\+)?\s*\n(.*?)```", artifact or "", re.S)
    if not blocks:
        return False, "NO_CODE: reply with ONE ```cpp block holding the full program."
    open("engine.cpp","w").write(blocks[-1])
    c = subprocess.run(["g++","-O2","-std=c++17","-o","engine","engine.cpp"],
                       capture_output=True, text=True, timeout=240)
    if c.returncode != 0:
        return False, "COMPILE_FAILED (fix these):\n"+c.stderr[-1600:]
    g = subprocess.run([sys.executable,"grade.py","./engine","--maxdepth","3"],
                       capture_output=True, text=True, timeout=600)
    if g.returncode == 0:
        return True, "perft depth<=3 PASSES.\n"+g.stdout[-400:]
    return False, "PERFT_MISMATCH (your move generation has a bug):\n"+g.stdout[-1400:]

print(">>> village attempting RUNG 1: perft-correct movegen\n", flush=True)
ans = delegate(load_state(), ) if False else delegate(TASK, load_state(), verifier=verify, task_type="chess_engine")
print("\n==== FULL-KEY GRADE OF BEST ATTEMPT ====", flush=True)
if ans:
    verify(ans)
    g = subprocess.run([sys.executable,"grade.py","./engine"], capture_output=True, text=True, timeout=1800)
    print(g.stdout[-2500:])
else:
    print("village produced nothing compilable this round.")
