# Rung 1 exam: perft-correct move generation

## Task for the village
Build a C++ chess engine that generates **only legal moves** correctly, proven by perft.

## Required interface (how the grader calls it)
The compiled binary must accept:
    ./engine perft "<FEN>" <depth>
and print the perft leaf-node count as a single integer on its own line.

perft(depth) = number of leaf nodes of the legal-move tree explored to `depth` plies
from the given position (full-move enumeration, legal moves only).

## Must handle every rule
pawn pushes (single/double) + captures, en passant, promotions (all 4 pieces),
knight/bishop/rook/queen/king moves, castling (K/Q, blocked by occupancy/attacks/rights),
check/pin legality (a move is illegal if it leaves your own king in check).

## Pass bar
Output must match `perft_key.json` EXACTLY for every position and depth.
No partial credit — one wrong count = movegen bug = fail, repair, regrade.

## Notes
Mailbox board is fine (bitboards later). Correctness first; speed is a later rung.
