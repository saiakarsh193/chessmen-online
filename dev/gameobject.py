import random

class gameObject:
    def __init__(self, uid1, uid2):
        self.player1 = uid1
        self.player2 = uid2
        if(random.random() > 0.5):
            self.white = self.player1
            self.black = self.player2
        else:
            self.white = self.player2
            self.black = self.player1
        self.fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR'
        self.turn = self.white
        self.status = 0 # 0: running, -1: one left, -2: both left and remove game

    def color(self, uid):
        if(uid == self.white):
            return 'white'
        elif(uid == self.black):
            return 'black'
        else:
            return None

    def update(self, fen):
        self.fen = fen
        if(self.turn == self.white):
            self.turn = self.black
        else:
            self.turn = self.white
    
    def __str__(self):
        return 'player1 ' + self.player1 + '\nplayer2 ' + self.player2 + '\nwhite ' + self.white + '\nblack ' + self.black + '\nfen ' + self.fen + '\nturn ' + self.turn + '\nstatus ' + str(self.status)
