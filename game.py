from board import Board

import os


class Game:
    def __init__(self, board: Board):
        self.board = board

    def render_board(self):
        os.system('clear')
        print(f"[{self.board.player2.big_pit:02}]  [{self.board.player2.pits[5]:02}][{self.board.player2.pits[4]:02}]"
              f"[{self.board.player2.pits[3]:02}][{self.board.player2.pits[2]:02}][{self.board.player2.pits[1]:02}]"
              f"[{self.board.player2.pits[0]:02}]")
        print(f"      [{self.board.player1.pits[0]:02}][{self.board.player1.pits[1]:02}]"
              f"[{self.board.player1.pits[2]:02}][{self.board.player1.pits[3]:02}][{self.board.player1.pits[4]:02}]"
              f"[{self.board.player1.pits[5]:02}]  [{self.board.player1.big_pit:02}]")

    def check_win(self):
        if all(e == 0 for e in self.board.player1.pits) or all(e == 0 for e in self.board.player2.pits):
            return 1 if self.board.player1.big_pit > self.board.player2.big_pit else 2
        return None

    def legal_move(self, player_id: int, pit: int):
        if pit not in range(0, 6):
            input(f"Illegal move, {pit} must be in range 1..6!")
            return False
        if (player_id == 1 and self.board.player1.pits[pit] == 0) or \
                (player_id == 2 and self.board.player2.pits[pit] == 0):
            input(f"The pit {pit} does not contain any stones!")
            return False
        return True

    def start(self):
        winner = None
        turn = 0
        self.render_board()
        while not winner:
            if turn % 2 == 0:
                pit = int(input("Player 1 move [1-6]: ")) - 1
                if not self.legal_move(1, pit):
                    continue
                self.board.move(1, pit)
            else:
                pit = int(input("Player 2 move [1-6]: ")) - 1
                if not self.legal_move(2, pit):
                    continue
                self.board.move(2, pit)
            turn += 1
            winner = self.check_win()
            self.render_board()
        return winner
