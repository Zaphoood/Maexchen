import unittest

from player import DummyPlayer, ShowOffPlayer
from gamelog import GameLog
from gameevent import EventAbort, EventFinish


class TestGameLog(unittest.TestCase):
    def test_abort(self):
        players = [DummyPlayer(player_id=1)]
        log = GameLog(players)
        log.happen(EventAbort())

    def test_player_list(self):
        players = [DummyPlayer(player_id=1), ShowOffPlayer(player_id=2)]
        log = GameLog(players)

        e_abort = EventAbort()
        log.happen(e_abort)
        self.assertEqual(log.getEvents(), [e_abort])
        self.assertEqual(log.countRounds(), 1)
        log.newRound()
        self.assertEqual(log.countRounds(), 2)

        log.pretty()

    def test_unfinished(self):
        players = [DummyPlayer(player_id=1)]

        log = GameLog(players)
        self.assertFalse(log.hasFinished())
        log.pretty()
        log.happen(EventFinish(0))
        self.assertTrue(log.hasFinished())

        log = GameLog(players)
        log.happen(EventAbort())
        self.assertTrue(log.hasFinished())
