from chessmen.utils import get_env
from chessmen import chessmenClient
from chessmen.engine import ChessmenBoard

# print(get_env(return_json=True))
# print()

# client = chessmenClient("tester")
# print(client.ping("login"))
# print(client.ping("find_game"))

cb = ChessmenBoard()
cb.run_offline_multiplayer()
