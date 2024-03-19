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