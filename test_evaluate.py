from unittest import TestCase

from evaluate import getWinner
from game import Game
from player import DummyPlayer, ShowOffPlayer
from gamelog import GameLog


class TestEvaluate(TestCase):
    def test_get_winner(self):
        players = [DummyPlayer(), ShowOffPlayer()]
        seed = 8310664473561248720
        self.game = Game(players, seed=seed)
        self.game.init()
        self.game.run()
        print(f"Seed is {self.game.getSeed()}\n")
        print(self.game.log.pretty())
        # Bei diesem Seed gewinnt DummyPlayer
        self.assertEqual(getWinner(self.game.log), players[0])
