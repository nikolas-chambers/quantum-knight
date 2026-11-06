# Learning habits (document + promote)
## GOOD (promote)
- Converges on fed-back errors (rung 1a: 0s -> overcount -> correct, 3 tries).
- Fixes the exact error named.
## BAD (correct)
- REGRESSES: re-breaks working code (rung 1b att3-5 reintroduced compile errors after att2 compiled).
- Rewrites from scratch each try -> oscillates compile<->logic, never converges.
## Promoted into retry prompts
- "Keep what already compiled/passed; change ONLY what the error names; don't rewrite from scratch; keep your #includes."
