import re, subprocess, sys, os
sys.path.insert(0, "/home/user/nikc/leverage-ai")
os.chdir("/home/user/chess")
from leverage_ai.state import load_state
from leverage_ai.delegation import delegate

TASK = '''Write a COMPLETE single-file C++17 program (standard library only).
Interface:  ./engine fen "<FEN>"
Parse the FEN. Print the 8x8 board rank 8 (top) down to rank 1 (bottom): each square one
char (uppercase=white piece, lowercase=black, '.' for empty), 8 chars per line, no spaces.
Then a final line exactly: "side: w"  or  "side: b".
Must compile: g++ -O2 -std=c++17 -o engine engine.cpp
Reply with EXACTLY one ```cpp code block. No prose.'''

print(">>> KID (single mode) attempting micro-rung 0: FEN -> board\n", flush=True)
ans = delegate(TASK, load_state(), mode="single", task_type="chess_fen")
blocks = re.findall(r"```(?:cpp)?\s*\n(.*?)```", ans or "", re.S)
if not blocks:
    print("KID produced no code block. First 600 chars:\n", (ans or "")[:600]); sys.exit()
open("fen.cpp","w").write(blocks[-1])
print("KID wrote fen.cpp (%d lines). Compiling...\n" % blocks[-1].count(chr(10)))
c = subprocess.run(["g++","-O2","-std=c++17","-o","fen_engine","fen.cpp"],capture_output=True,text=True,timeout=180)
if c.returncode!=0:
    print("COMPILE FAILED:\n"+c.stderr[-1800:]); sys.exit()
print("COMPILED OK. Running on startpos:\n")
r = subprocess.run(["./fen_engine","fen","rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"],
                   capture_output=True,text=True,timeout=10)
print(r.stdout)
if r.stderr: print("--stderr--\n"+r.stderr[:400])
