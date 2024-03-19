from chessmen import chessmenClient, chessmenBoard

class chessmenCLI:
    def __init__(self, name: str):
        self.client = chessmenClient(user_id=name)
        # self.board = chessmenBoard()
        self.client.login()
        self.client.find_game()
    
    def run(self):
        ...

cli = chessmenCLI("akarsh")

# client = chessmenClient(user_id="akarsh")
# client.login()
# client.find_game()

# client = chessmenClient(user_id="ankitha")
# client.login()
# client.find_game()