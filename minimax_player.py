# import os
# import logging
#
# from copy import deepcopy
# from player import IPlayer, NUMBER_OF_PITS, HAVE_TO_STEAL
#
# logging.basicConfig(level=os.environ.get("LOGLEVEL", "WARNING"))
#
#
# class MiniMaxPlayer(IPlayer):
#     """
#     Implementation of the Player class for a player that chooses
#     the pits at random, with no strategy.
#     """
#
#     def move(self) -> (int, int):
#         print("Hard AI player thinking of a move")
#         move_values = [float('-inf')] * NUMBER_OF_PITS
#         backup_pits = deepcopy(self.pits)
#         backup_big_pit = deepcopy(self.big_pit)
#         opponent_backup_pits = deepcopy(self.opponent.pits)
#         opponent_backup_big_pit = deepcopy(self.opponent.big_pit)
#         for pit_index, _ in enumerate(self.pits):
#             if self.pits[pit_index] > 0:
#                 index_score = self.minimax(pit_index, self, self.opponent, depth=1, maximizing=True)
#                 move_values[pit_index] = index_score
#         print(f"Move values: {move_values}")
#         self.pits = backup_pits
#         self.big_pit = backup_big_pit
#         self.opponent.pits = opponent_backup_pits
#         self.opponent.big_pit = opponent_backup_big_pit
#         chosen_move = move_values.index(max(move_values))
#         print(f"Hard AI player chose the index: {chosen_move}")
#         return self.move_from(chosen_move)


#     self.big_pit = 0
#     self.pits = [STARTING_STONES] * NUMBER_OF_PITS
#     self.selected_pit = None
#     self.opponent = None

# def all_selectable_pits(self):
#     """
#     Return a list of all the pits that have stones in them, and so they can be selected.
#     """
#     return [valid_index for valid_index, pit in enumerate(self.pits) if pit > 0]
#
# def is_terminal(self):
#     """
#     Check if the game is over.
#     """
#     return len(self.all_selectable_pits()) == 0
#
# def print_current_board_state(self):
#     print(f"Player {self} has {self.big_pit} {self.pits} and opponent has {self.opponent.big_pit} {self.opponent.pits}")

# # Calculate a score for this possible move using the minimax algorithm
# def minimax(self, move, player, opponent, depth, maximizing):
#     self.print_current_board_state()
#     # TODO: Implement a Board class to backup and restore these values easier
#     if self.is_terminal() or depth == 0:
#         return player.evaluate()
#
#     if maximizing:
#         print(f"Maximize for player {player}")
#         current_player = deepcopy(player)
#         current_opponent = deepcopy(opponent)
#         best_score = float('-inf')
#         remaining_stones, current_pit = player.move_from(move)
#         while remaining_stones != 0:
#             logging.info(f"Remaining stones: {remaining_stones} current pit: {current_pit}")
#             if remaining_stones == HAVE_TO_STEAL:
#                 player.steal_from(current_pit)
#                 remaining_stones = 0
#             elif current_pit == NUMBER_OF_PITS - 1 and remaining_stones > 0:
#                 current_pit, remaining_stones = self.move_outside_of_own_pits(current_pit, remaining_stones, player, opponent)
#             else:
#                 logging.info(f"Adding more to own pits")
#                 remaining_stones = player.add_stones(remaining_stones)
#
#         for next_move in player.all_selectable_pits():
#             score = self.minimax(next_move, player, opponent, depth-1, False)
#             best_score = max(best_score, score)
#         self.pits = current_player.pits
#         self.big_pit = current_player.big_pit
#         opponent.pits = current_opponent.pits
#         opponent.big_pit = current_opponent.big_pit
#         return best_score
#     else:
#         print(f"Minimize for player {player}")
#         current_player = deepcopy(player)
#         current_opponent = deepcopy(opponent)
#         best_score = float('inf')
#         remaining_stones, current_pit = player.move_from(move)
#         while remaining_stones != 0:
#             logging.info(f"Remaining stones: {remaining_stones} current pit: {current_pit}")
#             if remaining_stones == HAVE_TO_STEAL:
#                 player.steal_from(current_pit)
#                 remaining_stones = 0
#             elif current_pit == NUMBER_OF_PITS - 1 and remaining_stones > 0:
#                 current_pit, remaining_stones = self.move_outside_of_own_pits(current_pit, remaining_stones, player,
#                                                                               opponent)
#             else:
#                 logging.info(f"Adding more to own pits")
#                 remaining_stones = player.add_stones(remaining_stones)
#
#         for next_move in opponent.all_selectable_pits():
#             score = self.minimax(next_move, opponent, player, depth-1, True)
#             best_score = min(best_score, score)
#         self.pits = current_player.pits
#         self.big_pit = current_player.big_pit
#         opponent.pits = current_opponent.pits
#         opponent.big_pit = current_opponent.big_pit
#         return best_score

# Temporary, move this crap out
# @staticmethod
# def move_outside_of_own_pits(current_pit, remaining_stones, player, opponent):
#     logging.info(f"Adding to big pit")
#     player.big_pit += 1
#     remaining_stones -= 1
#     if remaining_stones > 0:
#         logging.info(f"Adding to other player's pits")
#         remaining_stones = opponent.add_stones(remaining_stones)
#         # Don't steal stones if we're landing on empty on the other player's pits
#         if remaining_stones == HAVE_TO_STEAL:
#             remaining_stones = 0
#         current_pit = 0
#     return current_pit, remaining_stones

# Here we need to evaluate the state of the board and make a
# judgement of how good it is for the player
# def evaluate(self):
#     # return (self.big_pit + sum(self.pits)) - (self.opponent.big_pit + sum(self.opponent.pits))
#     # simple algorithm, who has more points in the end
#     # print(f"Evaluate time, player has {self.big_pit} {self.pits} and opponent has {self.opponent.big_pit} {self.opponent.pits}")
#     return self.big_pit - self.opponent.big_pit