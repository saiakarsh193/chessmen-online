import socket
import random
from typing import Optional

try:
    from dev.utils import get_env # if calling from app.py
except:
    from utils import get_env # if directly running

IP_ADDR, PORT, BUFFER_SIZE = get_env()

class chessbonClient:
    def __init__(self, user_id: Optional[str] = None) -> None:
        if (user_id == None):
            user_id_prefix = "guest_"
            user_id = hex(random.getrandbits(100))[2: 22] # 20 digit hex string
        else:
            user_id_prefix = "player_"
            user_id = user_id[: 20] # max 20 char name
            user_id = user_id.replace(':', '') # and no ':', '|', ' '  in the name (special chars)
            user_id = user_id.replace('|', '')
            user_id = user_id.replace(' ', '')
        self.user_id = user_id_prefix + user_id
    
    def ping(self, request: str):
        # request: req or req::args|args
        if request == "get_user_id":
            return self.user_id
        request = f"<{self.user_id}::{request}>"
        server = socket.socket()
        try:
            server.connect((IP_ADDR, PORT)) # connect to server
            print(f"client user ({self.user_id}) connected to server ({IP_ADDR}:{PORT})")
            # <akarsh : allocate> <akarsh : status> <akarsh : getfen>
            # <akarsh : setfen : rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR> <akarsh : exit>
            server.send(request.encode())
            response = server.recv(BUFFER_SIZE).decode()
            server.close() # disconnect from server
            print('disconnected from server')
            status, response = response[1: -1].split("::")
            return response
        except socket.error as e:
            print(str(e))
            return None

if __name__ == '__main__':
    client = chessbonClient("tester")
    # client = chessbonClient("killserver")
    print(client.ping("login"))
    print(client.ping("find_match"))
