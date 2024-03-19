import time
import socket
import random
from typing import Dict, List, Tuple
from .utils import get_env, string_hash

IP_ADDR, PORT, BUFFER_SIZE, SERVER_HASH = get_env()

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

    def __init__(self, server_password: str) -> None:
        if string_hash(server_password) != SERVER_HASH:
            print("incorrect server password")
            exit()

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

    def login(self, user_id: str) -> bool:
        if not user_id in self.users_online:
            self.users_online.add(user_id)
            return True
        return False
    
    def find_game(self, user_id: str) -> bool:
        if user_id in self.users_online and not user_id in self.users_inqueue and not user_id in self.users_ingame:
            self.users_inqueue.add(user_id)
            return True
        return False
    
    def refresh(self):
        while len(self.users_inqueue) >= 2: # find games for users in queue
            user_id1, user_id2 = random.sample(self.users_inqueue, k=2)
            self.users_inqueue.remove(user_id1)
            self.users_inqueue.remove(user_id2)
            self.users_ingame.add(user_id1)
            self.users_ingame.add(user_id2)
            game = chessmenGame(user_id1, user_id2)
            self.games[game.game_id] = game

    def handle_request(self, user_id: str, request_type: str, args: List[str]) -> Tuple[str, str]:
        print(user_id, request_type, args)
        if request_type == "login":
            if self.login(user_id=user_id):
                return "success", "user is now online"
            else:
                return "error", "user is already online"
        elif request_type == "find_game":
            if self.find_game(user_id=user_id):
                return "success", "user is in game queue"
            else:
                return "error", "cant find user or user already in queue or game"

    def run(self):
        while True:
            (client, address) = self.skt.accept()
            print(f"client: {address}")
            
            # request: user_id::type::arg1|arg2
            user_id, request_type, args = client.recv(BUFFER_SIZE).decode().split("::")
            args = args.split("|")

            if request_type == "killserver":
                client.send("success::killing server".encode())
                client.close()
                break
            else:
                status, payload = self.handle_request(user_id, request_type, args)
                client.send(f"{status}::{payload}".encode())
                client.close()
            
            if time.time() - self.last_refresh_time >= self.REFRESH_TIME:
                self.last_refresh_time = time.time()
                self.refresh()
            
            print("users_online:", self.users_online)
            print("users_inqueue:", self.users_inqueue)
            print("users_ingame", self.users_ingame)
            print("games:")
            print([self.games[game_id] for game_id in self.games])
