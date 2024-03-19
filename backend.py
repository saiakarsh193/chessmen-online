import argparse
from chessmen import chessmenServer, chessmenClient
from chessmen.utils import get_env, update_env, string_hash

parser = argparse.ArgumentParser(description="chessmen server backend interface")
parser.add_argument("action", help="server action to be taken", type=str, choices=["start", "kill", "update_pass"])
parser.add_argument("password", help="server admin password", type=str)
args = parser.parse_args()

if args.action == "start":
    server = chessmenServer(server_password=args.password)
    server.run()
elif args.action == "kill":
    chessmenClient(server_password=args.password).kill_server()
elif args.action == "update_pass":
    envs = get_env(return_json=True)
    if string_hash(args.password) == envs["server_password"]:
        new_password = input("Enter new password: ")
        envs["server_password"] = string_hash(new_password)
        update_env(envs)
    else:
        print(f"incorrect password")
