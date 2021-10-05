import unittest

from player import DummyPlayer, ShowOffPlayer
from gamelog import GameLog
from gameevent import EventAbort


class TestGameLog(unittest.TestCase):
    def test_abort(self):
        players = [DummyPlayer(playerId=1)]
        log = GameLog(players)
        log.happen(EventAbort())
        pretty = log.pretty()
        print(pretty)
        self.assertEqual(len(pretty.split('\n')), 4)

    def test_player_list(self):
        players = [DummyPlayer(playerId=1), ShowOffPlayer(playerId=2)]
        log = GameLog(players)
        log.happen(EventAbort())
        pretty = log.pretty()
        print(pretty)
        self.assertEqual(len(pretty.split('\n')), 5)

    def test_unfinished(self):
        players = [DummyPlayer(playerId=1)]
        log = GameLog(players)
        pretty = log.pretty()
        print(pretty)
        self.assertEqual(len(pretty.split("\n")), 3)
        self.assertTrue(pretty.endswith("(Game is still ongoing)"))


if __name__ == '__main__':
    unittest.main()
