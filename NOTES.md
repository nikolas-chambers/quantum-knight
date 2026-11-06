# Chess engine project — running notes

## Goal
Build a chess engine from scratch, climb toward Stockfish rung by rung.
North star = beat Stockfish (moonshot/ceiling). The *grade bar* is a reachable ladder.

## The family / roles
- **Kiddo (leverage village)** DOES the work — writes the engine.
- **Teachers:** Nik (positional judgment / taste) + Claude (mechanics). We teach, never hand answers.
- **Examiner:** perft + Stockfish. Incorruptible. Final word — grades the teachers too.
- **Mom (opencode):** NOT wired yet. Future build = she *watches* runs + keeps notes
  (the "watch" verb of the mothering cord). Until then, Claude keeps these notes.

## The grading ladder (each rung: pass -> accept -> climb)
1. perft-exact movegen  (THIS rung)
2. legal games over UCI
3. beats a random-mover
4. beats Stockfish Level 0, then 1, 2, 3 ...

## Exam (rung 1) — built in ~/chess
- perft_key.json  : answer key, 25 checks across 6 positions (startpos, Kiwipete, pos3-6)
- EXAM.md         : task spec (binary must do `./engine perft "<FEN>" <depth>`)
- grade.py        : grader (compares engine's perft to the key)
- proctor.py      : runs the village through the exam (leverage generate->verify->repair)

## Round 1 result (2026-11-06) — FAILED, nothing compilable
WHY (the lesson):
- Coordinator FRAGMENTED a single-artifact task into plan/contract/research/movegen
  subtasks -> merge = NO_CODE (fragments, not one program).
- Repairs hit request failures + **HTTP 413 (payload too large)** — the whole-engine-in-
  one-request blew past provider size limits.
Takeaway: panel/decompose + "whole engine at once" + 3 repair cycles = produces NOTHING.

## The RIGHT setup (maximize potential) — next time
- **single/direct mode** per artifact (one model writes a whole program, no fragments).
- **Scaffold into micro-rungs with targeted unit tests**, each small + passable + localizing:
  board+FEN -> knight moves -> sliders -> pawns -> castling -> en passant -> promotion -> legality.
  Small tasks => small requests (no 413) + localized failure => targeted teaching.
- More than 3 iterations. Panel only for genuinely multi-angle work, never one cohesive file.
- Honest: free models + perft-exact movegen is a grind; the tricky rules (castle/ep/promo/pins)
  may stall the kid -> teacher steps in and shows it (that's the mothering).

## TODO / future
- [ ] Rebuild exam into scaffolded micro-rungs; re-run in single mode.
- [ ] Wire "mom watches + keeps notes" (opencode observing leverage's event log).
- [ ] ML/NNUE = far rung, after the engine plays legal chess. Research then, not now.
- [ ] Eventually: Android chess GUI for the console; UCI keeps engine/GUI decoupled.

## Progress log
- Rung 0 (FEN->board): PASSED first try, single mode (Cloudflare). Accepted 2026-11-06.
