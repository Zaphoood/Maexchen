import unittest
from game import Game
from player import DummyPlayer


class TestOnePlayer(unittest.TestCase):
    def setUp(self):
        players = [DummyPlayer()]
        self.game = Game(players)

    def test_move(self):
        self.game.move()
        self.assertFalse(self.game.isRunning())


if __name__ == '__main__':
    # unittest.main()
    pass
