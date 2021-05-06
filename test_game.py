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


class TestPlayerIds(unittest.TestCase):
    """Testet das verhalten der Game Klasse hinsichtlich dem vergeben einzigartiger ids"""

    def assert_unique_ids(self, game):
        ids = set()
        for p in game.players:
            self.assertFalse(p.id in ids)
            self.assertTrue(isinstance(p.id, int))
            ids.add(p.id)

    def test_assign(self):
        # No IDs assigned manually
        players = [DummyPlayer()] * 10
        game = Game(players)
        self.assert_unique_ids(game)

    def test_partial(self):
        # Some IDs assigned manually, some to be assigned by Game
        players = [DummyPlayer(id=3), DummyPlayer(id=100), DummyPlayer(), DummyPlayer(), DummyPlayer(id=2)]
        game = Game(players)
        self.assert_unique_ids(game)
        self.assertTrue(any([p.id == 3 for p in game.players]))
        self.assertTrue(any([p.id == 100 for p in game.players]))
        self.assertTrue(any([p.id == 2 for p in game.players]))

    def test_conflict(self):
        # Conflicting IDs assigned manually
        players = [DummyPlayer(id=2), DummyPlayer(id=2), DummyPlayer(id=3), DummyPlayer(), DummyPlayer(id=2)]
        game = Game(players)
        self.assert_unique_ids(game)


class TestThreePlayers(unittest.TestCase):
    """Testet ein Spiel mit drei Spielern.

    Es gibt kein erwartetes Ergebnis, nur, dass nach einer Runde ein Spieler übrig ist, der gewonnen hat.
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
