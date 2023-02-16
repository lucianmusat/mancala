from player import HumanPlayer
from game import Game


def main():
    player1 = HumanPlayer(1)
    player2 = HumanPlayer(2)
    mancala_game = Game(player1, player2)
    winner = mancala_game.start()
    print(f"Player {winner} won!")


if __name__ == '__main__':
    main()
