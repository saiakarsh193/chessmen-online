import time
import socket
import random
from typing import Dict, List, Tuple
from .utils import get_env, string_hash

IP_ADDR, PORT, BUFFER_SIZE, SERVER_HASH = get_env()

class chessmenServer:
    REFRESH_TIME = 3 # seconds
    MAX_IDLE_TIME = 30 # seconds

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
        remove_games = []
        remove_users = []
        queue_users = []
        for user_id, meta in self.users.items():
            if time.time() - meta["ping"] >= self.MAX_IDLE_TIME: # user crosses idle time
                if meta["status"] == "in_game": # remove game, and both users
                    user_id1, user_id2 = self.games[meta["game_id"]]["white"], self.games[meta["game_id"]]["black"]
                    remove_games.append(meta["game_id"])
                    remove_users.append(user_id1)
                    remove_users.append(user_id2)
                else:
                    remove_users.append(user_id)
            elif meta["status"] == "in_queue": # add user to queue
                queue_users.append(user_id)
        
        # remove games
        for game_id in remove_games:
            del self.games[game_id]

        # remove users
        for user_id in remove_users:
            del self.users[user_id]
        
        # create games
        while len(queue_users) >= 2: # 2 users at a time
            user_id1, user_id2 = random.sample(queue_users, k=2)
            queue_users.remove(user_id1)
            queue_users.remove(user_id2)
            self.users[user_id1]["status"] = "in_game"
            self.users[user_id2]["status"] = "in_game"
            game_id = string_hash(user_id1 + user_id2 + str(int(time.time())))
            self.users[user_id1]["game_id"] = game_id
            self.users[user_id2]["game_id"] = game_id
            self.games[game_id] = {
                "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR",
                "white": user_id1,
                "black": user_id2,
                "turn": "white"
            }
        
        print("\n" + "="*30)
        print("server refresh done")
        print("users:")
        for user_id, meta in self.users.items():
            print(f"\t{user_id} : {meta['status']} | {meta['game_id']} | {int(time.time() - meta['ping'])}")
        print("games:")
        for game_id, meta in self.games.items():
            print(f"\t{game_id} : {meta['fen']} | {meta['white']} | {meta['black']} | {meta['turn']}")
        print("="*30 + "\n")

    def handle_request(self, user_id: str, request_type: str, args: List[str]) -> Tuple[str, str]:
        if user_id in self.users:
            self.users[user_id]["ping"] = time.time()
        if request_type == "find_game":
            if user_id in self.users:
                if self.users[user_id]["status"] == "in_queue":
                    return "error", "user is already in queue"
                elif self.users[user_id]["status"] == "in_game":
                    return "error", "user is already in game"
            else:
                self.users[user_id] = {
                    "status": "in_queue",
                    "game_id": None,
                    "ping": time.time()
                }
                return "success", "user added to queue"
        elif request_type == "status":
            if user_id in self.users:
                if self.users[user_id]["status"] == "in_queue":
                    return "success", "in_queue"
                elif self.users[user_id]["status"] == "in_game":
                    game = self.games[self.users[user_id]["game_id"]]
                    return "success", "in_game" + "|" + game["fen"] + "|" + game["white"] + "|" + game["black"] + "|" + game["turn"]
            else:
                return "error", "user is not online"
        elif request_type == "update":
            if user_id in self.users:
                if self.users[user_id]["status"] == "in_queue":
                    return "error", "user not in game"
                elif self.users[user_id]["status"] == "in_game":
                    game_id = self.users[user_id]["game_id"]
                    user_color = "white" if self.games[game_id]["white"] == user_id else "black"
                    if user_color == self.games[game_id]["turn"]:
                        self.games[game_id]["fen"] = args[0]
                        self.games[game_id]["turn"] = "black" if self.games[game_id]["turn"] == "white" else "white"
                        return "success", "fen has been updated"
                    else:
                        return "error", "not user turn yet"
            else:
                return "error", "user is not online"

    def run(self):
        while True:
            (client, address) = self.skt.accept()            
            user_id, request_type, args = client.recv(BUFFER_SIZE).decode().split("::")
            args = args.split("|")
            print(f"client: {address} -> {user_id} : {request_type}")

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
