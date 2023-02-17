from move import HumanMove
from player import Player
from board import Board
from game import Game


def main():
    board = Board()
    human_move_strategy = HumanMove(board)
    player1 = Player(1, human_move_strategy)
    player2 = Player(2, human_move_strategy)
    mancala_game = Game(player1, player2)
    winner = mancala_game.start()
    print(f"Player {winner} won!")


if __name__ == '__main__':
    main()
