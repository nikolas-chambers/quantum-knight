import chess, chess.engine, sys
skill = int(sys.argv[1]) if len(sys.argv)>1 else 0
mydepth = int(sys.argv[2]) if len(sys.argv)>2 else 4
mine = chess.engine.SimpleEngine.popen_uci("./engine")
sf = chess.engine.SimpleEngine.popen_uci("/usr/games/stockfish")
try: sf.configure({"Skill Level": skill})
except Exception as e: print("cfg:", e)
board = chess.Board()
who = {chess.WHITE:(mine, chess.engine.Limit(depth=mydepth)),
       chess.BLACK:(sf,  chess.engine.Limit(depth=mydepth))}
n=0
try:
    while not board.is_game_over() and n<300:
        eng,lim = who[board.turn]; res=eng.play(board,lim)
        if res.move is None: break
        board.push(res.move); n+=1
    oc=board.outcome()
    print(f"QuantumKnight(W) vs Stockfish skill {skill} @depth{mydepth}: {board.result()} in {n} moves ({oc.termination.name if oc else 'cap'})")
finally:
    mine.quit(); sf.quit()
