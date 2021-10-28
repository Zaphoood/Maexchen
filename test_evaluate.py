import unittest

from evaluate import getWinner
from game import Game
from player import DummyPlayer, ShowOffPlayer
from gamelog import GameLog


class TestEvaluate(unittest.TestCase):
    def test_get_winner(self):
        players = [DummyPlayer(playerId=0), DummyPlayer(playerId=1), DummyPlayer(playerId=2), ShowOffPlayer()]
        seed = 8310664473561248720
        self.game = Game(players, seed=seed)
        # Spieler neu speichern, da ihnen von Game IDs zugewiesen wurden
        players = self.game.players
        self.game.init()
        self.game.run()
        print(f"Seed is {self.game.getSeed()}\n")
        print(self.game.log.pretty())
        # Bei diesem Seed gewinnt DummyPlayer mit id=2;
        # Überprüfen von getWinner
        self.assertEqual(getWinner(self.game.log), DummyPlayer(playerId=2))

    def test_get_winner_unfinished(self):
        """getWinner() mit nicht beendetem Spiel testen."""
        self.game = Game([DummyPlayer(), DummyPlayer()])
        self.assertEqual(getWinner(self.game.log), None)
        self.game.init()
        self.assertEqual(getWinner(self.game.log), None)


if __name__ == '__main__':
    unittest.main()
