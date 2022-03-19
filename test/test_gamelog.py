import unittest

from player import DummyPlayer, ShowOffPlayer
from gamelog import GameLog
from gameevent import EventAbort


class TestGameLog(unittest.TestCase):
    def test_abort(self):
        players = [DummyPlayer(playerId=1)]
        log = GameLog(players)
        log.happen(EventAbort())
        prettyList = log.prettyList()
        self.assertEqual(len(prettyList), 3)

    def test_player_list(self):
        players = [DummyPlayer(playerId=1), ShowOffPlayer(playerId=2)]
        log = GameLog(players)
        log.happen(EventAbort())
        prettyList = log.prettyList()
        self.assertEqual(len(prettyList), 4)

    def test_unfinished(self):
        players = [DummyPlayer(playerId=1)]
        log = GameLog(players)
        prettyList = log.prettyList()
        self.assertEqual(len(prettyList), 3)
        self.assertTrue(prettyList[-1].endswith("(Game is still ongoing)"))
