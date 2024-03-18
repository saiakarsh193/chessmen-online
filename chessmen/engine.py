from typing import List, Tuple, Optional

class ChessmenBoard:
    def __init__(self):
        self.fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"
        self.turn = 'w'
    
    def fen2board(self, fen: str) -> List[List[str]]:
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
    
    def board2fen(self, board: List[List[str]]) -> str:
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
    
    def flip_board(self, board: List[List[str]]) -> List[List[str]]:
        return [row[::-1] for row in board[::-1]]

    def pos2coord(self, pos: str) -> Tuple[int, int]:
        return 8 - int(pos[1]), ord(pos[0]) - ord('a')
    
    def coord2pos(self, coord: Tuple[int, int]) -> str:
        return chr(ord('a') + coord[1]) + str(8 - coord[0])
    
    def flip_coord(self, coord: Tuple[int, int]) -> Tuple[int, int]:
        return 7 - coord[0], 7 - coord[1]
    
    def format_pos(self, pos: str) -> Optional[str]:
        pos = pos.strip().lower()
        if len(pos) == 2 and pos[0] >= 'a' and pos[0] <= 'h' and pos[1] >= '1' and pos[1] <= '8':
            return pos
        return None

    def get_valid_moves(self, board: List[List[str]], coord: Tuple[int, int]) -> List[Tuple[int, int]]:
        row, col = coord
        piece, color = board[row][col]
        is_bound = lambda row, col: (row >= 0 and row <= 7) and (col >= 0 and col <= 7)
        is_same = lambda row, col: board[row][col] != ' ' and board[row][col][1] == color
        is_opposite = lambda row, col: board[row][col] != ' ' and board[row][col][1] != color
        is_empty = lambda row, col: board[row][col] == ' '
        valid_moves = []
        if piece == 'p':
            if row == 6 and is_empty(row - 1, col) and is_empty(row - 2, col): # first double move
                valid_moves.append((row - 2, col))
            if is_bound(row - 1, col) and is_empty(row - 1, col): # straight
                valid_moves.append((row - 1, col))
            if is_bound(row - 1, col - 1) and is_opposite(row - 1, col - 1): # kill
                valid_moves.append((row - 1, col - 1))
            if is_bound(row - 1, col + 1) and is_opposite(row - 1, col + 1): # kill
                valid_moves.append((row - 1, col + 1))
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

    def display(self) -> None:
        board = self.fen2board(self.fen)
        if self.turn == 'b':
            board = self.flip_board(board)
        row_sep = '  ' + '=====' * 8 + '='
        for row in range(8):
            print(row_sep)
            for col in range(8):
                if col == 0:
                    print(str(8 - row) if self.turn == 'w' else str(row + 1), end=' ')
                back = '-' if (row + col) % 2 else ' '
                piece = board[row][col] if board[row][col] != ' ' else back * 2
                print(f'|{back}{piece}{back}', end='')
                if col == 7:
                    print('|')
            if row == 7:
                print(row_sep)
        l_not = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
        print('    '.join([''] + (l_not if self.turn == 'w' else l_not[::-1])))
    
    def run(self):
        while True:
            self.display()
            board = self.fen2board(self.fen)
            inp = input(f"({self.turn})> ").strip().split()
            if len(inp) != 2:
                print("invalid format")
                continue
            st, en = self.format_pos(inp[0]), self.format_pos(inp[1])
            if st == None or en == None:
                print("invalid position (bound)")
                continue
            st_coord = self.pos2coord(st)
            en_coord = self.pos2coord(en)
            if board[st_coord[0]][st_coord[1]] == ' ':
                print("invalid position (no piece)")
                continue
            if board[st_coord[0]][st_coord[1]][1] != self.turn:
                print("invalid position (opp piece)")
                continue
            if self.turn == 'b':
                board = self.flip_board(board)
                st_coord = self.flip_coord(st_coord)
                en_coord = self.flip_coord(en_coord)
            valid_moves = self.get_valid_moves(board, st_coord)
            if self.turn == 'b':
                valid_moves = [self.flip_coord(move) for move in valid_moves]
            valid_moves = [self.coord2pos(move) for move in valid_moves]
            if not en in valid_moves:
                print("invalid move, valid:", ' '.join(valid_moves))
                continue
            board[en_coord[0]][en_coord[1]] = board[st_coord[0]][st_coord[1]]
            board[st_coord[0]][st_coord[1]] = ' '
            if self.turn == 'b':
                board = self.flip_board(board)
            self.fen = self.board2fen(board)
            self.turn = 'w' if self.turn == 'b' else 'b'

cb = ChessmenBoard()
cb.run()
