from copy import deepcopy
from typing import List, Tuple, Optional, Literal, Union

FEN = str
BOARD = List[List[str]]
COORD = Tuple[int, int]
NOTATION = str

START_FEN: FEN = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR'
PIECE_COLOR = Literal['black', 'white']

class chessmenBoardUtility:
    @staticmethod
    def convert_fen2board(fen: FEN) -> BOARD:
        # upper case is white
        # lower case is black
        # we convert all numbers into empty spaces
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
    def convert_board2fen(board: BOARD) -> FEN:
        # we convert all empty spaces into numbers
        # notation if from top left to bottom right
        fen = ''
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
    
    # standard notation
    # 8 r n b q k b n r    ->    BLACK
    # 7 p p p p p p p p
    # 6
    # 5
    # 4
    # 3
    # 2 P P P P P P P P
    # 1 R N B Q K B N R    ->    WHITE
    #   a b c d e f g h

    # board representation
    # (0, 0)     ->    (0, 7)
    # rb
    #
    #
    #
    #
    # rw
    # (7, 0)     ->    (7, 7)

    @staticmethod
    def notation2coord(pos: NOTATION) -> COORD:
        # a1 -> (7, 0)
        return 8 - int(pos[1]), ord(pos[0]) - ord('a')
    
    @staticmethod
    def coord2notation(coord: COORD) -> NOTATION:
        # (7, 0) -> a1
        return chr(ord('a') + coord[1]) + str(8 - coord[0])
    
    @staticmethod
    def verify_notation(pos: NOTATION) -> bool:
        return len(pos) == 2 and pos[0] >= 'a' and pos[0] <= 'h' and pos[1] >= '1' and pos[1] <= '8'
    
    @ staticmethod
    def verify_coord(coord: COORD) -> bool:
        return coord[0] >= 0 and coord[0] <= 7 and coord[1] >= 0 and coord[1] <= 7
    
    @staticmethod
    def moves_for_pawn(coord: COORD, board: BOARD) -> List[COORD]:
        row, col = coord
        piece, color = board[row][col]
        is_bound = lambda r, c: (r >= 0 and r <= 7) and (c >= 0 and c <= 7)
        is_empty = lambda r, c: board[r][c] == ' '
        is_opposite = lambda r, c: board[r][c] != ' ' and board[r][c][1] != color
        valid_moves = []
        if color == 'w':
            if row == 6 and is_empty(row - 1, col) and is_empty(row - 2, col): # first double move
                valid_moves.append((row - 2, col))
            if is_bound(row - 1, col) and is_empty(row - 1, col): # straight
                valid_moves.append((row - 1, col))
            if is_bound(row - 1, col - 1) and is_opposite(row - 1, col - 1): # kill
                valid_moves.append((row - 1, col - 1))
            if is_bound(row - 1, col + 1) and is_opposite(row - 1, col + 1): # kill
                valid_moves.append((row - 1, col + 1))
        else:
            # only black pawn needs to be handled based on color as it moves in different direction
            if row == 1 and is_empty(row + 1, col) and is_empty(row + 2, col): # first double move
                valid_moves.append((row + 2, col))
            if is_bound(row + 1, col) and is_empty(row + 1, col): # straight
                valid_moves.append((row + 1, col))
            if is_bound(row + 1, col - 1) and is_opposite(row + 1, col - 1): # kill
                valid_moves.append((row + 1, col - 1))
            if is_bound(row + 1, col + 1) and is_opposite(row + 1, col + 1): # kill
                valid_moves.append((row + 1, col + 1))
        return valid_moves
    
    @staticmethod
    def moves_for_knight(coord: COORD, board: BOARD) -> List[COORD]:
        row, col = coord
        piece, color = board[row][col]
        is_bound = lambda r, c: (r >= 0 and r <= 7) and (c >= 0 and c <= 7)
        is_same = lambda r, c: board[r][c] != ' ' and board[r][c][1] == color
        valid_moves = []
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
        return valid_moves
    
    @staticmethod
    def moves_for_bishop(coord: COORD, board: BOARD) -> List[COORD]:
        row, col = coord
        piece, color = board[row][col]
        is_bound = lambda r, c: (r >= 0 and r <= 7) and (c >= 0 and c <= 7)
        is_same = lambda r, c: board[r][c] != ' ' and board[r][c][1] == color
        is_empty = lambda r, c: board[r][c] == ' '
        valid_moves = []
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
        return valid_moves
    
    @staticmethod
    def moves_for_rook(coord: COORD, board: BOARD) -> List[COORD]:
        row, col = coord
        piece, color = board[row][col]
        is_bound = lambda r, c: (r >= 0 and r <= 7) and (c >= 0 and c <= 7)
        is_same = lambda r, c: board[r][c] != ' ' and board[r][c][1] == color
        is_empty = lambda r, c: board[r][c] == ' '
        valid_moves = []
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
        return valid_moves
    
    @staticmethod
    def moves_for_queen(coord: COORD, board: BOARD) -> List[COORD]:
        valid_moves = chessmenBoardUtility.moves_for_bishop(coord, board)
        valid_moves += chessmenBoardUtility.moves_for_rook(coord, board)
        return valid_moves
    
    @staticmethod
    def moves_for_king(coord: COORD, board: BOARD) -> List[COORD]:
        row, col = coord
        piece, color = board[row][col]
        is_bound = lambda r, c: (r >= 0 and r <= 7) and (c >= 0 and c <= 7)
        is_same = lambda r, c: board[r][c] != ' ' and board[r][c][1] == color
        valid_moves = []
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
    def update_board(board: BOARD, st_coord: COORD, en_coord: COORD, return_copy: bool = False) -> BOARD:
        if return_copy:
            board = deepcopy(board)
        board[en_coord[0]][en_coord[1]] = board[st_coord[0]][st_coord[1]]
        board[st_coord[0]][st_coord[1]] = ' '
        return board
    
    @staticmethod
    def can_piece_reach_target(coord: COORD, board: BOARD, check_color: str = 'w') -> bool:
        ...

    @staticmethod
    def filter_moves_on_king_check(moves: List[COORD], board: BOARD, check_color: str = 'w') -> List[COORD]:
        valid_moves = []
        ...

    @staticmethod
    def get_valid_moves(coord: COORD, board: BOARD, get_notation: bool = False) -> Union[List[COORD], List[NOTATION]]:
        row, col = coord
        piece, color = board[row][col]
        if piece == 'p':
            valid_moves = chessmenBoardUtility.moves_for_pawn(coord, board)
        elif piece == 'n':
            valid_moves = chessmenBoardUtility.moves_for_knight(coord, board)
        elif piece == 'b':
            valid_moves = chessmenBoardUtility.moves_for_bishop(coord, board)
        elif piece == 'r':
            valid_moves = chessmenBoardUtility.moves_for_rook(coord, board)
        elif piece == 'q':
            valid_moves = chessmenBoardUtility.moves_for_queen(coord, board)
        else:
            valid_moves = chessmenBoardUtility.moves_for_king(coord, board)
        if get_notation:
            valid_moves = [chessmenBoardUtility.coord2notation(move) for move in valid_moves]
        return valid_moves
    
    @staticmethod
    def get_target_moves(valid_moves: Union[List[COORD], List[NOTATION]], board: BOARD, user_color: PIECE_COLOR) -> Union[List[COORD], List[NOTATION]]:
        target_moves = []
        for move in valid_moves:
            if isinstance(move, NOTATION):
                coord = chessmenBoardUtility.notation2coord(move)
            else:
                coord = move
            row, col = coord
            piece, color = board[row][col]
            if color != user_color:
                target_moves.append(move)
        return target_moves

