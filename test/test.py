import pytest

from game import Game
from player import HumanPlayer


class TestGame:

    @pytest.fixture(scope='function')
    def basic_setup(self):
        players = {
            0: HumanPlayer(),
            1: HumanPlayer()
        }
        game = Game(players)
        return game, players

    def test_game_basic_move(self, basic_setup):
        game, players = basic_setup
        assert players[0].move(0) == (1, 5)
        assert players[0].pits == [0, 7, 7, 7, 7, 7]
        assert players[0].big_pit == 0
        assert players[1].pits == [6, 6, 6, 6, 6, 6]
        assert players[1].big_pit == 0

    def test_game_move_last(self, basic_setup):
        game, players = basic_setup
        assert players[0].move(5) == (6, 5)
        assert players[0].pits == [6, 6, 6, 6, 6, 0]
        assert players[0].big_pit == 0
        assert players[1].pits == [6, 6, 6, 6, 6, 6]
        assert players[1].big_pit == 0

    def test_game_move_empty_pit(self, basic_setup):
        game, players = basic_setup
        game.players[0].pits = [0, 7, 7, 7, 7, 7]
        game.players[0].big_pit = 1
        game.players[1].pits = [6, 6, 6, 6, 6, 6]
        game.players[1].big_pit = 0
        assert game.calculate_move(0, 0, 0) == (-1, 0)

    def test_game_move_twice(self, basic_setup):
        game, players = basic_setup
        game.players[0].pits = [0, 7, 7, 7, 7, 7]
        game.players[0].big_pit = 1
        game.players[1].pits = [6, 6, 6, 6, 6, 6]
        game.players[1].big_pit = 0
        assert game.calculate_move(0, 1, 0) == (-1, 1)
        assert game.players[0].pits == [0, 0, 8, 8, 8, 8]
        assert game.players[0].big_pit == 2
        assert game.players[1].pits == [7, 7, 6, 6, 6, 6]
        assert game.players[1].big_pit == 0

    def test_game_land_on_empty(self, basic_setup):
        game, players = basic_setup
        game.players[0].pits = [1, 0, 8, 8, 8, 8]
        game.players[0].big_pit = 2
        game.players[1].pits = [0, 8, 7, 7, 7, 7]
        game.players[1].big_pit = 1
        assert game.calculate_move(0, 0, 0) == (-1, 1)
        assert game.players[0].pits == [0, 0, 8, 8, 8, 8]
        assert game.players[0].big_pit == 10
        assert game.players[1].pits == [0, 8, 7, 7, 0, 7]
        assert game.players[1].big_pit == 1

    def test_land_on_empty_with_moves(self, basic_setup):
        game, players = basic_setup
        assert game.calculate_move(0, 0, 0) == (-1, 0)
        assert game.calculate_move(0, 1, 0) == (-1, 1)
        assert game.calculate_move(1, 0, 1) == (-1, 0)
        assert game.calculate_move(0, 0, 0) == (-1, 1)
        assert game.players[0].pits == [0, 0, 8, 8, 8, 8]
        assert game.players[0].big_pit == 10
        assert game.players[1].pits == [0, 8, 7, 7, 0, 7]
        assert game.players[1].big_pit == 1

    def test_overflow_player1(self, basic_setup):
        game, players = basic_setup
        game.players[0].pits = [2, 3, 9, 9, 2, 4]
        game.players[0].big_pit = 6
        game.players[1].pits = [2, 9, 8, 8, 8, 0]
        game.players[1].big_pit = 2
        assert game.calculate_move(0, 5, 0) == (-1, 1)
        assert game.players[0].pits == [2, 3, 9, 9, 2, 0]
        assert game.players[0].big_pit == 7
        assert game.players[1].pits == [3, 10, 9, 8, 8, 0]
        assert game.players[1].big_pit == 2

    def test_overflow_player1_back_around(self, basic_setup):
        game, players = basic_setup
        game.players[0].pits = [2, 1, 9, 9, 1, 10]
        game.players[0].big_pit = 3
        game.players[1].pits = [2, 9, 8, 8, 8, 0]
        game.players[1].big_pit = 2
        assert game.calculate_move(0, 5, 0) == (-1, 1)
        assert game.players[0].pits == [3, 2, 10, 9, 1, 0]
        assert game.players[0].big_pit == 4
        assert game.players[1].pits == [3, 10, 9, 9, 9, 1]
        assert game.players[1].big_pit == 2

    def test_overflow_player2(self, basic_setup):
        game, players = basic_setup
        game.players[0].pits = [0, 7, 7, 7, 7, 7]
        game.players[0].big_pit = 1
        game.players[1].pits = [6, 6, 6, 6, 6, 3]
        game.players[1].big_pit = 3
        assert game.calculate_move(1, 5, 1) == (-1, 0)
        assert game.players[1].pits == [6, 6, 6, 6, 6, 0]
        assert game.players[1].big_pit == 4
        assert game.players[0].pits == [1, 8, 7, 7, 7, 7]
        assert game.players[0].big_pit == 1

    def test_land_in_big_pit(self, basic_setup):
        game, players = basic_setup
        game.players[0].pits = [6, 6, 4, 6, 6, 6]
        game.players[0].big_pit = 2
        game.players[1].pits = [6, 6, 6, 6, 6, 6]
        game.players[1].big_pit = 0
        assert game.calculate_move(0, 2, 0) == (-1, 0)
        assert game.players[0].pits == [6, 6, 0, 7, 7, 7]
        assert game.players[0].big_pit == 3
        assert game.players[1].pits == [6, 6, 6, 6, 6, 6]
        assert game.players[1].big_pit == 0

    def test_player_move(self, basic_setup):
        game, players = basic_setup
        assert game.players[0].big_pit == game.players[1].big_pit == 0
        assert game.players[0].pits == game.players[0].pits == [6, 6, 6, 6, 6, 6]
        assert players[0].move(0) == (1, 5)
        assert players[0].pits == [0, 7, 7, 7, 7, 7]

    def test_player_move_twice(self, basic_setup):
        game, players = basic_setup
        assert players[0].move(5) == (6, 5)
        assert players[0].pits == [6, 6, 6, 6, 6, 0]
        game.players[0].pits = [6, 2, 6, 6, 6, 0]
        assert players[0].move(1) == (0, 3)
        assert players[0].pits == [6, 0, 7, 7, 6, 0]

    def test_player_add_negative_stones(self, basic_setup):
        game, players = basic_setup
        with pytest.raises(AssertionError) as context:
            game.players[0].add_stones(-5)
            assert "Cannot add not-positive number of stones!" in str(context.value)
        assert players[0].pits == [6, 6, 6, 6, 6, 6]

    def test_player_add_zero_stones(self, basic_setup):
        game, players = basic_setup
        with pytest.raises(AssertionError) as context:
            game.players[0].add_stones(0)
            assert "Cannot add not-positive number of stones!" in str(context.value)
        assert players[0].pits == [6, 6, 6, 6, 6, 6]

    def test_player_add_stones(self, basic_setup):
        game, players = basic_setup
        assert game.players[0].add_stones(3) == 0
        assert game.players[0].add_stones(6) == 0
        assert game.players[0].add_stones(7) == 1
        assert players[0].pits == [9, 9, 9, 8, 8, 8]

    def test_player_collect_stones(self, basic_setup):
        game, players = basic_setup
        game.players[0].pits = [9, 9, 9, 8, 8, 8]
        players[0].collect_all_stones()
        assert players[0].pits == [0, 0, 0, 0, 0, 0]
        assert players[0].big_pit == 51
        assert game.players[0].add_stones(4) == -1

    def test_game_win(self, basic_setup):
        game, players = basic_setup
        assert game.check_win() == -1
        game.players[0].pits = [0, 0, 0, 0, 0, 0]
        game.players[1].pits = [12, 12, 12, 12, 12, 12]
        game.players[1].collect_all_stones()
        assert game.check_win() == 1
        game.players[0].reset()
        game.players[1].reset()
        game.players[0].pits = [12, 12, 12, 12, 12, 12]
        game.players[1].pits = [0, 0, 0, 0, 0, 0]
        game.players[0].collect_all_stones()
        assert game.check_win() == 0


