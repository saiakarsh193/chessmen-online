import os
from typing import List, Tuple, Optional, Literal, Union

class chessmenBoard:
    _BOARD = List[List[str]]
    _COORD = Tuple[int, int]
    _COLOR = Literal["white", "black"]
    _START_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"

    @staticmethod
    def flip_turn(turn: _COLOR) -> _COLOR:
        return "white" if turn == "black" else "black"
    
    @staticmethod
    def fen2board(fen: str) -> _BOARD:
        bfen = []
        for row in fen.split('/'):
            cfen = []
            for col in row:
                if col >= '1' and col <= '8':
                    cfen += [' '] * int(col)
                else:
                    cfen.append(col.lower() + ('w' if col.isupper() else 'b'))
            bfen.append(cfen)
        return bfen
    
    @staticmethod
    def board2fen(board: _BOARD) -> str:
        fen = ""
        for row in board:
            ctr = 0
            for i, col in enumerate(row):
                if col == ' ':
                    ctr += 1
                if col != ' ' or i == 7:
                    if ctr > 0:
                        fen += str(ctr)
                    if col != ' ':
                        fen += col[0].upper() if col[1] == 'w' else col[0]
                    ctr = 0
            fen += '/'
        return fen[: -1]
    
    @staticmethod
    def flip_board(board: _BOARD) -> _BOARD:
        return [row[::-1] for row in board[::-1]]
    
    @staticmethod
    def pos2coord(pos: str) -> _COORD:
        return 8 - int(pos[1]), ord(pos[0]) - ord('a')
    
    @staticmethod
    def coord2pos(coord: _COORD) -> str:
        return chr(ord('a') + coord[1]) + str(8 - coord[0])
    
    @staticmethod
    def get_valid_moves(board: _BOARD, coord: _COORD, reverse_board: bool = False) -> List[_COORD]:
        row, col = coord
        piece, color = board[row][col]
        is_bound = lambda row, col: (row >= 0 and row <= 7) and (col >= 0 and col <= 7)
        is_same = lambda row, col: board[row][col] != ' ' and board[row][col][1] == color
        is_opposite = lambda row, col: board[row][col] != ' ' and board[row][col][1] != color
        is_empty = lambda row, col: board[row][col] == ' '
        valid_moves = []
        if piece == 'p':
            if not reverse_board:
                if row == 6 and is_empty(row - 1, col) and is_empty(row - 2, col): # first double move
                    valid_moves.append((row - 2, col))
                if is_bound(row - 1, col) and is_empty(row - 1, col): # straight
                    valid_moves.append((row - 1, col))
                if is_bound(row - 1, col - 1) and is_opposite(row - 1, col - 1): # kill
                    valid_moves.append((row - 1, col - 1))
                if is_bound(row - 1, col + 1) and is_opposite(row - 1, col + 1): # kill
                    valid_moves.append((row - 1, col + 1))
            else:
                if row == 1 and is_empty(row + 1, col) and is_empty(row + 2, col): # first double move
                    valid_moves.append((row + 2, col))
                if is_bound(row + 1, col) and is_empty(row + 1, col): # straight
                    valid_moves.append((row + 1, col))
                if is_bound(row + 1, col - 1) and is_opposite(row + 1, col - 1): # kill
                    valid_moves.append((row + 1, col - 1))
                if is_bound(row + 1, col + 1) and is_opposite(row + 1, col + 1): # kill
                    valid_moves.append((row + 1, col + 1))
        if piece == 'n':
            if is_bound(row - 2, col - 1) and not is_same(row - 2, col - 1):
                valid_moves.append((row - 2, col - 1))
            if is_bound(row - 2, col + 1) and not is_same(row - 2, col + 1):
                valid_moves.append((row - 2, col + 1))
            if is_bound(row - 1, col - 2) and not is_same(row - 1, col - 2):
                valid_moves.append((row - 1, col - 2))
            if is_bound(row - 1, col + 2) and not is_same(row - 1, col + 2):
                valid_moves.append((row - 1, col + 2))
            if is_bound(row + 1, col - 2) and not is_same(row + 1, col - 2):
                valid_moves.append((row + 1, col - 2))
            if is_bound(row + 1, col + 2) and not is_same(row + 1, col + 2):
                valid_moves.append((row + 1, col + 2))
            if is_bound(row + 2, col - 1) and not is_same(row + 2, col - 1):
                valid_moves.append((row + 2, col - 1))
            if is_bound(row + 2, col + 1) and not is_same(row + 2, col + 1):
                valid_moves.append((row + 2, col + 1))
        if piece == 'b' or piece == 'q':
            for i in range(1, min(row, col) + 1): # left top
                if is_bound(row - i, col - i):
                    if not is_same(row - i, col - i): # empty or kill
                        valid_moves.append((row - i, col - i))
                    if not is_empty(row - i, col - i): # path blocked
                        break
            for i in range(1, min(row, 7 - col) + 1): # right top
                if is_bound(row - i, col + i):
                    if not is_same(row - i, col + i): # empty or kill
                        valid_moves.append((row - i, col + i))
                    if not is_empty(row - i, col + i): # path blocked
                        break
            for i in range(1, min(7 - row, col) + 1): # bottom left
                if is_bound(row + i, col - i):
                    if not is_same(row + i, col - i): # empty or kill
                        valid_moves.append((row + i, col - i))
                    if not is_empty(row + i, col - i): # path blocked
                        break
            for i in range(1, min(7 - row, 7 - col) + 1): # bottom right
                if is_bound(row + i, col + i):
                    if not is_same(row + i, col + i): # empty or kill
                        valid_moves.append((row + i, col + i))
                    if not is_empty(row + i, col + i): # path blocked
                        break
        if piece == 'r' or piece == 'q':
            for i in range(1, col + 1): # left
                if is_bound(row, col - i):
                    if not is_same(row, col - i): # empty or kill
                        valid_moves.append((row, col - i))
                    if not is_empty(row, col - i): # path blocked
                        break
            for i in range(1, row + 1): # top
                if is_bound(row - i, col):
                    if not is_same(row - i, col): # empty or kill
                        valid_moves.append((row - i, col))
                    if not is_empty(row - i, col): # path blocked
                        break
            for i in range(1, (7 - col) + 1): # right
                if is_bound(row, col + i):
                    if not is_same(row, col + i): # empty or kill
                        valid_moves.append((row, col + i))
                    if not is_empty(row, col + i): # path blocked
                        break
            for i in range(1, (7 - row) + 1): # bottom
                if is_bound(row + i, col):
                    if not is_same(row + i, col): # empty or kill
                        valid_moves.append((row + i, col))
                    if not is_empty(row + i, col): # path blocked
                        break
        if piece == 'k':
            if is_bound(row - 1, col - 1) and not is_same(row - 1, col - 1):
                valid_moves.append((row - 1, col - 1))
            if is_bound(row - 1, col) and not is_same(row - 1, col):
                valid_moves.append((row - 1, col))
            if is_bound(row - 1, col + 1) and not is_same(row - 1, col + 1):
                valid_moves.append((row - 1, col + 1))
            if is_bound(row, col - 1) and not is_same(row, col - 1):
                valid_moves.append((row, col - 1))
            if is_bound(row, col + 1) and not is_same(row, col + 1):
                valid_moves.append((row, col + 1))
            if is_bound(row + 1, col - 1) and not is_same(row + 1, col - 1):
                valid_moves.append((row + 1, col - 1))
            if is_bound(row + 1, col) and not is_same(row + 1, col):
                valid_moves.append((row + 1, col))
            if is_bound(row + 1, col + 1) and not is_same(row + 1, col + 1):
                valid_moves.append((row + 1, col + 1))
        return valid_moves

    @staticmethod
    def display(data: Union[str, _BOARD], reverse_board: bool = False, flush: bool = False) -> None:
        if type(data) == str:
            board = chessmenBoard.fen2board(data)
        else:
            board = data
        if flush:
            os.system('clear')
        if reverse_board:
            board = chessmenBoard.flip_board(board)
        row_sep = '  ' + '=====' * 8 + '='
        for row in range(8):
            print(row_sep)
            for col in range(8):
                if col == 0:
                    print(str(8 - row) if not reverse_board else str(row + 1), end=' ')
                back = '-' if (row + col) % 2 else ' '
                piece = board[row][col] if board[row][col] != ' ' else back * 2
                print(f'|{back}{piece}{back}', end='')
                if col == 7:
                    print('|')
            if row == 7:
                print(row_sep)
        l_not = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
        print('    '.join([''] + (l_not if not reverse_board else l_not[::-1])))

    @staticmethod
    def prompt_user(prompt: str, board: _BOARD, turn: str) -> Optional[Tuple[_COORD, _COORD]]:
        inp = input(f"{prompt}> ").strip().lower().split()
        if len(inp) == 2:
            st, en = inp
            check_pos = lambda pos: len(pos) == 2 and pos[0] >= 'a' and pos[0] <= 'h' and pos[1] >= '1' and pos[1] <= '8'
            if check_pos(st) and check_pos(en):
                st_coord, en_coord = chessmenBoard.pos2coord(st), chessmenBoard.pos2coord(en)
                if board[st_coord[0]][st_coord[1]] == ' ' or board[st_coord[0]][st_coord[1]][1] != turn:
                    return st_coord, en_coord
                else:
                    print("invalid position (empty or opp)")
            else:
                print("invalid position")
        else:
            print("invalid format")
        return None
    
    @staticmethod
    def update_board(board: _BOARD, st_coord: _COORD, en_coord: _COORD, reverse_board: bool = False) -> Optional[_BOARD]:
        valid_moves = chessmenBoard.get_valid_moves(board, st_coord, reverse_board=reverse_board)
        if en_coord in valid_moves:
            board[en_coord[0]][en_coord[1]] = board[st_coord[0]][st_coord[1]]
            board[st_coord[0]][st_coord[1]] = ' '
            return board
        else:
            print("invalid move, valid:", ' '.join([chessmenBoard.coord2pos(move) for move in valid_moves]))
            return None
    
    @staticmethod
    def run_offline_multiplayer(fen: str = _START_FEN, turn: _COLOR = "white"):
        board = chessmenBoard.fen2board(fen)
        while True:
            chessmenBoard.display(board, (turn == "black"), flush=True)
            inp = chessmenBoard.prompt_user(f"({turn})", board, turn)
            if inp != None:
                st_coord, en_coord = inp
                new_board = chessmenBoard.update_board(board, st_coord, en_coord, (turn == "black"))
                if new_board != None:
                    turn = chessmenBoard.flip_turn(turn)
