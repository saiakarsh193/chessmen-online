import socket
import argparse

from utils import get_env, string_hash, chessbonMatch

IP_ADDR, PORT, BUFFER_SIZE = get_env()

class chessbonServer:
    def __init__(self, admin: str) -> None:
        assert self._login_admin(admin=admin), f"admin login failed using: {admin}"
        self._setup_socket()

        self.users_online = set()
        self.users_searching = set()
        self.users_ingame = set()
        self.matches = {}

    def _login_admin(self, admin: str) -> bool:
        self.admin_hash = get_env(return_json=True)["server_admin_hash"]
        return bool(self.admin_hash == string_hash(admin))
    
    def _setup_socket(self):
        self.skt = socket.socket()
        self.skt.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.skt.bind((IP_ADDR, PORT))
        print(f"server binded to {IP_ADDR}:{PORT}")
        self.skt.listen(5)
    
    def _login_user(self, user_id: str) -> bool:
        if not user_id in self.users_online:
            self.users_online.add(user_id)
            return True
        else:
            return False
    
    def _find_match_user(self, user_id: str) -> bool:
        if not user_id in self.users_searching and not user_id in self.users_ingame:
            self.users_searching.add(user_id)
            return True
        else:
            return False
    
    def _create_match(self, user_id_1: str, user_id_2: str) -> None:
        new_match = chessbonMatch(user_id_1, user_id_2)
        self.matches[new_match.match_id] = new_match

    def _maintain_server(self):
        # find matchs for users searching
        list_users_searching = list(self.users_searching)
        for ind in range(0, len(list_users_searching), 2):
            if ind + 1 < len(list_users_searching):
                user_id_1 = list_users_searching[ind]
                user_id_2 = list_users_searching[ind + 1]
                self.users_searching.remove(user_id_1)
                self.users_searching.remove(user_id_2)
                self.users_ingame.add(user_id_1)
                self.users_ingame.add(user_id_2)
                self._create_match(user_id_1, user_id_2)

    def run(self):
        while True:
            (client, address) = self.skt.accept()
            print(address)
            request = client.recv(BUFFER_SIZE).decode() # <user_id::type::args|args>
            request = request[1: -1].split("::")
            if len(request) == 2:
                user_id, request_type = request
                args = []
            else:
                user_id, request_type, args = request
                args = args.split("|")
            print(user_id, request_type, args)
            if user_id == "player_killserver":
                client.send("<ack::server loop stopping>".encode())
                client.close()
                break
            if request_type == "login":
                if self._login_user(user_id=user_id):
                    client.send("<ack::user login successful>".encode())
                else:
                    client.send("<err::user already logged in>".encode())
            elif request_type == "find_match":
                if self._find_match_user(user_id=user_id):
                    client.send("<ack::finding a match for user>".encode())
                else:
                    client.send("<err::user already in waiting list or match>".encode())
            client.close()
            self._maintain_server()
            print("users_online")
            print(self.users_online)
            print("users_searching")
            print(self.users_searching)
            print("users_ingame")
            print(self.users_ingame)
            print("matches")
            print(self.matches)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="server side for CHESSBON")
    parser.add_argument("admin", help="CHESSBON server admin name", type=str)
    args = parser.parse_args()
    server = chessbonServer(args.admin)
    server.run()
