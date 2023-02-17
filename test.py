import unittest

from game import Game
from utils import MoveResult
from player import Player
from board import Board
from move import HumanMove


class TestGame(unittest.TestCase):

    def test_player_id(self):
        board = Board()
        strategy = HumanMove(board)
        player1 = Player(1, strategy)
        player2 = Player(2, strategy)
        Game(player1, player2)

    def test_player_same_id(self):
        with self.assertRaises(AssertionError) as context:
            board = Board()
            strategy = HumanMove(board)
            player1 = Player(1, strategy)
            player2 = Player(1, strategy)
            Game(player1, player2)
        self.assertTrue("Cannot have two player" in str(context.exception))

    def test_player_invalid_id(self):
        with self.assertRaises(AssertionError) as context:
            board = Board()
            strategy = HumanMove(board)
            player1 = Player(1, strategy)
            player2 = Player(3, strategy)
            Game(player1, player2)
        self.assertTrue("Must be either player 1 or 2" in str(context.exception))

    def test_player_basic_move(self):
        board = Board()
        strategy = HumanMove(board)
        player1 = Player(1, strategy)
        player2 = Player(2, strategy)
        self.assertEqual(strategy.move_pit(player1.id, 0), MoveResult.InOwnBigPit)
        self.assertEqual(player1.pits, [0, 7, 7, 7, 7, 7])
        self.assertEqual(player1.big_pit, 1)
        self.assertEqual(player2.pits, [6, 6, 6, 6, 6, 6])
        self.assertEqual(player2.big_pit, 0)

    def test_player_move_empty_pit(self):
        board = Board()
        strategy = HumanMove(board)
        player1 = Player(1, strategy)
        player2 = Player(2, strategy)
        board.player_one_pits = [0, 7, 7, 7, 7, 7]
        board.player_one_big_pit = 1
        board.player_two_pits = [6, 6, 6, 6, 6, 6]
        board.player_two_big_pit = 0
        with self.assertRaises(AssertionError) as context:
            strategy.move_pit(player1.id, 0)
        self.assertTrue("No stones to pick" in str(context.exception))

    def test_player_move_twice(self):
        board = Board()
        strategy = HumanMove(board)
        player1 = Player(1, strategy)
        player2 = Player(2, strategy)
        board.player_one_pits = [0, 7, 7, 7, 7, 7]
        board.player_one_big_pit = 1
        board.player_two_pits = [6, 6, 6, 6, 6, 6]
        board.player_two_big_pit = 0
        self.assertEqual(strategy.move_pit(player1.id, 1), MoveResult.Valid)
        self.assertEqual(board.player_one_pits, [0, 0, 8, 8, 8, 8])
        self.assertEqual(player1.big_pit, 2)
        self.assertEqual(player2.pits, [7, 7, 6, 6, 6, 6])
        self.assertEqual(player2.big_pit, 0)

    def test_player_land_on_empty(self):
        board = Board()
        strategy = HumanMove(board)
        player1 = Player(1, strategy)
        player2 = Player(2, strategy)
        board.player_one_pits = [1, 0, 8, 8, 8, 8]
        board.player_one_big_pit = 2
        board.player_two_pits = [0, 8, 7, 7, 7, 7]
        board.player_two_big_pit = 1
        self.assertEqual(strategy.move_pit(player1.id, 0), MoveResult.Valid)
        self.assertEqual(player1.pits, [0, 0, 8, 8, 8, 8])
        self.assertEqual(player1.big_pit, 10)
        self.assertEqual(player2.pits, [0, 8, 7, 7, 0, 7])
        self.assertEqual(player2.big_pit, 1)

    def test_land_on_empty_with_moves(self):
        board = Board()
        strategy = HumanMove(board)
        player1 = Player(1, strategy)
        player2 = Player(2, strategy)
        self.assertEqual(strategy.move_pit(player1.id, 0), MoveResult.InOwnBigPit)
        self.assertEqual(strategy.move_pit(player1.id, 1), MoveResult.Valid)
        self.assertEqual(strategy.move_pit(player2.id, 0), MoveResult.Valid)
        self.assertEqual(strategy.move_pit(player1.id, 0), MoveResult.Valid)
        self.assertEqual(player1.pits, [0, 0, 8, 8, 8, 8])
        self.assertEqual(player1.big_pit, 10)
        self.assertEqual(player2.pits, [0, 8, 7, 7, 0, 7])
        self.assertEqual(player2.big_pit, 1)

    def test_overflow_player1(self):
        board = Board()
        strategy = HumanMove(board)
        player1 = Player(1, strategy)
        player2 = Player(2, strategy)
        board.player_one_pits = [0, 0, 6, 6, 12, 6]
        board.player_one_big_pit = 12
        board.player_two_pits = [6, 6, 6, 6, 6, 6]
        board.player_two_big_pit = 0
        self.assertEqual(strategy.move_pit(player1.id, 4), MoveResult.Valid)
        self.assertEqual(player1.pits, [1, 1, 7, 7, 0, 7])
        self.assertEqual(player1.big_pit, 13)
        self.assertEqual(player2.pits, [7, 7, 7, 7, 7, 7])
        self.assertEqual(player2.big_pit, 0)

    def test_overflow_player2(self):
        board = Board()
        strategy = HumanMove(board)
        player1 = Player(1, strategy)
        player2 = Player(2, strategy)
        board.player_one_pits = [6, 6, 6, 6, 6, 6]
        board.player_one_big_pit = 0
        board.player_two_pits = [0, 0, 6, 6, 12, 6]
        board.player_two_big_pit = 12
        self.assertEqual(strategy.move_pit(player2.id, 4), MoveResult.Valid)
        self.assertEqual(player2.pits, [1, 1, 7, 7, 0, 7])
        self.assertEqual(player2.big_pit, 13)
        self.assertEqual(player1.pits, [7, 7, 7, 7, 7, 7])
        self.assertEqual(player1.big_pit, 0)

    def test_land_in_big_pit(self):
        board = Board()
        strategy = HumanMove(board)
        player1 = Player(1, strategy)
        player2 = Player(2, strategy)
        board.player_one_pits = [6, 6, 6, 6, 15, 6]
        board.player_one_big_pit = 0
        board.player_two_pits = [6, 0, 0, 6, 6, 6]
        board.player_two_big_pit = 1
        self.assertEqual(strategy.move_pit(player1.id, 4), MoveResult.InOwnBigPit)
        self.assertEqual(player1.pits, [7, 7, 7, 7, 1, 8])
        self.assertEqual(player1.big_pit, 2)
        self.assertEqual(player2.pits, [7, 1, 1, 7, 7, 7])
        self.assertEqual(player2.big_pit, 1)


if __name__ == '__main__':
    unittest.main()
