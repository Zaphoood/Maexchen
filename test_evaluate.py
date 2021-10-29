import unittest

from evaluate import getWinner
from game import Game
from player import DummyPlayer, ShowOffPlayer, RandomPlayer
from gamelog import GameLog
from evaluate import Evaluation


class TestEvaluate(unittest.TestCase):
    def test_get_player_stats(self):
        ev = Evaluation([DummyPlayer()], 0, showProgress=False)
        ev.getPlayerStats(0)
        ev.run()
        print(ev.prettyResults())

    def test_randoms(self):
        ev = Evaluation([RandomPlayer() for _ in range(3)], 1000, showProgress=False)
        ev.run()
        print(ev.prettyResults())


if __name__ == '__main__':
    unittest.main()
