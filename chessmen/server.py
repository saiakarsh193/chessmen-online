import time
import socket
import random
from datetime import datetime
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional, Literal

from .engine import FEN, START_FEN
from .utils import get_env, string_hash

IP_ADDR, PORT, BUFFER_SIZE, SERVER_HASH = get_env()
SERVER_MIN_REFRESH_TIME = 3 # seconds
USER_MAX_IDLE_TIME = 30 # seconds
USER_STATUS = Literal['in_queue', 'in_match']

@dataclass
class chessmenUser:
    user_id: str
    status: USER_STATUS = 'in_queue'
    match_id: Optional[str] = None
    last_ping: float = time.time()

    def refresh_ping(self) -> None:
        self.last_ping = time.time()

    def time_since_last_ping(self) -> float:
        return time.time() - self.last_ping

@dataclass
class chessmenMatch:
    match_id: str
    white_user_id: str
    black_user_id: str
    fen: FEN = START_FEN

    def check_valid_turn(self, user_id: str) -> bool:
        user_color = 'w' if user_id == self.white_user_id else 'b'
        return self.fen.split()[1] == user_color

    @staticmethod
    def create_match(user_id_1: str, user_id_2: str) -> 'chessmenMatch':
        match_id = string_hash(user_id_1 + user_id_2 + str(time.time()))
        return chessmenMatch(
            match_id=match_id,
            white_user_id=user_id_1,
            black_user_id=user_id_2
        )

class chessmenServer:
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
        self.users: Dict[str, chessmenUser] = {}
        self.matches: Dict[str, chessmenMatch] = {}
    
    def refresh(self):
        matches_to_remove = []
        users_to_remove = []
        users_in_queue = []
        for user_id, user in self.users.items():
            if user.time_since_last_ping() >= USER_MAX_IDLE_TIME: # user crosses idle time
                if user.status == "in_match" and not user in users_to_remove: # remove match, and both users (if already not added)
                    match = self.matches[user.match_id]
                    users_to_remove.append(match.white_user_id)
                    users_to_remove.append(match.black_user_id)
                    matches_to_remove.append(match.match_id)
                else:
                    users_to_remove.append(user_id)
            elif user.status == "in_queue": # add user to queue
                users_in_queue.append(user_id)
        
        # remove matches
        for match_id in matches_to_remove:
            del self.matches[match_id]

        # remove users
        for user_id in users_to_remove:
            del self.users[user_id]
        
        # create matches
        while len(users_in_queue) >= 2: # 2 users at a time
            user_id_1, user_id_2 = random.sample(users_in_queue, k=2)
            match = chessmenMatch.create_match(user_id_1, user_id_2)
            self.users[user_id_1].status = 'in_match'
            self.users[user_id_1].match_id = match.match_id
            users_in_queue.remove(user_id_1)
            self.users[user_id_2].status = 'in_match'
            self.users[user_id_2].match_id = match.match_id
            users_in_queue.remove(user_id_2)
            self.matches[match.match_id] = match
        
        print("\n" + "="*30)
        print("SERVER REFRESH")
        print(f"USERS: ({len(self.users)})")
        for user_id, user in self.users.items():
            print(f"\t{user_id} : {user} - {user.time_since_last_ping():.2f}")
        print(f"MATCHES: ({len(self.matches)})")
        for match_id, match in self.matches.items():
            print(f"\t{match_id} : {match}")
        print("="*30 + "\n")

    def handle_request(self, request_type: str, user_id: str, args: List[str]) -> Tuple[str, str]:
        if user_id in self.users:
            self.users[user_id].refresh_ping()
        if request_type == "FIND_MATCH":
            if user_id in self.users:
                if self.users[user_id].status == "in_queue":
                    return "error", "user is already in queue"
                elif self.users[user_id].status == "in_match":
                    return "error", "user is already in match"
            else:
                self.users[user_id] = chessmenUser(user_id)
                return "success", "user added to match queue"
        elif request_type == "STATUS_MATCH":
            if user_id in self.users:
                if self.users[user_id].status == "in_queue":
                    return "success", "in_queue"
                elif self.users[user_id].status == "in_match":
                    match_id = self.users[user_id].match_id
                    match = self.matches[match_id]
                    return_args = ['in_match', match.fen, match.white_user_id, match.black_user_id, str(int(match.check_valid_turn(user_id)))]
                    return "success", '|'.join(return_args)
            else:
                return "error", "user is not online"
        elif request_type == "UPDATE_MATCH":
            if user_id in self.users:
                if self.users[user_id].status == "in_queue":
                    return "error", "user not in match"
                elif self.users[user_id].status == "in_match":
                    match_id = self.users[user_id].match_id
                    match = self.matches[match_id]
                    if match.check_valid_turn(user_id):
                        match.fen = args[0]
                        return "success", "fen has been updated"
                    else:
                        return "error", "not user turn yet"
            else:
                return "error", "user is not online"

    def run(self):
        while True:
            (client, address) = self.skt.accept()            
            request_type, user_id, args = client.recv(BUFFER_SIZE).decode().split("::")
            date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            args = args.split('|') if args else []
            print(f"{request_type} [{date}] {user_id} ({address})")

            # refresh the server before processing request
            if time.time() - self.last_refresh_time >= SERVER_MIN_REFRESH_TIME:
                self.last_refresh_time = time.time()
                self.refresh()

            # special kill command to stop server remotely
            if request_type == "KILLSWITCH":
                client.send("success::killing server".encode())
                client.close()
                break
            # handling client requests
            else:
                status, payload = self.handle_request(request_type, user_id, args)
                client.send(f"{status}::{payload}".encode())
                client.close()
