from dataclasses import dataclass
from typing import List, Tuple, Optional, Literal, Union, Dict, Callable

FEN = str
BOARD = List[List[str]]
COORD = Tuple[int, int]
NOTATION = str

START_FEN: FEN = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
PIECE_COLOR = Literal['black', 'white']
PIECE_COLOR_MAP = {'b': 'black', 'w': 'white'}
MOVE_TYPE = Literal['normal', 'enable_en_passant', 'en_passant', 'disable_castling', 'castling']

@dataclass
class chessmenMove:
    target_coord: COORD
    start_coord: Optional[COORD] = None
    move_type: MOVE_TYPE = 'normal'
    extra_coord: Optional[COORD] = None

    def notation(self) -> str:
        return chessmenBoardUtility.coord2notation(self.target_coord)

@dataclass
class chessmenBoardState:
    # FEN: Forsyth–Edwards Notation (https://en.wikipedia.org/wiki/Forsyth–Edwards_Notation)

    board: BOARD
    active_color: PIECE_COLOR
    castling_availability: str
    en_passant_target: NOTATION
    half_moves: int
    full_moves: int

    def update(self, move: chessmenMove) -> None:
        # check validity of start coord (piece that is moved)
        assert move.start_coord != None
        assert chessmenBoardUtility._get_color(move.start_coord, self.board) == self.active_color
        # move the main piece
        self.board[move.target_coord[0]][move.target_coord[1]] = self.board[move.start_coord[0]][move.start_coord[1]]
        self.board[move.start_coord[0]][move.start_coord[1]] = ' '
        # handle extra piece (en passant or castling) and set state flags
        piece = self.board[move.target_coord[0]][move.target_coord[1]].lower()
        self.update_en_passant_target() # always reset en passant at every move
        if piece == 'p': # handling en passant
            if move.move_type == 'enable_en_passant':
                self.update_en_passant_target(move.extra_coord)
            else:
                if move.move_type == 'en_passant': # kill the opponent pawn
                    self.board[move.extra_coord[0]][move.extra_coord[1]] = ' '
        elif piece == 'r': # handling castling
            if move.move_type == 'disable_castling':
                if 'Q' in self.castling_availability and move.extra_coord == (7, 0):
                    self.update_castling_availability('Q')
                elif 'K' in self.castling_availability and move.extra_coord == (7, 7):
                    self.update_castling_availability('K')
                elif 'q' in self.castling_availability and move.extra_coord == (0, 0):
                    self.update_castling_availability('q')
                elif 'k' in self.castling_availability and move.extra_coord == (0, 7):
                    self.update_castling_availability('k')
        elif piece == 'k': # handling castling
            if move.move_type == 'disable_castling':
                if ('Q' in self.castling_availability or 'K' in self.castling_availability) and move.extra_coord == (7, 4):
                    self.update_castling_availability('Q')
                    self.update_castling_availability('K')
                elif ('q' in self.castling_availability or 'k' in self.castling_availability) and move.extra_coord == (0, 4):
                    self.update_castling_availability('q')
                    self.update_castling_availability('k')
            if move.move_type == 'castling':
                if 'Q' in self.castling_availability and move.extra_coord == (7, 3):
                    self.board[7][0] = ' '
                    self.board[7][3] = 'R'
                    self.update_castling_availability('Q')
                    self.update_castling_availability('K')
                elif 'K' in self.castling_availability and move.extra_coord == (7, 5):
                    self.board[7][7] = ' '
                    self.board[7][5] = 'R'
                    self.update_castling_availability('Q')
                    self.update_castling_availability('K')
                elif 'q' in self.castling_availability and move.extra_coord == (0, 3):
                    self.board[0][0] = ' '
                    self.board[0][3] = 'r'
                    self.update_castling_availability('q')
                    self.update_castling_availability('k')
                elif 'k' in self.castling_availability and move.extra_coord == (0, 5):
                    self.board[0][7] = ' '
                    self.board[0][5] = 'r'
                    self.update_castling_availability('q')
                    self.update_castling_availability('k')

        # switch the active color
        self.switch_active_color()

    def switch_active_color(self) -> None:
        self.active_color = 'black' if self.active_color == 'white' else 'white'
        if self.active_color == 'white': # update full move after black's move
            self.full_moves += 1
    
    def update_castling_availability(self, piece: str) -> None:
        castling_availability = list(self.castling_availability)
        if piece in castling_availability:
            castling_availability.remove(piece)
        if len(castling_availability) == 0:
            castling_availability = ['-']
        self.castling_availability = ''.join(castling_availability)

    def update_en_passant_target(self, pos: Optional[Union[NOTATION, COORD]] = None) -> None:
        if pos == None:
            self.en_passant_target = '-'
        else:
            if not isinstance(pos, NOTATION):
                pos = chessmenBoardUtility.coord2notation(pos)
            self.en_passant_target = pos

class chessmenBoardUtility:
    @staticmethod
    def board_string2board(board_str: str) -> BOARD:
        board = []
        rows = board_str.split('/')
        for row in rows:
            board_row = []
            for col in row:
                if col.isdigit():
                    board_row += [' '] * int(col)
                else:
                    board_row.append(col)
            board.append(board_row)
        return board

    @staticmethod
    def board2board_string(board: BOARD) -> str:
        board_str = []
        for row in board:
            ctr = 0
            for i, col in enumerate(row):
                if col == ' ':
                    ctr += 1
                if col != ' ' or i == 7:
                    if ctr > 0:
                        board_str.append(str(ctr))
                    if col != ' ':
                        board_str.append(col)
                    ctr = 0
            board_str.append('/')
        return ''.join(board_str[: -1])

    @staticmethod
    def fen2board_state(fen: FEN) -> chessmenBoardState:
        board_str, active_color, castling_availability, en_passant_target, half_moves, full_moves = fen.split()
        return chessmenBoardState(
            board=chessmenBoardUtility.board_string2board(board_str=board_str),
            active_color=PIECE_COLOR_MAP[active_color],
            castling_availability=castling_availability,
            en_passant_target=en_passant_target,
            half_moves=int(half_moves),
            full_moves=int(full_moves)
        )

    @staticmethod
    def board_state2fen(board_state: chessmenBoardState) -> FEN:
        return ' '.join([
            chessmenBoardUtility.board2board_string(board=board_state.board),
            board_state.active_color[0],
            board_state.castling_availability,
            board_state.en_passant_target,
            str(board_state.half_moves),
            str(board_state.full_moves)
        ])
    
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
    # r
    #
    #
    #
    #
    # R
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
    
    @staticmethod
    def verify_coord(coord: COORD) -> bool:
        return coord[0] >= 0 and coord[0] <= 7 and coord[1] >= 0 and coord[1] <= 7
    
    @staticmethod
    def _get_color(coord: COORD, board: BOARD) -> Optional[PIECE_COLOR]:
        if board[coord[0]][coord[1]] == ' ':
            return None
        elif board[coord[0]][coord[1]].islower():
            return 'black'
        return 'white'
    
    @staticmethod
    def _is_inside(coord: COORD) -> bool:
        return chessmenBoardUtility.verify_coord(coord)
        
    @staticmethod
    def _is_empty(coord: COORD, board: BOARD) -> bool:
        return board[coord[0]][coord[1]] == ' '
    
    @staticmethod
    def _is_same(coord: COORD, target_coord: COORD, board: BOARD) -> bool:
        c1 = chessmenBoardUtility._get_color(coord, board)
        c2 = chessmenBoardUtility._get_color(target_coord, board)
        # both should be pieces and same
        if c1 == None or c2 == None:
            return False
        return c1 == c2
    
    @staticmethod
    def _is_opposite(coord: COORD, target_coord: COORD, board: BOARD) -> bool:
        c1 = chessmenBoardUtility._get_color(coord, board)
        c2 = chessmenBoardUtility._get_color(target_coord, board)
        # both should be pieces and not same
        if c1 == None or c2 == None:
            return False
        return c1 != c2
    
    @staticmethod
    def moves_for_pawn(coord: COORD, board_state: chessmenBoardState) -> List[chessmenMove]:
        row, col = coord
        board = board_state.board
        get_color = lambda r, c: chessmenBoardUtility._get_color((r, c), board)
        is_inside = lambda r, c: chessmenBoardUtility._is_inside((r, c))
        is_empty = lambda r, c: chessmenBoardUtility._is_empty((r, c), board)
        is_opposite = lambda r, c: chessmenBoardUtility._is_opposite(coord, (r, c), board)
        valid_moves: List[chessmenMove] = []
        if get_color(row, col) == 'white':
            if row == 6 and is_empty(row - 1, col) and is_empty(row - 2, col): # first double move -> enable en passant
                valid_moves.append(chessmenMove((row - 2, col), move_type='enable_en_passant', extra_coord=(row - 1, col)))
            if board_state.en_passant_target != '-' and row == 3: # possible en passant
                en_passant_target = chessmenBoardUtility.notation2coord(board_state.en_passant_target)
                if is_inside(row - 1, col - 1) and is_empty(row - 1, col - 1) and en_passant_target == (row - 1, col - 1):
                    valid_moves.append(chessmenMove((row - 1, col - 1), move_type='en_passant', extra_coord=(row, col - 1)))
                if is_inside(row - 1, col + 1) and is_empty(row - 1, col + 1) and en_passant_target == (row - 1, col + 1):
                    valid_moves.append(chessmenMove((row - 1, col + 1), move_type='en_passant', extra_coord=(row, col + 1)))
            if is_inside(row - 1, col) and is_empty(row - 1, col): # straight
                valid_moves.append(chessmenMove((row - 1, col)))
            if is_inside(row - 1, col - 1) and is_opposite(row - 1, col - 1): # kill
                valid_moves.append(chessmenMove((row - 1, col - 1)))
            if is_inside(row - 1, col + 1) and is_opposite(row - 1, col + 1): # kill
                valid_moves.append(chessmenMove((row - 1, col + 1)))
        else:
            # only black pawn needs to be handled based on color as it moves in different direction than standard
            if row == 1 and is_empty(row + 1, col) and is_empty(row + 2, col): # first double move -> enable en passant
                valid_moves.append(chessmenMove((row + 2, col), move_type='enable_en_passant', extra_coord=(row + 1, col)))
            if board_state.en_passant_target != '-' and row == 4: # possible en passant
                en_passant_target = chessmenBoardUtility.notation2coord(board_state.en_passant_target)
                if is_inside(row + 1, col - 1) and is_empty(row + 1, col - 1) and en_passant_target == (row + 1, col - 1):
                    valid_moves.append(chessmenMove((row + 1, col - 1), move_type='en_passant', extra_coord=(row, col - 1)))
                if is_inside(row + 1, col + 1) and is_empty(row + 1, col + 1) and en_passant_target == (row + 1, col + 1):
                    valid_moves.append(chessmenMove((row + 1, col + 1), move_type='en_passant', extra_coord=(row, col + 1)))
            if is_inside(row + 1, col) and is_empty(row + 1, col): # straight
                valid_moves.append(chessmenMove((row + 1, col)))
            if is_inside(row + 1, col - 1) and is_opposite(row + 1, col - 1): # kill
                valid_moves.append(chessmenMove((row + 1, col - 1)))
            if is_inside(row + 1, col + 1) and is_opposite(row + 1, col + 1): # kill
                valid_moves.append(chessmenMove((row + 1, col + 1)))
        for move in valid_moves:
            move.start_coord = (row, col)
        return valid_moves
    
    @staticmethod
    def moves_for_knight(coord: COORD, board_state: chessmenBoardState) -> List[chessmenMove]:
        row, col = coord
        board = board_state.board
        is_inside = lambda r, c: chessmenBoardUtility._is_inside((r, c))
        is_empty = lambda r, c: chessmenBoardUtility._is_empty((r, c), board)
        is_opposite = lambda r, c: chessmenBoardUtility._is_opposite(coord, (r, c), board)
        valid_moves: List[chessmenMove] = []
        if is_inside(row - 2, col - 1) and (is_empty(row - 2, col - 1) or is_opposite(row - 2, col - 1)):
            valid_moves.append(chessmenMove((row - 2, col - 1)))
        if is_inside(row - 2, col + 1) and (is_empty(row - 2, col + 1) or is_opposite(row - 2, col + 1)):
            valid_moves.append(chessmenMove((row - 2, col + 1)))
        if is_inside(row - 1, col - 2) and (is_empty(row - 1, col - 2) or is_opposite(row - 1, col - 2)):
            valid_moves.append(chessmenMove((row - 1, col - 2)))
        if is_inside(row - 1, col + 2) and (is_empty(row - 1, col + 2) or is_opposite(row - 1, col + 2)):
            valid_moves.append(chessmenMove((row - 1, col + 2)))
        if is_inside(row + 1, col - 2) and (is_empty(row + 1, col - 2) or is_opposite(row + 1, col - 2)):
            valid_moves.append(chessmenMove((row + 1, col - 2)))
        if is_inside(row + 1, col + 2) and (is_empty(row + 1, col + 2) or is_opposite(row + 1, col + 2)):
            valid_moves.append(chessmenMove((row + 1, col + 2)))
        if is_inside(row + 2, col - 1) and (is_empty(row + 2, col - 1) or is_opposite(row + 2, col - 1)):
            valid_moves.append(chessmenMove((row + 2, col - 1)))
        if is_inside(row + 2, col + 1) and (is_empty(row + 2, col + 1) or is_opposite(row + 2, col + 1)):
            valid_moves.append(chessmenMove((row + 2, col + 1)))
        for move in valid_moves:
            move.start_coord = (row, col)
        return valid_moves
    
    @staticmethod
    def _moves_linear_unblocked(coords: List[COORD], is_inside: Callable, is_empty: Callable, is_opposite: Callable) -> List[chessmenMove]:
        valid_moves = []
        for row, col in coords:
            if is_inside(row, col):
                if is_empty(row, col): # empty to move
                    valid_moves.append(chessmenMove((row, col)))
                else:
                    if is_opposite(row, col): # kill
                        valid_moves.append(chessmenMove((row, col)))
                    break
            else:
                break
        return valid_moves
    
    @staticmethod
    def moves_for_bishop(coord: COORD, board_state: chessmenBoardState) -> List[chessmenMove]:
        row, col = coord
        board = board_state.board
        is_inside = lambda r, c: chessmenBoardUtility._is_inside((r, c))
        is_empty = lambda r, c: chessmenBoardUtility._is_empty((r, c), board)
        is_opposite = lambda r, c: chessmenBoardUtility._is_opposite(coord, (r, c), board)
        valid_moves: List[chessmenMove] = []
        valid_moves += chessmenBoardUtility._moves_linear_unblocked([(row - i, col - i) for i in range(1, min(row, col) + 1)], is_inside, is_empty, is_opposite) # left top
        valid_moves += chessmenBoardUtility._moves_linear_unblocked([(row - i, col + i) for i in range(1, min(row, 7 - col) + 1)], is_inside, is_empty, is_opposite) # right top
        valid_moves += chessmenBoardUtility._moves_linear_unblocked([(row + i, col - i) for i in range(1, min(7 - row, col) + 1)], is_inside, is_empty, is_opposite) # bottom left
        valid_moves += chessmenBoardUtility._moves_linear_unblocked([(row + i, col + i) for i in range(1, min(7 - row, 7 - col) + 1)], is_inside, is_empty, is_opposite) # bottom right
        for move in valid_moves:
            move.start_coord = (row, col)
        return valid_moves
    
    @staticmethod
    def moves_for_rook(coord: COORD, board_state: chessmenBoardState, for_queen: bool = False) -> List[chessmenMove]:
        row, col = coord
        board = board_state.board
        is_inside = lambda r, c: chessmenBoardUtility._is_inside((r, c))
        is_empty = lambda r, c: chessmenBoardUtility._is_empty((r, c), board)
        is_opposite = lambda r, c: chessmenBoardUtility._is_opposite(coord, (r, c), board)
        valid_moves: List[chessmenMove] = []
        valid_moves += chessmenBoardUtility._moves_linear_unblocked([(row, col - i) for i in range(1, col + 1)], is_inside, is_empty, is_opposite) # left
        valid_moves += chessmenBoardUtility._moves_linear_unblocked([(row - i, col) for i in range(1, row + 1)], is_inside, is_empty, is_opposite) # top
        valid_moves += chessmenBoardUtility._moves_linear_unblocked([(row, col + i) for i in range(1, (7 - col) + 1)], is_inside, is_empty, is_opposite) # right
        valid_moves += chessmenBoardUtility._moves_linear_unblocked([(row + i, col) for i in range(1, (7 - row) + 1)], is_inside, is_empty, is_opposite) # bottom
        if not for_queen:
            # disable castling after moving the rook
            for move in valid_moves:
                move.move_type = 'disable_castling'
                move.extra_coord = (row, col)
        for move in valid_moves:
            move.start_coord = (row, col)
        return valid_moves
    
    @staticmethod
    def moves_for_queen(coord: COORD, board_state: chessmenBoardState) -> List[chessmenMove]:
        valid_moves = chessmenBoardUtility.moves_for_bishop(coord, board_state)
        valid_moves += chessmenBoardUtility.moves_for_rook(coord, board_state, for_queen=True)
        return valid_moves
    
    @staticmethod
    def _get_castling_move(color: PIECE_COLOR, board: BOARD, queen_side: bool = True) -> Optional[chessmenMove]:
        row = 7 if color == 'white' else 0
        cols = [0, 1, 2, 3, 4] if queen_side else [4, 5, 6, 7]
        for i, col in enumerate(cols):
            # all cols between rook and king should be empty
            if i > 0 and i < len(cols) - 1:
                if not chessmenBoardUtility._is_empty((row, col), board):
                    return None
            # check (row, col) should not be under check
            pass
        # only king can initiate castling
        if queen_side:
            return chessmenMove((row, 2), move_type='castling', extra_coord=(row, 3))
        else:
            return chessmenMove((row, 6), move_type='castling', extra_coord=(row, 5))
    
    @staticmethod
    def moves_for_king(coord: COORD, board_state: chessmenBoardState) -> List[chessmenMove]:
        row, col = coord
        board = board_state.board
        is_inside = lambda r, c: chessmenBoardUtility._is_inside((r, c))
        is_empty = lambda r, c: chessmenBoardUtility._is_empty((r, c), board)
        is_opposite = lambda r, c: chessmenBoardUtility._is_opposite(coord, (r, c), board)
        valid_moves: List[chessmenMove] = []
        if is_inside(row - 1, col - 1) and (is_empty(row - 1, col - 1) or is_opposite(row - 1, col - 1)):
            valid_moves.append(chessmenMove((row - 1, col - 1)))
        if is_inside(row - 1, col)and (is_empty(row - 1, col) or is_opposite(row - 1, col)):
            valid_moves.append(chessmenMove((row - 1, col)))
        if is_inside(row - 1, col + 1) and (is_empty(row - 1, col + 1) or is_opposite(row - 1, col + 1)):
            valid_moves.append(chessmenMove((row - 1, col + 1)))
        if is_inside(row, col - 1) and (is_empty(row, col - 1) or is_opposite(row, col - 1)):
            valid_moves.append(chessmenMove((row, col - 1)))
        if is_inside(row, col + 1) and (is_empty(row, col + 1) or is_opposite(row, col + 1)):
            valid_moves.append(chessmenMove((row, col + 1)))
        if is_inside(row + 1, col - 1) and (is_empty(row + 1, col - 1) or is_opposite(row + 1, col - 1)):
            valid_moves.append(chessmenMove((row + 1, col - 1)))
        if is_inside(row + 1, col) and (is_empty(row + 1, col) or is_opposite(row + 1, col)):
            valid_moves.append(chessmenMove((row + 1, col)))
        if is_inside(row + 1, col + 1) and (is_empty(row + 1, col + 1) or is_opposite(row + 1, col + 1)):
            valid_moves.append(chessmenMove((row + 1, col + 1)))
        # disable castling after moving the king
        for move in valid_moves:
            move.move_type = 'disable_castling'
            move.extra_coord = (row, col)
        # for castling
        get_color = lambda r, c: chessmenBoardUtility._get_color((r, c), board)
        color = get_color(row, col)
        if color == 'white':
            if 'Q' in board_state.castling_availability:
                move = chessmenBoardUtility._get_castling_move(color, board, queen_side=True)
                if move != None:
                    valid_moves.append(move)
            if 'K' in board_state.castling_availability:
                move = chessmenBoardUtility._get_castling_move(color, board, queen_side=False)
                if move != None:
                    valid_moves.append(move)
        else:
            if 'q' in board_state.castling_availability:
                move = chessmenBoardUtility._get_castling_move(color, board, queen_side=True)
                if move != None:
                    valid_moves.append(move)
            if 'k' in board_state.castling_availability:
                move = chessmenBoardUtility._get_castling_move(color, board, queen_side=False)
                if move != None:
                    valid_moves.append(move)
        for move in valid_moves:
            move.start_coord = (row, col)
        return valid_moves
    
    @staticmethod
    def can_color_reach_target(coord: COORD, board: BOARD, check_color: str = 'w') -> bool:
        ...

    @staticmethod
    def filter_moves_on_king_check(moves: List[COORD], board: BOARD, check_color: str = 'w') -> List[COORD]:
        valid_moves = []
        ...

    @staticmethod
    def get_valid_moves(coord: COORD, board_state: chessmenBoardState) -> List[chessmenMove]:
        row, col = coord
        board = board_state.board
        piece = board[row][col].lower()
        if piece == 'p':
            valid_moves = chessmenBoardUtility.moves_for_pawn(coord, board_state)
        elif piece == 'n':
            valid_moves = chessmenBoardUtility.moves_for_knight(coord, board_state)
        elif piece == 'b':
            valid_moves = chessmenBoardUtility.moves_for_bishop(coord, board_state)
        elif piece == 'r':
            valid_moves = chessmenBoardUtility.moves_for_rook(coord, board_state)
        elif piece == 'q':
            valid_moves = chessmenBoardUtility.moves_for_queen(coord, board_state)
        elif piece == 'k':
            valid_moves = chessmenBoardUtility.moves_for_king(coord, board_state)
        else:
            valid_moves = []
        return valid_moves
    
    @staticmethod
    def get_target_moves(valid_moves: List[chessmenMove], board_state: chessmenBoardState) -> List[chessmenMove]:
        board = board_state.board
        target_moves = []
        for move in valid_moves:
            assert move.start_coord != None
            if chessmenBoardUtility._is_opposite(move.start_coord, move.target_coord, board):
                target_moves.append(move)
        return target_moves

    @staticmethod
    def get_missing_pieces(board_state: chessmenBoardState, user_color: PIECE_COLOR) -> Dict[str, int]:
        if user_color == 'white':
            missing_pieces = {'P': 0, 'R': 0, 'N': 0, 'B': 0, 'Q': 0, 'K': 0}
        else:
            missing_pieces = {'p': 0, 'r': 0, 'n': 0, 'b': 0, 'q': 0, 'k': 0}
        for row in board_state.board:
            for col in row:
                if col in missing_pieces:
                    missing_pieces[col] += 1
        for piece in missing_pieces:
            if piece.lower() == 'p':
                missing_pieces[piece] = 8 - missing_pieces[piece]
            elif piece.lower() in ['r', 'n', 'b']:
                missing_pieces[piece] = 2 - missing_pieces[piece]
            else:
                missing_pieces[piece] = 1 - missing_pieces[piece]
        return {piece: val for piece, val in missing_pieces.items() if val > 0}

if __name__ == '__main__':
    print(START_FEN)
    board_state = chessmenBoardUtility.fen2board_state(START_FEN)
    print(board_state)
    print(chessmenBoardUtility.board_state2fen(board_state))
    valid_moves = chessmenBoardUtility.get_valid_moves((7, 1), board_state)
    print(valid_moves)
    board_state.update(valid_moves[0])
    print(board_state)
    valid_moves = chessmenBoardUtility.get_valid_moves((5, 0), board_state)
    print(valid_moves)