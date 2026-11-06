#!/usr/bin/env python3
# Teacher's grader. Usage: python3 grade.py ./engine [--maxdepth N]
import json, subprocess, sys, time
key = json.load(open("perft_key.json"))
engine = sys.argv[1] if len(sys.argv) > 1 else "./engine"
maxd = 99
if "--maxdepth" in sys.argv: maxd = int(sys.argv[sys.argv.index("--maxdepth")+1])
total=passed=0; first_fail=None
for p in key["positions"]:
    for d,exp in sorted(((int(k),v) for k,v in p["nodes"].items())):
        if d>maxd: continue
        total+=1
        try:
            t=time.time()
            out=subprocess.run([engine,"perft",p["fen"],str(d)],capture_output=True,text=True,timeout=120)
            nums=[int(x) for x in out.stdout.split() if x.lstrip("-").isdigit()]
            got=nums[-1] if nums else None
            dt=time.time()-t
        except Exception as e:
            got=None; dt=0; out=type("o",(),{"stderr":str(e)})
        ok = got==exp
        passed+=ok
        mark="✓" if ok else "✗"
        print(f"  {mark} {p['name']:10} d{d}: got {got} expected {exp}  ({dt:.1f}s)")
        if not ok and first_fail is None:
            first_fail=(p['name'],d,got,exp,getattr(out,'stderr','')[:200])
print(f"\nGRADE: {passed}/{total}")
if first_fail:
    n,d,g,e,err=first_fail
    print(f"FIRST DIVERGENCE: {n} depth {d} -> got {g}, expected {e}")
    if err: print(f"  stderr: {err}")
    sys.exit(1)
print("PASS — movegen is perft-correct. Accept, move to rung 2 (UCI).")
