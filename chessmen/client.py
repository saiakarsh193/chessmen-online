import socket
from typing import Optional, Tuple, List

from .engine import FEN, PIECE_COLOR
from .utils import get_env, random_hash, string_hash

IP_ADDR, PORT, BUFFER_SIZE, SERVER_HASH = get_env()
MAX_USERNAME_LEN = 20

class chessmenClient:
    def __init__(self, user_id: str = None, server_password: str = None) -> None:
        if user_id:
            self.user_id = "player_" + user_id.replace(':', '').replace('|', '').replace(' ', '_')[: MAX_USERNAME_LEN]
        else:
            self.user_id = "guest_" + random_hash(MAX_USERNAME_LEN)
        self.is_admin = False
        if server_password and string_hash(server_password) == SERVER_HASH:
            self.is_admin = True

    def kill_server(self) -> bool:
        if self.is_admin:
            status, payload = self.request("KILLSWITCH")
            print(payload)
            return True if status == "success" else False
        else:
            print("client does not have access to kill server")
            return False

    def find_match(self) -> bool:
        status, payload = self.request("FIND_MATCH")
        if status == "success":
            return True
        else:
            print(payload)
            return False

    def status_match(self) -> Optional[Tuple[str, Optional[Tuple[FEN, Tuple[str, str], PIECE_COLOR, bool]]]]:
        status, payload = self.request("STATUS_MATCH")
        if status == "success":
            payload = payload.split("|")
            if payload[0] == "in_queue":
                return payload[0], None
            else:
                fen, white_user_id, black_user_id, user_turn = payload[1: ]
                user_color = 'white' if white_user_id == self.user_id else 'black'
                users = (white_user_id, black_user_id) if user_color == 'white' else (black_user_id, white_user_id)
                return payload[0], (fen, users, user_color, bool(int(user_turn)))
        else:
            print(payload)
            return None
    
    def update_match(self, fen: FEN) -> bool:
        status, payload = self.request("UPDATE_MATCH", [fen])
        if status == "success":
            return True
        else:
            print(payload)
            return False

    def request(self, request_type: str, args: List[str] = []) -> Tuple[str, str]:
        server = socket.socket()
        try:
            server.connect((IP_ADDR, PORT)) # connect to server
            # print(f"client user ({self.user_id}) connected to server ({IP_ADDR}:{PORT})")
            args = '|'.join(args)
            server.send(f"{request_type}::{self.user_id}::{args}".encode())
            status, payload = server.recv(BUFFER_SIZE).decode().split("::")
            server.close() # disconnect from server
            # print(f"disconnected from server with status {status}")
            return status, payload
        except socket.error as e:
            print(e)
            return "error", str(e)
