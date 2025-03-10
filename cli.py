import os
import time
import argparse
from typing import Tuple

from chessmen import chessmenClient, chessmenBoardUtility as CBU, COORD, BOARD, PIECE_COLOR

class chessmenCLI:
    REFRESH_TIME = 1 # seconds

    def __init__(self, user_id: str) -> None:
        self.client = chessmenClient(user_id=user_id)
        self.user_id = self.client.user_id
        assert self.client.find_match()

    def display(self, board: BOARD, black_side_view: bool = False, flush: bool = False) -> None:
        if flush:
            os.system('clear')
        row_separator = '  ' + '=====' * 8 + '='
        col_separator = '|'
        background_filler = '-'
        for row in range(8):
            print(row_separator)
            for col in range(8):
                # row marking
                if col == 0:
                    if black_side_view:
                        print(row + 1, end=' ')
                    else:
                        print(8 - row, end=' ')
                # black or white tile background
                background = background_filler if (row + col) % 2 else ' '
                if black_side_view:
                    piece = board[7 - row][7 - col]
                else:
                    piece = board[row][col]
                if piece == ' ':
                    # no piece on tile
                    tile = background * 4
                else:
                    # put the piece in the middle of the tile
                    tile = background + piece + background
                print(f'{col_separator}{tile}', end='')
                if col == 7:
                    print(col_separator)
            if row == 7:
                print(row_separator)
        column_marker = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
        if black_side_view:
            column_marker.reverse()
        print('    '.join([''] + column_marker))
    
    def prompt_user(self, prompt: str, board: BOARD, user_color: PIECE_COLOR) -> Tuple[COORD, COORD]:
        while True:
            inp = input(f'{prompt}> ').strip().lower().split()
            if len(inp) == 2:
                st_notation, en_notation = inp
                if CBU.verify_notation(st_notation) and CBU.verify_notation(en_notation):
                    st_coord = CBU.notation2coord(st_notation)
                    en_coord = CBU.notation2coord(en_notation)
                    piece = board[st_coord[0]][st_coord[1]]
                    if piece == ' ':
                        print('no piece selected')
                    elif piece[1] != user_color[0]: # matching color
                        print('opposite piece selected')
                    else:
                        valid_moves = CBU.get_valid_moves(st_coord, board, get_notation=True)
                        if en_notation in valid_moves:
                            return st_coord, en_coord
                        else:
                            print(f'invalid move (possible valid moves: {valid_moves})')
                else:
                    print('invalid notation')
            else:
                print('invalid format (number of arguments)')
    
    def run(self):
        while True:
            status = self.client.status_match()
            if status == None: # match does not exist / has stopped
                break
            status, payload = status
            # status: in_queue or in_match
            if status == 'in_match':
                fen, user_color, turn = payload
                board = CBU.convert_fen2board(fen)
                self.display(board, black_side_view=(user_color == 'black'), flush=True)
                if user_color == turn:
                    st_coord, en_coord = self.prompt_user(f"({self.user_id}-{user_color})", board, user_color)
                    new_board = CBU.update_board(board, st_coord, en_coord)
                    self.display(new_board, black_side_view=(user_color == 'black'), flush=True)
                    new_fen = CBU.convert_board2fen(new_board)
                    self.client.update_match(new_fen)
            time.sleep(self.REFRESH_TIME)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='chessmen client CLI interface')
    parser.add_argument('user_id', help='username for client', type=str)
    args = parser.parse_args()

    cli = chessmenCLI(args.user_id)
    cli.run()
