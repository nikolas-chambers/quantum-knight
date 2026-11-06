import chess, chess.engine
mine = chess.engine.SimpleEngine.popen_uci("./engine")
sf = chess.engine.SimpleEngine.popen_uci("/usr/games/stockfish")
try: sf.configure({"Skill Level":0})
except Exception as e: print("cfg:",e)
board = chess.Board()
who = {chess.WHITE:("mine",mine,chess.engine.Limit(depth=4)),
       chess.BLACK:("stockfish",sf,chess.engine.Limit(depth=1))}
n=0
try:
    while not board.is_game_over() and n<300:
        name,eng,lim = who[board.turn]
        res = eng.play(board, lim)
        if res.move is None: break
        board.push(res.move); n+=1
    print("RESULT:", board.result(), "| moves:", n)
    oc=board.outcome(); print("reason:", oc.termination.name if oc else "move-cap")
    print(board)
finally:
    mine.quit(); sf.quit()
