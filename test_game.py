import unittest
import logging

from game import Game
from player import Player, DummyPlayer, ShowOffPlayer, RandomPlayer, ProbabilisticPlayer, TrackingPlayer
from userplayer import UserPlayer
from gamelog import GameLog
import gameevent
import throw

logging.basicConfig(format='[%(levelname)s] %(message)s', level=logging.INFO)


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
        players = [DummyPlayer(playerId=3), DummyPlayer(playerId=100), DummyPlayer(), DummyPlayer(), DummyPlayer(playerId=2)]
        game = Game(players)
        self.assert_unique_ids(game)
        self.assertTrue(any([p.id == 3 for p in game.players]))
        self.assertTrue(any([p.id == 100 for p in game.players]))
        self.assertTrue(any([p.id == 2 for p in game.players]))

    def test_conflict(self):
        # Conflicting IDs assigned manually
        players = [DummyPlayer(playerId=2), DummyPlayer(playerId=2), DummyPlayer(playerId=3), DummyPlayer(), DummyPlayer(playerId=2)]
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
        self.game.run()

class TestLog(unittest.TestCase):
    def test_log(self):
        log1 = GameLog()
        log1.happen(gameevent.EventAbort)
        log2 = GameLog()
        log2.happen(gameevent.EventAbort)
        self.assertEqual(log1, log2)


class TestGameWithLog(unittest.TestCase):
    def test_gamewlog(self):
        fixed_seed = 123456
        game1 = Game([DummyPlayer()] * 4, seed=fixed_seed)
        game1.init()
        game1.run()
        game2 = Game([DummyPlayer()] * 4, seed=fixed_seed)
        game2.init()
        game2.run()
        self.assertEqual(game1.log, game2.log)
        print(game1.log.pretty())


class TestGameEvent(unittest.TestCase):
    def test_gameevent_equals(self):
        e1 = gameevent.EventThrow(1, throw.Throw(1, 2), throw.Throw(1, 2))
        e2 = gameevent.EventThrow(1, throw.Throw(1, 2), throw.Throw(1, 2))
        self.assertEqual(e1, e2)
        e1 = gameevent.EventDoubt(1)
        e2 = gameevent.EventDoubt(1)
        self.assertEqual(e1, e2)
        e1 = gameevent.EventKick(1, "reason")
        e2 = gameevent.EventKick(1, "reason")
        self.assertEqual(e1, e2)
        p = Player(1)
        e1 = gameevent.EventFinish(p)
        e2 = gameevent.EventFinish(p)
        self.assertEqual(e1, e2)
        e1 = gameevent.EventAbort()
        e2 = gameevent.EventAbort()
        self.assertEqual(e1, e2)


class TestGameUser(unittest.TestCase):
    def test_game_w_user(self):
        up = UserPlayer()
        game = Game([DummyPlayer()] * 2 + [ShowOffPlayer(), up])
        game.init()
        game.run()

class EventListenerPlayer(Player):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.listensToEvents = True

    def getDoubt(lastThrow, *args, **kwargs):
        return False

    def getThrowStated(myThrow, lastThrow, *args, **kwargs):
        return lastThrow + 1

    def onEvent(self, event):
        print(f"EventListenerPlayer got Event: {event}")

class TestEventListening(unittest.TestCase):
    def test_event_listening(self):
        game = Game([RandomPlayer(), EventListenerPlayer()])
        game.init()
        game.run()

class TestTrackingPlayer(unittest.TestCase):
    def test_normal_functionality(self):
        players = [DummyPlayer(), RandomPlayer(), ProbabilisticPlayer(), TrackingPlayer()]
        for i, player in enumerate(players):
            player.id = i
        game = Game(players)
        game.init()
        game.run()

if __name__ == '__main__':
    unittest.main()
