# MOM spec — Wizard-of-Oz role
# Point: learn exactly what to configure opencode-mom to do, by doing it manually first.

## Mom's loop (per micro-rung)
1. WATCH  — take the kid's output (code / answer).
2. GRADE  — compile (if code) + run the rung's FULL test suite. EDGE CASES, not a spot-check.
            Pass only on 100%.
3. DECIDE + ACT:
   - all pass -> ACCEPT the rung, advance, log the win (feeds the competence signal).
   - any fail -> diagnose (which test, how it diverged) -> COACH (hand back with a targeted hint)
                 OR FIX (correct it directly).   [coach-vs-fix rule: TBD — learn it from a fail cycle]
4. LOG    — what was tested, per-test pass/fail, the hint/fix given -> notes + learning loop.

## What mom needs wired (to automate in opencode)
- Per-rung test suite (inputs + expected) = the exam.
- A compile/run harness (g++, run the binary, capture output).
- Ground truth to grade against (perft key, unit expectations).
- A log sink (the scoreboard / these notes).
- A channel back to the kid (leverage) to hand coaching / request a retry.

## Rules learned by playing it
- THOROUGHNESS: always probe edge cases; never accept on the happy path alone.
  (Rung 0: kid passed startpos, but mom still tested black-to-move, mixed pieces, digit-runs.)
- AUTONOMY (maximize-potential): low-stakes reversible code -> high autonomy; the grader is the net.
- SMALL TASKS: single mode, one small artifact. (Round-1 lesson: monolith panel = fragments + HTTP 413.)

## Observed cycles
- Rung 0 (FEN -> board): kid = single mode via Cloudflare, ~free, 54-line fen.cpp, compiled,
  PASSED all 4 FEN tests first try. Mom: graded edges -> ACCEPT -> advance.
  (Happy path — mom's FIX/COACH branch NOT yet exercised; next harder rung should trigger it.)
