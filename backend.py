import argparse
from getpass import getpass
from chessmen import chessmenServer, chessmenClient
from chessmen.utils import get_env, update_env, string_hash

parser = argparse.ArgumentParser(description="chessmen server backend interface")
parser.add_argument("action", help="server action to be taken", type=str, choices=["start", "kill", "update_pass"])
args = parser.parse_args()

passwd = getpass("enter server password: ")

if args.action == "start":
    server = chessmenServer(server_password=passwd)
    server.run()
elif args.action == "kill":
    chessmenClient(server_password=passwd).kill_server()
elif args.action == "update_pass":
    envs = get_env(return_json=True)
    if string_hash(passwd) == envs["server_password"]:
        new_passwd = getpass("enter new server password: ")
        envs["server_password"] = string_hash(passwd)
        update_env(envs)
    else:
        print(f"incorrect password")
