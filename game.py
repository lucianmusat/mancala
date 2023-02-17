import os

from player import Player
from utils import MoveResult


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

    def check_win(self) -> int:
        assert self.player1.big_pit + self.player2.big_pit + sum(self.player1.pits) + sum(self.player2.pits) == 72, \
            f"There was a problem in the stone moves!"
        if all(stones == 0 for stones in self.player1.pits):
            self.player2.collect_all_stones()
            return 1 if self.player1.big_pit > self.player2.big_pit else 2
        if all(stones == 0 for stones in self.player2.pits):
            self.player1.collect_all_stones()
            return 1 if self.player1.big_pit > self.player2.big_pit else 2
        return 0

    def start(self):
        winner = None
        turn = 0
        while not winner:
            self.render_board()
            if turn % 2 == 0:
                if self.player1.move() != MoveResult.Valid:
                    continue
            else:
                if self.player2.move() != MoveResult.Valid:
                    continue
            turn += 1
            winner = self.check_win()
            self.render_board()
        return winner
