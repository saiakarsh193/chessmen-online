import socket
from typing import Optional, Tuple, List, Any
from .utils import get_env, random_hash, string_hash

IP_ADDR, PORT, BUFFER_SIZE, SERVER_HASH = get_env()

class chessmenClient:
    MAX_USER_LEN = 20

    def __init__(self, user_id: str = None, server_password: str = None) -> None:
        if user_id:
            self.user_id = "player_" + user_id.replace(':', '').replace('|', '').replace(' ', '_')[: self.MAX_USER_LEN]
        else:
            self.user_id = "guest_" + random_hash(self.MAX_USER_LEN)
        self.is_admin = False
        if server_password and string_hash(server_password) == SERVER_HASH:
            self.is_admin = True

    def find_game(self) -> bool:
        status, payload = self.request("find_game", [])
        if status == "success":
            return True
        else:
            print(payload)
            return False

    def status(self) -> Optional[Tuple[str, Optional[Tuple[str, str, str]]]]:
        status, payload = self.request("status", [])
        if status == "success":
            payload = payload.split("|")
            if payload[0] == "in_queue":
                return payload[0], None
            else:
                fen, white_player, black_player, turn = payload[1: ]
                user_side = "white" if white_player == self.user_id else "black"
                return payload[0], (fen, user_side, turn)
        else:
            print(payload)
            return None
    
    def update(self, fen: str) -> bool:
        status, payload = self.request("update", [fen])
        if status == "success":
            return True
        else:
            print(payload)
            return False

    def kill_server(self) -> bool:
        if self.is_admin:
            status, payload = self.request("killserver", [])
            print(payload)
            return True if status == "success" else False
        else:
            print("client does not have access to kill server")
            return False

    def request(self, request_type: str, args: List[str]) -> Tuple[str, str]:
        server = socket.socket()
        try:
            server.connect((IP_ADDR, PORT)) # connect to server
            # print(f"client user ({self.user_id}) connected to server ({IP_ADDR}:{PORT})")
            server.send(f"{self.user_id}::{request_type}::{'|'.join(args)}".encode())
            status, payload = server.recv(BUFFER_SIZE).decode().split("::")
            server.close() # disconnect from server
            # print(f"disconnected from server with status {status}")
            return status, payload
        except socket.error as e:
            print(e)
            return "error", str(e)
