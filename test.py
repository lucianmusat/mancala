import unittest

from game import Game
from utils import MoveResult
from player import HumanPlayer


class TestGame(unittest.TestCase):

    def test_player_id(self):
        player1 = HumanPlayer(1)
        player2 = HumanPlayer(2)
        Game(player1, player2)

    def test_player_same_id(self):
        with self.assertRaises(AssertionError) as context:
            player1 = HumanPlayer(1)
            player2 = HumanPlayer(1)
            Game(player1, player2)
        self.assertTrue("Cannot have two player" in str(context.exception))

    def test_player_invalid_id(self):
        with self.assertRaises(AssertionError) as context:
            player1 = HumanPlayer(1)
            player2 = HumanPlayer(3)
            Game(player1, player2)
        self.assertTrue("Must be either player 1 or 2" in str(context.exception))

    def test_player_basic_move(self):
        player1 = HumanPlayer(1)
        player2 = HumanPlayer(2)
        self.assertEqual(player1.move_pit(0, player2), MoveResult.InOwnBigPit)
        self.assertEqual(player1.pits, [0, 7, 7, 7, 7, 7])
        self.assertEqual(player1.big_pit, 1)
        self.assertEqual(player2.pits, [6, 6, 6, 6, 6, 6])
        self.assertEqual(player2.big_pit, 0)

    def test_player_move_empty_pit(self):
        player1 = HumanPlayer(1)
        player2 = HumanPlayer(2)
        player1.pits = [0, 7, 7, 7, 7, 7]
        player1.big_pit = 1
        player2.pits = [6, 6, 6, 6, 6, 6]
        player2.big_pit = 0
        with self.assertRaises(AssertionError) as context:
            player1.move_pit(0, player2)
        self.assertTrue("No stones to pick" in str(context.exception))

    def test_player_move_twice(self):
        player1 = HumanPlayer(1)
        player2 = HumanPlayer(2)
        player1.pits = [0, 7, 7, 7, 7, 7]
        player1.big_pit = 1
        player2.pits = [6, 6, 6, 6, 6, 6]
        player2.big_pit = 0
        self.assertEqual(player1.move_pit(1, player2), MoveResult.Valid)
        self.assertEqual(player1.pits, [0, 0, 8, 8, 8, 8])
        self.assertEqual(player1.big_pit, 2)
        self.assertEqual(player2.pits, [7, 7, 6, 6, 6, 6])
        self.assertEqual(player2.big_pit, 0)

    def test_player_land_on_empty(self):
        player1 = HumanPlayer(1)
        player2 = HumanPlayer(2)
        player1.pits = [1, 0, 8, 8, 8, 8]
        player1.big_pit = 2
        player2.pits = [0, 8, 7, 7, 7, 7]
        player2.big_pit = 1
        self.assertEqual(player1.move_pit(0, player2), MoveResult.Valid)
        self.assertEqual(player1.pits, [0, 0, 8, 8, 8, 8])
        self.assertEqual(player1.big_pit, 10)
        self.assertEqual(player2.pits, [0, 8, 7, 7, 0, 7])
        self.assertEqual(player2.big_pit, 1)

    def test_overflow_player1(self):
        player1 = HumanPlayer(1)
        player2 = HumanPlayer(2)
        player1.pits = [0, 0, 6, 6, 12, 6]
        player1.big_pit = 12
        player2.pits = [6, 6, 6, 6, 6, 6]
        player2.big_pit = 0
        self.assertEqual(player1.move_pit(4, player2), MoveResult.Valid)
        self.assertEqual(player1.pits, [1, 1, 7, 7, 0, 7])
        self.assertEqual(player1.big_pit, 13)
        self.assertEqual(player2.pits, [7, 7, 7, 7, 7, 7])
        self.assertEqual(player2.big_pit, 0)

    def test_overflow_player2(self):
        player1 = HumanPlayer(1)
        player2 = HumanPlayer(2)
        player1.pits = [6, 6, 6, 6, 6, 6]
        player1.big_pit = 0
        player2.pits = [0, 0, 6, 6, 12, 6]
        player2.big_pit = 12
        self.assertEqual(player2.move_pit(4, player1), MoveResult.Valid)
        self.assertEqual(player2.pits, [1, 1, 7, 7, 0, 7])
        self.assertEqual(player2.big_pit, 13)
        self.assertEqual(player1.pits, [7, 7, 7, 7, 7, 7])
        self.assertEqual(player1.big_pit, 0)

    def test_land_in_big_pit(self):
        player1 = HumanPlayer(1)
        player2 = HumanPlayer(2)
        player1.pits = [6, 6, 6, 6, 15, 6]
        player1.big_pit = 0
        player2.pits = [6, 0, 0, 6, 6, 6]
        player2.big_pit = 1
        self.assertEqual(player1.move_pit(4, player2), MoveResult.InOwnBigPit)
        self.assertEqual(player1.pits, [7, 7, 7, 7, 1, 8])
        self.assertEqual(player1.big_pit, 2)
        self.assertEqual(player2.pits, [7, 1, 1, 7, 7, 7])
        self.assertEqual(player2.big_pit, 1)


if __name__ == '__main__':
    unittest.main()
