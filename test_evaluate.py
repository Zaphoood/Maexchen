import unittest

from evaluate import getWinner
from game import Game
from player import Player, DummyPlayer, RandomPlayer
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

class TestOnInitPlayer(Player):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.playersReceived = None

    def onInit(self, players: list[Player]):
        print("TestOnInitPlayer got these players:")
        print("\n".join([repr(player) for player in players]))
        self.playersReceived = players

class TestOnInit(unittest.TestCase):
    def test_player_on_init(self):
        test_player = TestOnInitPlayer()
        ev = Evaluation([DummyPlayer(), test_player], 1, disableDeepcopy = True)
        self.assertEqual(ev.players, test_player.playersReceived)

if __name__ == '__main__':
    unittest.main()
