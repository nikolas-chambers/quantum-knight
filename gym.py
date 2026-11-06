#!/usr/bin/env python3
"""Self-teaching gym -- the VILLAGE improves the engine's evaluation.

Big bro only runs the gym. The village:
 - reads the current evaluate() + its LEARNED.md journal
 - proposes a BETTER evaluate() (mobility / king safety / passed pawns / rook on
   open file -- anything computable from board[]). Returns ONLY that one function.
 - gym splices it in, gates it (must compile, perft stays 25/25, must not lose to
   skill 6), ranks it over 3 games vs skill 7, keeps it only if it climbs,
   and writes the lesson to LEARNED.md so it never repeats a dead end.

Run:  /data/data/com.termux/files/usr/bin/python gym.py <rounds>
"""
import re, json, shutil, subprocess, sys, os, time
sys.path.insert(0, "/home/user/nikc/leverage-ai")
os.chdir("/home/user/chess")
from leverage_ai.state import load_state
from leverage_ai.delegation import delegate

PY = "/data/data/com.termux/files/usr/bin/python"
ROUNDS = int(sys.argv[1]) if len(sys.argv) > 1 else 3

def sh(cmd, t=2400):
    return subprocess.run(cmd, capture_output=True, text=True, timeout=t)

def splice_eval(full_src, new_eval):
    """Replace the existing int evaluate(){...} with new_eval via brace matching."""
    i = full_src.index("int evaluate()")
    j = full_src.index("{", i)
    depth = 0
    k = j
    while k < len(full_src):
        if full_src[k] == "{": depth += 1
        elif full_src[k] == "}":
            depth -= 1
            if depth == 0: break
        k += 1
    return full_src[:i] + new_eval.strip() + full_src[k+1:]

def build(src):
    open("cand.cpp", "w").write(src)
    c = sh(["g++", "-O2", "-std=c++17", "-o", "cand", "cand.cpp"], t=300)
    return (c.returncode == 0), c.stderr[-1200:]

def perft_ok(binary):
    key = json.load(open("perft_key.json"))
    for pos in key["positions"]:
        for d, exp in pos["nodes"].items():
            r = sh([binary, "perft", pos["fen"], str(d)], t=200)
            nums = [int(x) for x in r.stdout.split() if x.lstrip("-").isdigit()]
            if not nums or nums[-1] != exp:
                return False, f"perft FAIL {pos['name']} d{d}"
    return True, "perft 25/25"

def play(binary, skill, depth=5):
    r = sh([PY, "game.py", str(skill), str(depth)], t=2400)
    out = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else ""
    m = re.search(r":\s*([012/-]+)\s+in\s+(\d+)\s+moves\s+\((\w+)\)", out)
    if not m: return -1, 0, "NO_RESULT"
    result = m.group(1)
    score = 2 if result == "1-0" else (1 if result == "1/2-1/2" else 0)
    return score, int(m.group(2)), m.group(3)

def fitness():
    # gate: one skill-6 game must NOT be a loss (skill levels are noisy; a loss = real regression)
    s6, m6, t6 = play("./cand", 6)
    if s6 < 1:
        return None, f"LOST to skill6 ({t6}) -> regression"
    # rank: 3 games vs skill 7
    games = [play("./cand", 7) for _ in range(3)]
    total = sum(g[0] for g in games)
    moves = sum(g[1] for g in games)
    detail = ",".join(f"{['L','D','W'][g[0]]}{g[1]}" if g[0] in (0,1,2) else "?" for g in games)
    return (total, moves), f"skill6 ok; skill7 total={total}/6 [{detail}]"

GOAL = """Improve the EVALUATION of a C++17 chess engine (0x88 board). It already beats
Stockfish skill 6 and draws skill 7. Draws happen because the eval is too shallow to
convert an edge. Write a BETTER evaluate().

You may use these already-defined globals/helpers (do not redefine them):
  int board[128];           // 0x88; piece chars PNBRQK / pnbrqk, 0=empty
  int sideToMove;           // 0 white, 1 black
  int kingSq[2];
  bool onBoard(int s); int fileOf(int s); int rankOf(int s);
  int colorOf(int p);       // 0 white, 1 black, -1 empty
  int typeOf(int p);        // 'p','n','b','r','q','k'
  int val[256];             // material, white +, black - (val['P']=100 ... val['Q']=900)
  bool squareAttacked(int s,int by);
  void genMoves(vector<Move>&mv);   // pseudo-legal moves for current sideToMove
  const int PST_P/PST_N/PST_B/PST_K[64];
evaluate() must return the score from the side-to-move's point of view
(white-positive internally, then negate if sideToMove==1 -- keep that convention).

Add ONE or two well-chosen positional terms, e.g. mobility (reward more moves),
rook on open/half-open file, passed pawns, king-pawn-shield / king safety,
bishop pair, doubled/isolated pawn penalty. Keep material + PST that already exist.

OUTPUT: exactly ONE ```cpp block containing ONLY the complete function
`int evaluate(){ ... }`. No other text, no other functions, no #include.
"""

def extract(ans):
    b = re.findall(r"```(?:cpp)?\s*\n(.*?)```", ans or "", re.S)
    for blk in reversed(b):
        if "int evaluate()" in blk:
            return blk
    return None

def journal(line):
    open("LEARNED.md", "a").write(line + "\n"); print(line, flush=True)

base = open("chess.cpp").read()
cur_eval = base[base.index("int evaluate()"):].split("\nstring sqName")[0]
if not os.path.exists("LEARNED.md"):
    open("LEARNED.md", "w").write("# What the engine taught itself (gym journal)\n\n")

# establish baseline fitness with the CURRENT eval
shutil.copy("chess.cpp", "cand.cpp"); subprocess.run(["g++","-O2","-std=c++17","-o","cand","cand.cpp"])
base_fit, base_note = fitness()
journal(f"\n## gym session {time.strftime('%Y-%m-%d %H:%M')}")
journal(f"- BASELINE eval: {base_note} -> {base_fit}")
best_eval = cur_eval

state = load_state()
for rnd in range(1, ROUNDS + 1):
    journal(f"\n### round {rnd}")
    learned = open("LEARNED.md").read()[-3500:]
    prompt = (GOAL
              + "\n\n=== YOUR JOURNAL (don't repeat dead ends) ===\n" + learned
              + "\n\n=== CURRENT evaluate() (improve on this) ===\n```cpp\n" + best_eval + "\n```\n")
    ans = delegate(prompt, state, mode="single", task_type="chess_eval")
    ev = extract(ans)
    if not ev:
        journal("- skip: no evaluate() block returned"); continue
    try:
        cand_src = splice_eval(base, ev)
    except Exception as e:
        journal(f"- REVERT: splice failed ({e})"); continue
    ok, err = build(cand_src)
    if not ok:
        journal("- REVERT: compile error. lesson: " + err.replace(chr(10)," ")[:160]); continue
    pok, pnote = perft_ok("./cand")
    if not pok:
        journal(f"- REVERT: {pnote}"); continue
    fit, note = fitness()
    if fit is None:
        journal(f"- REVERT: {note}"); continue
    if base_fit is None or fit > base_fit:
        journal(f"- KEEP: climbed! {note}  ({base_fit} -> {fit})")
        best_eval = ev.strip(); base = cand_src; base_fit = fit
        open("chess.cpp","w").write(cand_src)
        subprocess.run(["g++","-O2","-std=c++17","-o","engine","chess.cpp"])
    else:
        journal(f"- REVERT: no climb ({note}; {fit} <= {base_fit})")

journal(f"\n- SESSION END: best {base_fit}. chess.cpp holds the best eval.")
print("\n==== gym done ====")
