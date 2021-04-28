import unittest
from game import Game
from player import DummyPlayer


class TestOnePlayer(unittest.TestCase):
    """Testet ein Spiel mit nur einem Spieler"""

    def setUp(self):
        players = [DummyPlayer()]
        self.game = Game(players)

    def test_move(self):
        self.game.init()
        self.game.move()
        self.assertFalse(self.game.isRunning())


class TestThreePlayers(unittest.TestCase):
    """Testet ein Spiel mit drei Spielern.

    Es gibt kein erwartetes Ergebnis, nur, dass am Ende ein Spieler übrig ist, der gewonnen hat.
    """

    def setUp(self):
        players = [DummyPlayer()] * 3
        self.game = Game(players)

    def test_game(self):
        self.game.init()
        while self.game.isRunning():
            self.game.move()


if __name__ == '__main__':
    unittest.main()
