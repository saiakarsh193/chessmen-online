import argparse
from chessmen import chessmenServer, chessmenClient
from chessmen.utils import get_env, update_env, string_hash

SERVER_HASH = get_env(return_json=True)["server_password"]

parser = argparse.ArgumentParser(description="chessmen server backend interface")
parser.add_argument("action", help="server action to be taken", type=str, choices=["start", "kill", "update_pass"])
parser.add_argument("password", help="server admin password", type=str)
args = parser.parse_args()

if SERVER_HASH == string_hash(args.password):
    if args.action == "start":
        server = chessmenServer()
        server.run()
    elif args.action == "kill":
        chessmenClient("killserver").ping('')
    else:
        new_password = input("Enter new password: ")
        envs = get_env(return_json=True)
        envs["server_password"] = string_hash(new_password)
        update_env(envs)
else:
    print(f"incorrect password")
