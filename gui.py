import time
import argparse
from typing import List, Optional

from pyglet import image
from avour import Avour, COORD2FLOAT
from avour.utils.math import mapper_1d as mapper
from chessmen import chessmenClient, chessmenMove, chessmenBoardUtility as CBU, COORD, FEN, PIECE_COLOR
from chessmen.engine import START_FEN

class chessmenBoard:
    def __init__(self, user_id: str, sheet_path: str = 'imgs/piece_sheet.png') -> None:
        self.user_id = user_id
        self.load_image_data(sheet_path)
        
        # default setup
        self.set_board(START_FEN, 'white', False)
        
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

        # misc variables
        self.wait_dot_count = 0
        self.wait_dot_last_update = time.time()
        self.wait_dot_update_interval = 0.5 # seconds

        # mouse drag variables
        self.selected_coord: COORD = None
        self.valid_moves: List[chessmenMove] = []
    
    def load_image_data(self, path: str) -> None:
        sheet = image.load(path)
        piece_width, piece_height = 130, 130
        self.image_data = {
            'black': {
                'p': sheet.get_region(0, 307, piece_width, piece_height), # pawn
                'r': sheet.get_region(0, 460, piece_width, piece_height), # rook
                'n': sheet.get_region(149, 462, piece_width, piece_height), # knight
                'b': sheet.get_region(297, 465, piece_width, piece_height), # bishop
                'q': sheet.get_region(445, 465, piece_width, piece_height), # queen
                'k': sheet.get_region(596, 465, piece_width, piece_height), # king
            },
            'white': {
                'p': sheet.get_region(0, 155, piece_width, piece_height), # pawn
                'r': sheet.get_region(0, 10, piece_width, piece_height), # rook
                'n': sheet.get_region(149, 12, piece_width, piece_height), # knight
                'b': sheet.get_region(297, 15, piece_width, piece_height), # bishop
                'q': sheet.get_region(445, 15, piece_width, piece_height), # queen
                'k': sheet.get_region(596, 15, piece_width, piece_height), # king
            }
        }
    
    def set_board(self, fen: FEN, user_color: PIECE_COLOR, user_turn: bool) -> None:
        self.board_state = CBU.fen2board_state(fen)
        self.user_color = user_color
        self.black_side_view = user_color == 'black'
        self.user_turn = user_turn
        self.response_ready = False

    def draw_wait_screen(self, avour: Avour) -> None:
        avour.color(self.C_WHITE)
        text = 'waiting for match '
        text_width = avour._text_width(text, font_size=25)
        avour.text(text + ('.' * self.wait_dot_count), (-text_width / 2, 0), font_size=25, anchor_x='left')
        if time.time() - self.wait_dot_last_update > self.wait_dot_update_interval:
            self.wait_dot_count = (self.wait_dot_count + 1) % 5
            self.wait_dot_last_update = time.time()

    def draw(self, avour: Avour, status: Optional[str]) -> None:
        # background
        avour.background(self.C_BLACK)

        # match does not exist
        if status == None:
            return

        # still waiting for match
        if status == 'in_queue':
            self.draw_wait_screen(avour)
            return

        # else status is 'in_match': found a match
        board = self.board_state.board
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
                    tile = board[7 - row][7 - col]
                else:
                    tile = board[row][col]
                # chess piece
                if tile != ' ':
                    if tile.isupper():
                        piece_image = self.image_data['white'][tile.lower()]
                    else:
                        piece_image = self.image_data['black'][tile]
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
        for move in self.valid_moves:
            coord = move.target_coord
            pos = self.coord2pos(coord)
            pos = (
                pos[0] + self.tile_size / 2,
                pos[1] - self.tile_size / 2
            )
            # valid tile is either empty or opposite piece
            if CBU._is_empty(coord, board):
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

    def _move_piece_and_update_server_response(self, coord: COORD) -> None:
        # check if target location is valid
        selected_move = None
        for move in self.valid_moves:
            if move.target_coord == coord:
                selected_move = move
        # if valid, update the board and set server response
        if selected_move != None:
            self.board_state.update(selected_move)
            # then update server response
            self.user_turn = False
            self.response_ready = True
            # then remove selection
            self._reset_piece_selection()
    
    def _set_piece_selection(self, coord: COORD) -> None:
        self.selected_coord = coord
        self.valid_moves = CBU.get_valid_moves(coord, self.board_state)        

    def _reset_piece_selection(self) -> None:
        self.selected_coord = None
        self.valid_moves = []
    
    def on_mousedown(self, pos: COORD2FLOAT) -> None:
        if not self.user_turn:
            return
        if pos[0] >= self.board_pos[0] and pos[0] <= self.board_pos[0] + self.board_size and pos[1] <= self.board_pos[1] and pos[1] >= self.board_pos[1] - self.board_size:
            coord = self.pos2coord(pos)
            # if selected tile is empty
            if CBU._is_empty(coord, self.board_state.board):
                # if piece has already been selected, move it to empty tile
                if self.selected_coord != None:
                    self._move_piece_and_update_server_response(coord)
                # otherwise remove selection
                else:
                    self._reset_piece_selection()
            # if some piece is selected
            else:
                color = CBU._get_color(coord, self.board_state.board)
                # same color
                if color == self.user_color:
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
                        self._move_piece_and_update_server_response(coord)
    
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

        self.last_status = None
        self.last_status_time = time.time()

    def on_keydown(self, key: str) -> None:
        if key == 'Q' or key == 'ESCAPE':
            self.exit()

    def on_mousedrag(self, pos: COORD2FLOAT, button: str) -> None:
        self.board.on_mousedrag(pos)

    def on_mousedown(self, pos: COORD2FLOAT, button: str) -> None:
        self.board.on_mousedown(pos)

    def draw(self) -> None:
        self.board.draw(self, status=self.last_status)

    def loop(self, dt: float) -> None:
        if time.time() - self.last_status_time > self.REFRESH_TIME:
            status = self.client.status_match()
            if status == None: # match does not exist / has stopped
                self.exit()
            status, payload = status
            # status: in_queue or in_match
            if status == 'in_match':
                fen, user_color, user_turn = payload
                # if it is the user's turn
                # and if there is a waiting response from user
                # send it to server and clear it
                if user_turn and self.board.response_ready:
                    fen = CBU.board_state2fen(self.board.board_state)
                    self.client.update_match(fen)
                    self.board.response_ready = False
                    return
                # set board variables (including user_turn, response_ready)
                self.board.set_board(
                    fen=fen,
                    user_color=user_color,
                    user_turn=user_turn
                )
            self.last_status = status
            self.last_status_time = time.time()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='chessmen client GUI interface')
    parser.add_argument('user_id', help='username for client', type=str)
    args = parser.parse_args()

    app = chessmenGUI(args.user_id)
    app.run()
