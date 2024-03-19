import time
import socket
import random
from typing import Dict, List, Tuple
from .utils import get_env, string_hash

IP_ADDR, PORT, BUFFER_SIZE, SERVER_HASH = get_env()

class chessmenServer:
    REFRESH_TIME = 5 # seconds
    MAX_IDLE_TIME = 10 # seconds

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
        self.users = {}
        self.games = {}
    
    def refresh(self):
        print("running server refresh")
        idle_users = []
        queue_users = []
        for user_id, meta in self.users.items():
            # user crosses idle time
            if time.time() - meta["ping"] >= self.MAX_IDLE_TIME:
                # remove the game attached to idle user
                if meta["status"] == "in_game":
                    del self.games[meta["game_id"]]
                idle_users.append(user_id)
            # if a user's game has been removed
            elif meta["status"] == "in_game" and not meta["game_id"] in self.games:
                self.users[user_id]["status"] = "online"
                self.users[user_id]["game_id"] = None
            # handle user waiting for a game
            elif meta["status"] == "in_queue":
                queue_users.append(user_id)
        
        # remove all idle users
        for user_id in idle_users:
            del self.users[user_id]
        
        # find games for users in queue (2 at a time)
        while len(queue_users) >= 2:
            user_id1, user_id2 = random.sample(queue_users, k=2)
            queue_users.remove(user_id1)
            queue_users.remove(user_id2)
            game_id = string_hash(user_id1 + user_id2 + str(int(time.time())))
            self.users[user_id1]["status"] = "in_game"
            self.users[user_id2]["status"] = "in_game"
            self.users[user_id1]["game_id"] = game_id
            self.users[user_id2]["game_id"] = game_id
            self.games[game_id] = {
                "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR",
                "white": user_id1,
                "black": user_id2,
                "turn": "white"
            }

    def handle_request(self, user_id: str, request_type: str, args: List[str]) -> Tuple[str, str]:
        print(user_id, request_type, args)
        if user_id in self.users:
            self.users[user_id]["ping"] = time.time()
        if request_type == "login":
            if user_id in self.users:
                return "error", "user is already online"
            else:
                self.users[user_id] = {
                    "status": "online",
                    "game_id": None,
                    "ping": time.time()
                }
                return "success", "user is now online"
        elif request_type == "find_game":
            if not user_id in self.users:
                return "error", "user is not online"
            elif self.users[user_id]["status"] == "in_queue":
                return "error", "user already in queue"
            elif self.users[user_id]["status"] == "in_game":
                return "error", "user already in game"
            else:
                self.users[user_id]["status"] = "in_queue"
                return "success", "user added to queue"

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
            
            print("users:", self.users)
            print("games:", self.games)
