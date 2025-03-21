import os
import time
import argparse
from typing import Tuple

from chessmen import chessmenClient, chessmenMove, chessmenBoardState, chessmenBoardUtility as CBU, PIECE_COLOR, START_FEN

def display_board(board_state: chessmenBoardState, black_side_view: bool = False, flush: bool = False) -> None:
    if flush:
        os.system('clear')
    board = board_state.board
    row_separator = '  ' + '====' * 8 + '='
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
                tile = background * 3
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
    print(' ' + '   '.join([''] + column_marker))

def prompt_user(prompt: str, board_state: chessmenBoardState, user_color: PIECE_COLOR) -> chessmenMove:
    board = board_state.board
    while True:
        inp = input(f'{prompt}> ').strip().lower().split()
        if len(inp) == 2:
            st_notation, en_notation = inp
            if CBU.verify_notation(st_notation) and CBU.verify_notation(en_notation):
                st_coord = CBU.notation2coord(st_notation)
                en_coord = CBU.notation2coord(en_notation)
                if CBU._is_empty(st_coord, board):
                    print('no piece selected')
                elif CBU._get_color(st_coord, board) != user_color: # matching color
                    print('opposite piece selected')
                else:
                    valid_moves = CBU.get_valid_moves(st_coord, board_state)
                    selected_move = None
                    for move in valid_moves:
                        if move.target_coord == en_coord:
                            selected_move = move
                    if selected_move != None:
                        return selected_move
                    else:
                        print(f'invalid move (possible valid moves: {[move.notation() for move in valid_moves]})')
            else:
                print('invalid notation')
        else:
            print('invalid format (number of arguments)')

class chessmenCLILocal:
    def __init__(self) -> None:
        self.board_state = CBU.fen2board_state(START_FEN)
    
    def run(self) -> None:
        while True:
            display_board(self.board_state, black_side_view=(self.board_state.active_color == 'black'), flush=True)
            move = prompt_user(f"({self.board_state.active_color})", self.board_state, self.board_state.active_color)
            self.board_state.update(move)

class chessmenCLI:
    REFRESH_TIME = 1 # seconds

    def __init__(self, user_id: str) -> None:
        self.client = chessmenClient(user_id=user_id)
        self.user_id = self.client.user_id
        assert self.client.find_match()
    
    def run(self) -> None:
        while True:
            status = self.client.status_match()
            if status == None: # match does not exist / has stopped
                break
            status, payload = status
            # status: in_queue or in_match
            if status == 'in_match':
                fen, users, user_color, user_turn = payload
                board_state = CBU.fen2board_state(fen)
                display_board(board_state, black_side_view=(user_color == 'black'), flush=True)
                if user_turn:
                    move = prompt_user(f"({self.user_id}-{user_color})", board_state, user_color)
                    board_state.update(move)
                    display_board(board_state, black_side_view=(user_color == 'black'), flush=True)
                    fen = CBU.board_state2fen(board_state)
                    self.client.update_match(fen)
            time.sleep(self.REFRESH_TIME)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='chessmen client CLI interface')
    parser.add_argument('--user_id', help='username for client', type=str, default=None)
    parser.add_argument('--local', help='play local match', action='store_true')
    args = parser.parse_args()

    if args.local:
        cli = chessmenCLILocal()
    else:
        cli = chessmenCLI(args.user_id)
    cli.run()
