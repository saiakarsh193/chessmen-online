from chessmen.utils import get_env
from chessmen import chessmenClient

# print(get_env(return_json=True))
# print()

client = chessmenClient("tester")
print(client.ping("login"))
print(client.ping("find_game"))