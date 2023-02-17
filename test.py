import pytest

from game import Game
from utils import MoveResult
from player import Player
from board import Board
from move import HumanMove


class TestGame:

    @pytest.fixture(scope='function')
    def basic_setup(self):
        board = Board()
        strategy = HumanMove(board)
        player1 = Player(1, strategy)
        player2 = Player(2, strategy)
        return board, player1, player2

    def test_player_id(self, basic_setup):
        _, player1, player2 = basic_setup
        Game(player1, player2)

    def test_player_same_id(self):
        with pytest.raises(AssertionError) as context:
            board = Board()
            strategy = HumanMove(board)
            player1 = Player(1, strategy)
            player2 = Player(1, strategy)
            Game(player1, player2)
        assert "Cannot have two player" in str(context.value)

    def test_player_invalid_id(self):
        with pytest.raises(AssertionError) as context:
            board = Board()
            strategy = HumanMove(board)
            player1 = Player(1, strategy)
            player2 = Player(3, strategy)
            Game(player1, player2)
        assert "Must be either player 1 or 2" in str(context.value)

    def test_player_basic_move(self, basic_setup):
        board, player1, player2 = basic_setup
        assert board.move_pit(player1.id, 0) == MoveResult.InOwnBigPit
        assert player1.pits == [0, 7, 7, 7, 7, 7]
        assert player1.big_pit == 1
        assert player2.pits == [6, 6, 6, 6, 6, 6]
        assert player2.big_pit == 0

    def test_player_move_empty_pit(self, basic_setup):
        board, player1, _ = basic_setup
        board.player_one_pits = [0, 7, 7, 7, 7, 7]
        board.player_one_big_pit = 1
        board.player_two_pits = [6, 6, 6, 6, 6, 6]
        board.player_two_big_pit = 0
        with pytest.raises(AssertionError) as context:
            board.move_pit(player1.id, 0)
        assert "No stones to pick" in str(context.value)

    def test_player_move_twice(self, basic_setup):
        board, player1, player2 = basic_setup
        board.player_one_pits = [0, 7, 7, 7, 7, 7]
        board.player_one_big_pit = 1
        board.player_two_pits = [6, 6, 6, 6, 6, 6]
        board.player_two_big_pit = 0
        assert board.move_pit(player1.id, 1) == MoveResult.Valid
        assert board.player_one_pits == [0, 0, 8, 8, 8, 8]
        assert player1.big_pit == 2
        assert player2.pits == [7, 7, 6, 6, 6, 6]
        assert player2.big_pit == 0

    def test_player_land_on_empty(self, basic_setup):
        board, player1, player2 = basic_setup
        board.player_one_pits = [1, 0, 8, 8, 8, 8]
        board.player_one_big_pit = 2
        board.player_two_pits = [0, 8, 7, 7, 7, 7]
        board.player_two_big_pit = 1
        assert board.move_pit(player1.id, 0) == MoveResult.Valid
        assert player1.pits == [0, 0, 8, 8, 8, 8]
        assert player1.big_pit == 10
        assert player2.pits == [0, 8, 7, 7, 0, 7]
        assert player2.big_pit == 1

    def test_land_on_empty_with_moves(self, basic_setup):
        board, player1, player2 = basic_setup
        assert board.move_pit(player1.id, 0) == MoveResult.InOwnBigPit
        assert board.move_pit(player1.id, 1) == MoveResult.Valid
        assert board.move_pit(player2.id, 0) == MoveResult.Valid
        assert board.move_pit(player1.id, 0) == MoveResult.Valid
        assert player1.pits == [0, 0, 8, 8, 8, 8]
        assert player1.big_pit == 10
        assert player2.pits == [0, 8, 7, 7, 0, 7]
        assert player2.big_pit == 1

    def test_overflow_player1(self, basic_setup):
        board, player1, player2 = basic_setup
        board.player_one_pits = [0, 0, 6, 6, 12, 6]
        board.player_one_big_pit = 12
        board.player_two_pits = [6, 6, 6, 6, 6, 6]
        board.player_two_big_pit = 0
        assert board.move_pit(player1.id, 4) == MoveResult.Valid
        assert player1.pits == [1, 1, 7, 7, 0, 7]
        assert player1.big_pit == 13
        assert player2.pits == [7, 7, 7, 7, 7, 7]
        assert player2.big_pit == 0

    def test_overflow_player2(self, basic_setup):
        board, player1, player2 = basic_setup
        board.player_one_pits = [6, 6, 6, 6, 6, 6]
        board.player_one_big_pit = 0
        board.player_two_pits = [0, 0, 6, 6, 12, 6]
        board.player_two_big_pit = 12
        assert board.move_pit(player2.id, 4) == MoveResult.Valid
        assert player2.pits == [1, 1, 7, 7, 0, 7]
        assert player2.big_pit == 13
        assert player1.pits == [7, 7, 7, 7, 7, 7]
        assert player1.big_pit == 0

    def test_land_in_big_pit(self, basic_setup):
        board, player1, player2 = basic_setup
        board.player_one_pits = [6, 6, 6, 6, 15, 6]
        board.player_one_big_pit = 0
        board.player_two_pits = [6, 0, 0, 6, 6, 6]
        board.player_two_big_pit = 1
        assert board.move_pit(player1.id, 4) == MoveResult.InOwnBigPit
        assert player1.pits == [7, 7, 7, 7, 1, 8]
        assert player1.big_pit == 2
        assert player2.pits == [7, 1, 1, 7, 7, 7]
        assert player2.big_pit == 1

    def test_player(self, basic_setup):
        board, player1, player2 = basic_setup
        assert player1.id == 1
        assert player2.id == 2
        assert player1.big_pit == board.player_one_big_pit
        assert player2.big_pit == board.player_two_big_pit
        assert player1.pits == board.player_one_pits
        assert player2.pits == board.player_two_pits
        player1.reset_all_pits()
        assert player1.pits == [0, 0, 0, 0, 0, 0]
        player1.add_stones_to_big_pit(100)
        assert player1.big_pit == 100
        player1.add_stones_to_big_pit(-5)
        assert player1.big_pit == 100
        board.player_two_pits = [1, 2, 3, 4, 5, 6]
        player2.collect_all_stones()
        assert player2.pits == [0, 0, 0, 0, 0, 0]
        assert player2.big_pit == 21

    def test_board(self, basic_setup):
        board, player1, player2 = basic_setup
        assert board.player_one_big_pit == 0
        assert board.player_two_big_pit == 0
        player2.add_stones_to_big_pit(5)
        assert board.player_big_pit(player1.id) == 0
        assert board.player_big_pit(player2.id) == 5
        board.add_stones_to_big_pit(player1.id, 6)
        assert board.player_big_pit(player1.id) == 6
        board.increment_big_pit(player1.id)
        assert board.player_big_pit(player1.id) == 7
        assert board.player_pits(player1.id) == board.player_one_pits == [6, 6, 6, 6, 6, 6]
        assert board.player_pits(player2.id) == board.player_two_pits == [6, 6, 6, 6, 6, 6]
        board.add_stones_to_pit(player2.id, 3, 6)
        assert board.player_pits(player2.id) == board.player_two_pits == [6, 6, 6, 12, 6, 6]
        board.increment_pit(player1.id, 0)
        assert board.player_pits(player1.id) == board.player_one_pits == [7, 6, 6, 6, 6, 6]
        board.reset_pit(player1.id, 1)
        assert board.player_pits(player1.id) == board.player_one_pits == [7, 0, 6, 6, 6, 6]
        board.reset_all_pits(player1.id)
        assert board.player_pits(player1.id) == board.player_one_pits == [0, 0, 0, 0, 0, 0]
