import time
import argparse
from chessmen import chessmenClient, chessmenBoard

class chessmenCLI:
    REFRESH_TIME = 1 # seconds

    def __init__(self, name: str):
        self.client = chessmenClient(user_id=name)
        self.username = self.client.user_id
        assert self.client.find_game()
    
    def run(self):
        while True:
            status = self.client.status()
            if status == None:
                break
            status, payload = status
            if status == "in_game": # otherwise still waiting for game
                fen, user_side, turn = payload
                board = chessmenBoard.fen2board(fen)
                chessmenBoard.display(board, (user_side == "black"), flush=True)
                if user_side == turn:
                    inp = chessmenBoard.prompt_user(f"({self.username}-{turn})", board, turn)
                    if inp != None:
                        st_coord, en_coord = inp
                        new_board = chessmenBoard.update_board(board, st_coord, en_coord, (turn == "black"))
                        if new_board != None:
                            chessmenBoard.display(new_board, (turn == "black"), flush=True)
                            fen = chessmenBoard.board2fen(new_board)
                            self.client.update(fen)
            time.sleep(self.REFRESH_TIME)

parser = argparse.ArgumentParser(description="chessmen client CLI interface")
parser.add_argument("username", help="username for client", type=str)
args = parser.parse_args()

cli = chessmenCLI(args.username)
cli.run()
