from unittest import TestCase

from evaluate import getWinner
from game import Game
from player import DummyPlayer, ShowOffPlayer
from gamelog import GameLog

class TestEvaluate(TestCase):
    def test_get_winner(self):
        players = [DummyPlayer(), ShowOffPlayer()]
        self.game = Game(players)
        print(self.game.log.pretty())
