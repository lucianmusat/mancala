import os
import logging

from copy import deepcopy
import board
from player import IPlayer

logging.basicConfig(level=os.environ.get("LOGLEVEL", "WARNING"))


class MiniMaxPlayer(IPlayer):
    """
    Implementation of the Player class for a player that chooses
    the pits using the minimax algorithm with alpha-beta pruning.
    """

    def __init__(self, index: int, game_board: board.Board):
        self.index = index
        self.board = game_board
        self.selected_pit = None
        logging.info(f"Minimax player {index} created")

    def move(self) -> int:
        logging.info("Minimax player making a move")
        return self.board.move(self.index, self.best_move())

    def best_move(self):
        """
        Find the best move for the current player.
        Look at every available move and calculate the score for each one.
        Choose the move with the highest score.
        """
        alpha = -1000
        beta = 1000
        best_value = -1000
        best_move = None
        for pit in self.board.valid_pit_indexes(self.index):
            new_board = deepcopy(self.board)
            new_board.move(self.index, pit)
            value = self.minimax(self.index, 1 - self.index, new_board, depth=2, maximizing=False, alpha=alpha, beta=beta)
            logging.info(f"Analyzing pit {pit} with value {value}")
            if value > best_value:
                best_value = value
                best_move = pit
            alpha = max(alpha, best_value)
        logging.info(f"Best move is {best_move} with value {best_value}")
        return best_move

    def minimax(self, player_index, current_player_index, current_board, depth, maximizing, alpha, beta):
        """
        Calculate a score for this possible move using the minimax algorithm with alpha-beta pruning.
        Basically you go through every possible combination and then switch and chose
        the best one your opponent would choose. Depending on the depth you go down
        and chose best or worst move until you either reach max depth or a game over.
        AB Pruning is an optimization that stops analyzing a move when at least one possibility has been found that
        proves the move to be worse than a previously examined move.
        :param player_index: The index of the player for which to calculate the score.
        :param current_player_index: The index of the player that is currently moving.
        :param current_board: The board to calculate the score for.
        :param depth: The depth to go down.
        :param maximizing: Whether to maximize or minimize the score.
        :param alpha: The best score that the maximizing player can guarantee at this point or later.
        :param beta: The best score that the minimizing player can guarantee at this point or later.
        """
        if depth == 0 or current_board.game_over():
            return current_board.evaluate(player_index)

        if maximizing:
            best_value = -1000
            for pit in current_board.valid_pit_indexes(current_player_index):
                new_board = deepcopy(current_board)
                new_board.move(current_player_index, pit)
                value = self.minimax(player_index, 1 - current_player_index, new_board, depth - 1, False, alpha, beta)
                best_value = max(best_value, value)
                logging.debug(f"Analyzing pit {pit} with value {value}")
                alpha = max(alpha, best_value)
                if alpha >= beta:
                    break
            logging.debug(f"Best value for player {player_index} is {best_value}")
            return best_value
        else:
            best_value = 1000
            for pit in current_board.valid_pit_indexes(current_player_index):
                new_board = deepcopy(current_board)
                new_board.move(current_player_index, pit)
                value = self.minimax(player_index, 1 - current_player_index, new_board, depth - 1, True, alpha, beta)
                best_value = min(best_value, value)
                logging.debug(f"Analyzing pit {pit} with value {value}")
                beta = min(beta, best_value)
                if alpha >= beta:
                    break
            logging.debug(f"Best value for player {player_index} is {best_value}")
            return best_value
