import socket
from typing import Optional
from .utils import get_env, random_hash

IP_ADDR, PORT, BUFFER_SIZE = get_env()
# request_packet: uid::req / uid::req::arg1|arg2|arg3
# req -> login / find_game / 
# allocate
# status
# getfen
# setfen::rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR
# exit

class chessmenClient:
    def __init__(self, user_id: Optional[str] = None) -> None:
        if (user_id == None):
            user_id_prefix = "guest_"
            user_id = random_hash(20)
        else:
            user_id_prefix = "player_"
            # :, | are special chars
            user_id = user_id.replace(':', '')
            user_id = user_id.replace('|', '')
            user_id = user_id.replace(' ', '_')
            user_id = user_id[: 20] # max 20 char name
        self.user_id = user_id_prefix + user_id
    
    def ping(self, request: str) -> Optional[str]:
        request_packet = f"{self.user_id}::{request}"
        server = socket.socket()
        try:
            server.connect((IP_ADDR, PORT)) # connect to server
            print(f"client user ({self.user_id}) connected to server ({IP_ADDR}:{PORT})")
            server.send(request_packet.encode())
            status, data = server.recv(BUFFER_SIZE).decode().split("::")
            server.close() # disconnect from server
            print(f"disconnected from server with status {status}")
            return data
        except socket.error as e:
            print(e)
            return None
