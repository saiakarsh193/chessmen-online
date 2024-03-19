import socket
from typing import Optional, Tuple, List
from .utils import get_env, random_hash, string_hash

IP_ADDR, PORT, BUFFER_SIZE, SERVER_HASH = get_env()
# request_packet: uid::req / uid::req::arg1|arg2|arg3
# req -> login / find_game / 
# allocate
# status
# getfen
# setfen::rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR
# exit

class chessmenClient:
    _MAX_USER_LEN = 20

    def __init__(self, user_id: str = None, server_password: str = None) -> None:
        if user_id:
            self.user_id = "player_" + user_id.replace(':', '').replace('|', '').replace(' ', '_')[: self._MAX_USER_LEN]
        else:
            self.user_id = "guest_" + random_hash(self._MAX_USER_LEN)
        self.is_admin = False
        if server_password and string_hash(server_password) == SERVER_HASH:
            self.is_admin = True

    def login(self) -> bool:
        status, payload = self.request("login", [])
        print(payload)
        return True if status == "success" else False

    def find_game(self):
        status, payload = self.request("find_game", [])
        print(payload)
        return True if status == "success" else False

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
            print(f"client user ({self.user_id}) connected to server ({IP_ADDR}:{PORT})")
            server.send(f"{self.user_id}::{request_type}::{'|'.join(args)}".encode())
            status, payload = server.recv(BUFFER_SIZE).decode().split("::")
            server.close() # disconnect from server
            print(f"disconnected from server with status {status}")
            return status, payload
        except socket.error as e:
            print(e)
            return "error", str(e)
