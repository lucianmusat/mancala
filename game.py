from player import Player

import os


class Game:
    def __init__(self, player1: Player, player2: Player):
        self.player1 = player1
        self.player2 = player2
        assert self.player1.id != self.player2.id, f"Cannot have two player{self.player1.id}!"

    def render_board(self):
        os.system('clear')
        print(f"[{self.player2.big_pit:02}]  [{self.player2.pits[5]:02}][{self.player2.pits[4]:02}]"
              f"[{self.player2.pits[3]:02}][{self.player2.pits[2]:02}][{self.player2.pits[1]:02}]"
              f"[{self.player2.pits[0]:02}]")
        print(f"      [{self.player1.pits[0]:02}][{self.player1.pits[1]:02}]"
              f"[{self.player1.pits[2]:02}][{self.player1.pits[3]:02}][{self.player1.pits[4]:02}]"
              f"[{self.player1.pits[5]:02}]  [{self.player1.big_pit:02}]")

    def check_win(self):
        if all(e == 0 for e in self.player1.pits) or all(e == 0 for e in self.player2.pits):
            return 1 if self.player1.big_pit > self.player2.big_pit else 2
        return None

    def start(self):
        winner = None
        turn = 0
        self.render_board()
        while not winner:
            if turn % 2 == 0:
                if not self.player1.move(self.player2):
                    continue
            else:
                if not self.player2.move(self.player1):
                    continue
            turn += 1
            winner = self.check_win()
            self.render_board()
        return winner
