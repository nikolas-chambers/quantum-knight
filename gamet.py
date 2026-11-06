import chess, chess.engine, sys
skill = int(sys.argv[1]) if len(sys.argv)>1 else 0
ms    = int(sys.argv[2]) if len(sys.argv)>2 else 500   # equal thinking time per move
mine = chess.engine.SimpleEngine.popen_uci("./engine")
sf = chess.engine.SimpleEngine.popen_uci("/usr/games/stockfish")
try: sf.configure({"Skill Level": skill})
except Exception as e: print("cfg:", e)
board = chess.Board()
lim = chess.engine.Limit(time=ms/1000.0)
who = {chess.WHITE: mine, chess.BLACK: sf}
n=0
try:
    while not board.is_game_over() and n<300:
        res = who[board.turn].play(board, lim)
        if res.move is None: break
        board.push(res.move); n+=1
    oc=board.outcome()
    print(f"QuantumKnight(W) vs Stockfish skill {skill} @{ms}ms: {board.result()} in {n} moves ({oc.termination.name if oc else 'cap'})")
finally:
    mine.quit(); sf.quit()
