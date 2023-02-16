from board import Board
from player import Player
from game import Game


def main():
    player1 = Player(1)
    player2 = Player(2)
    board = Board(player1, player2)
    mancala_game = Game(board)
    winner = mancala_game.start()
    print(f"Player {winner} won!")


if __name__ == '__main__':
    main()
