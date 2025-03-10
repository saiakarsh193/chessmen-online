import time
import argparse
from typing import List

from pyglet import image
from avour import Avour, COORD2FLOAT
from avour.utils.math import mapper_1d as mapper
from chessmen import chessmenClient, chessmenBoardUtility as CBU, COORD, BOARD, FEN, PIECE_COLOR
from chessmen.engine import START_FEN

class chessmenBoard:
    def __init__(self, user_id: str, sheet_path: str = 'imgs/piece_sheet.png') -> None:
        self.user_id = user_id
        self.load_image_data(sheet_path)
        
        # default setup
        self.set_board(START_FEN, 'white', 'white')
        self.user_turn = False
        
        # drawing variables
        self.board_size = 650
        self.board_pos = (-self.board_size / 2, self.board_size / 2)
        self.tile_size = self.board_size / 8
        self.valid_tile_radius = 0.9 * self.tile_size / 2
        self.target_tile_radius = 0.7 * self.tile_size / 2
        self.column_marker = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']

        # drawing colors variables
        self.C_GREEN = (119, 150, 87)
        self.C_WHITE = (238, 239, 211)
        self.C_BLACK = (38, 36, 34)
        self.C_VALID = (100, 100, 100, 120)

        # mouse drag variables
        self.selected_coord: COORD = None
        self.selected_coord_valid_moves: List[COORD] = []
    
    def load_image_data(self, path: str) -> None:
        sheet = image.load(path)
        self.image_color_map = {'b': 'black', 'w': 'white'}
        self.image_piece_map = {'p': 'pawn', 'r': 'rook', 'n': 'knight', 'b': 'bishop', 'q': 'queen', 'k': 'king'}
        piece_width, piece_height = 130, 130
        self.image_data = {
            'black': {
                'pawn': sheet.get_region(0, 307, piece_width, piece_height),
                'rook': sheet.get_region(0, 460, piece_width, piece_height),
                'knight': sheet.get_region(149, 462, piece_width, piece_height),
                'bishop': sheet.get_region(297, 465, piece_width, piece_height),
                'queen': sheet.get_region(445, 465, piece_width, piece_height),
                'king': sheet.get_region(596, 465, piece_width, piece_height),
            },
            'white': {
                'pawn': sheet.get_region(0, 155, piece_width, piece_height),
                'rook': sheet.get_region(0, 10, piece_width, piece_height),
                'knight': sheet.get_region(149, 12, piece_width, piece_height),
                'bishop': sheet.get_region(297, 15, piece_width, piece_height),
                'queen': sheet.get_region(445, 15, piece_width, piece_height),
                'king': sheet.get_region(596, 15, piece_width, piece_height),
            }
        }
    
    def set_board(self, fen: FEN, user_color: PIECE_COLOR, turn: PIECE_COLOR) -> None:
        self.board = CBU.convert_fen2board(fen)
        self.user_color = user_color
        self.black_side_view = user_color == 'black'
        self.user_turn = user_color == turn
        self.response_ready = False

    def get_board(self) -> FEN:
        return CBU.convert_board2fen(self.board)

    def draw(self, avour: Avour) -> None:
        # background
        avour.background(self.C_BLACK)

        if self.board == None:
            return

        # board
        avour.fill(True)
        for row in range(8):
            for col in range(8):
                # black or white tile color
                tile_color = self.C_GREEN if (row + col) % 2 else self.C_WHITE
                avour.color(tile_color)
                pos = (
                    mapper(col, 0, 8, self.board_pos[0], self.board_pos[0] + self.board_size),
                    mapper(row, 0, 8, self.board_pos[1], self.board_pos[1] - self.board_size)
                )
                # cornered tiles
                if row == 0 and col == 0:
                    avour.rect(pos, self.tile_size, self.tile_size, radius=(0, 10, 0, 0), segments=5)
                elif row == 0 and col == 7:
                    avour.rect(pos, self.tile_size, self.tile_size, radius=(0, 0, 10, 0), segments=5)
                elif row == 7 and col == 7:
                    avour.rect(pos, self.tile_size, self.tile_size, radius=(0, 0, 0, 10), segments=5)
                elif row == 7 and col == 0:
                    avour.rect(pos, self.tile_size, self.tile_size, radius=(10, 0, 0, 0), segments=5)
                else:
                    avour.rect(pos, self.tile_size, self.tile_size)
                if self.black_side_view:
                    tile = self.board[7 - row][7 - col]
                else:
                    tile = self.board[row][col]
                # chess piece
                if tile != ' ':
                    piece, color = tile
                    piece_image = self.image_data[self.image_color_map[color]][self.image_piece_map[piece]]
                    piece_pos = (
                        pos[0] + 5,
                        pos[1] - 5
                    )
                    avour.sprite(piece_image, piece_pos, scale=0.55)
                # row marking
                if col == 0:
                    text_color = self.C_WHITE if (row + col) % 2 else self.C_GREEN
                    text_pos = (
                        pos[0] + 2,
                        pos[1] - 0
                    )
                    avour.color(text_color)
                    text_row = (row + 1) if self.black_side_view else (8 - row)
                    avour.text(str(text_row), text_pos, font_size=15, anchor_x='left', anchor_y='top')
                # col marking
                if row == 7:
                    text_color = self.C_WHITE if (row + col) % 2 else self.C_GREEN
                    text_pos = (
                        pos[0] + self.tile_size - 4,
                        pos[1] - self.tile_size + 2
                    )
                    text_col = (7 - col) if self.black_side_view else col
                    avour.color(text_color)
                    avour.text(self.column_marker[text_col], text_pos, font_size=15, anchor_x='right', anchor_y='bottom')
        
        # valid / target moves
        for coord in self.selected_coord_valid_moves:
            pos = self.coord2pos(coord)
            pos = (
                pos[0] + self.tile_size / 2,
                pos[1] - self.tile_size / 2
            )
            row, col = coord
            tile = self.board[row][col]
            # valid tile is either empty or opposite piece
            if tile == ' ':
                avour.color(self.C_VALID)
                avour.circle(pos, self.valid_tile_radius)
            # opposite piece is a target move
            else:
                avour.color(self.C_VALID)
                avour.fill(False)
                avour.thickness(self.valid_tile_radius - self.target_tile_radius)
                avour.circle(pos, self.valid_tile_radius)
                avour.fill(True)

    def pos2coord(self, pos: COORD2FLOAT) -> COORD:
        # x axis is col, y axis is row
        pos = (pos[0] - self.board_pos[0], -(pos[1] - self.board_pos[1]))
        coord = int(pos[1] / self.tile_size), int(pos[0] / self.tile_size)
        if self.black_side_view:
            return 7 - coord[0], 7 - coord[1]
        return coord
    
    def coord2pos(self, coord: COORD) -> COORD2FLOAT:
        if self.black_side_view:
            coord = 7 - coord[0], 7 - coord[1]
        # x axis is col, y axis is row
        pos = (coord[1] * self.tile_size, coord[0] * self.tile_size)
        return (pos[0] + self.board_pos[0], -pos[1] + self.board_pos[1])

    def _move_piece_and_update_server(self, coord: COORD) -> None:
        # check if target location is valid
        if coord in self.selected_coord_valid_moves:
            CBU.update_board(self.board, self.selected_coord, coord)
            # then remove selection
            self._reset_piece_selection()
            # then update server
            self.user_turn = False
            self.response_ready = True
    
    def _set_piece_selection(self, coord: COORD) -> None:
        self.selected_coord = coord
        self.selected_coord_valid_moves = CBU.get_valid_moves(coord, self.board)        

    def _reset_piece_selection(self) -> None:
        self.selected_coord = None
        self.selected_coord_valid_moves = []
    
    def on_mousedown(self, pos: COORD2FLOAT) -> None:
        if not self.user_turn:
            return
        if pos[0] >= self.board_pos[0] and pos[0] <= self.board_pos[0] + self.board_size and pos[1] <= self.board_pos[1] and pos[1] >= self.board_pos[1] - self.board_size:
            coord = self.pos2coord(pos)
            row, col = coord
            tile = self.board[row][col]
            # if selected tile is empty
            if tile == ' ':
                # if piece has already been selected, move it to empty tile
                if self.selected_coord != None:
                    self._move_piece_and_update_server(coord)
                # otherwise remove selection
                else:
                    self._reset_piece_selection()
            # if some piece is selected
            else:
                piece, color = tile
                # same color
                if color == self.user_color[0]:
                    # if clicked on the already selected piece, remove selection
                    if coord == self.selected_coord:
                        self._reset_piece_selection()
                    # otherwise select the piece and calculate valid moves
                    else:
                        self._set_piece_selection(coord)
                # opposite color
                else:
                    # if piece has already been selected, move it to opposite piece tile
                    if self.selected_coord != None:
                        self._move_piece_and_update_server(coord)
    
    def on_mousedrag(self, pos: COORD2FLOAT) -> None:
        ...

class chessmenGUI(Avour):
    REFRESH_TIME = 1 # seconds

    def __init__(self, user_id: str) -> None:
        super().__init__(screen_title='chessmen online', show_fps=True)
        self.set_frame_rate(80)
        screen_size = self.get_screen_size()
        self.translate((screen_size[0] / 2, screen_size[1] / 2))
        
        self.client = chessmenClient(user_id=user_id)
        self.board = chessmenBoard(user_id=self.client.user_id)
        assert self.client.find_match()

        self.last_status_time = time.time()

    def on_keydown(self, key: str) -> None:
        if key == 'Q' or key == 'ESCAPE':
            self.exit()

    def on_mousedrag(self, pos: COORD2FLOAT, button: str) -> None:
        self.board.on_mousedrag(pos)

    def on_mousedown(self, pos: COORD2FLOAT, button: str) -> None:
        self.board.on_mousedown(pos)

    def draw(self) -> None:
        self.board.draw(self)

    def loop(self, dt: float) -> None:
        if time.time() - self.last_status_time > self.REFRESH_TIME:
            status = self.client.status_match()
            if status == None: # match does not exist / has stopped
                self.exit()
            status, payload = status
            # status: in_queue or in_match
            if status == 'in_match':
                fen, user_color, turn = payload
                if self.board.response_ready:
                    self.client.update_match(self.board.get_board())
                self.board.set_board(
                    fen=fen,
                    user_color=user_color,
                    turn=turn
                )
            self.last_status_time = time.time()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='chessmen client GUI interface')
    parser.add_argument('user_id', help='username for client', type=str)
    args = parser.parse_args()

    app = chessmenGUI(args.user_id)
    app.run()
