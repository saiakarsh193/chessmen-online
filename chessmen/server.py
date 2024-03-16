import time
import socket
import random
from typing import Dict
from .utils import get_env, string_hash

IP_ADDR, PORT, BUFFER_SIZE = get_env()

class chessmenGame:
    def __init__(self, user_id1: str, user_id2: str) -> None:
        self.game_id = string_hash(user_id1 + user_id1)
        self.users = (user_id1, user_id2) # White, Black
        self.current_user = 0 # 0: W, 1: B
        self.fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR'
    
    def update(self, user_id: str, fen: str) -> bool:
        if user_id == self.users[self.current_user]:
            self.current_user = (1 + self.current_user) % 2
            self.fen = fen
            return True
        return False
    
    def __str__(self) -> str:
        return f"{self.match_id}|{self.users}|{self.current_user}|{self.fen}"

class chessmenServer:
    REFRESH_TIME = 5 # seconds

    def __init__(self) -> None:
        self.skt = socket.socket()
        self.skt.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.skt.bind((IP_ADDR, PORT))
        print(f"server started at {IP_ADDR}:{PORT}")
        self.skt.listen(5)

        self.last_refresh_time = time.time()
        self.users_online = set()
        self.users_inqueue = set()
        self.users_ingame = set()
        self.games: Dict[str, chessmenGame] = {}

    def _login_user(self, user_id: str) -> bool:
        if not user_id in self.users_online:
            self.users_online.add(user_id)
            return True
        return False
    
    def _find_game_for_user(self, user_id: str) -> bool:
        if user_id in self.users_online and not user_id in self.users_inqueue and not user_id in self.users_ingame:
            self.users_inqueue.add(user_id)
            return True
        return False
    
    def _refresh(self):
        # find matchs for users searching
        while len(self.users_inqueue) >= 2:
            user_id1, user_id2 = random.sample(self.users_inqueue, k=2)
            self.users_inqueue.remove(user_id1)
            self.users_inqueue.remove(user_id2)
            self.users_ingame.add(user_id1)
            self.users_ingame.add(user_id2)
            game = chessmenGame(user_id1, user_id2)
            self.games[game.game_id] = game

    def run(self):
        while True:
            (client, address) = self.skt.accept()
            print(f"client: {address}")
            # request: user_id::type::arg1|arg2
            request = client.recv(BUFFER_SIZE).decode().split("::")
            if len(request) == 2:
                user_id, request_type = request
                args = []
            else:
                user_id, request_type, args = request
                args = args.split("|")
            print(user_id, request_type, args)
            
            if user_id == "player_killserver":
                client.send("ack::server loop stopping".encode())
                client.close()
                break
            
            if request_type == "login":
                if self._login_user(user_id=user_id):
                    client.send("ack::user login successful".encode())
                else:
                    client.send("err::user already logged in".encode())
            elif request_type == "find_game":
                if self._find_game_for_user(user_id=user_id):
                    client.send("ack::finding game".encode())
                else:
                    client.send("err::user offline, or in queue or in match".encode())
            
            client.close()
            if time.time() - self.last_refresh_time >= self.REFRESH_TIME:
                self.last_refresh_time = time.time()
                self._refresh()
            print("users_online")
            print(self.users_online)
            print("users_inqueue")
            print(self.users_inqueue)
            print("users_ingame")
            print(self.users_ingame)
            print("games")
            print([self.games[game_id] for game_id in self.games])
