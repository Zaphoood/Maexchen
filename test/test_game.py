import unittest
import logging

from game import Game, TooFewPlayers
from player import Player, DummyPlayer, AdvancedDummyPlayer, CounterDummyPlayer, ShowOffPlayer, RandomPlayer, ThresholdPlayer, TrackingPlayer
from gamelog import GameLog
import gameevent
from throw import Throw

logging.basicConfig(format='[%(levelname)s] %(message)s', level=logging.INFO)


class TestInit(unittest.TestCase):
    def test_seed(self):
        Game([DummyPlayer()], seed=123)

    def test_deepcopy(self):
        # No deepcopy, a and b should be references to the same object
        a, b = [DummyPlayer()] * 2
        game = Game([a, b], deepcopy=False)
        self.assertTrue(game.players[0] is game.players[1])

        # No deepcopy, a and b should individual objects
        a, b = [DummyPlayer()] * 2
        game = Game([a, b], deepcopy=True)
        self.assertFalse(game.players[0] is game.players[1])

    def test_shuffle(self):
        Game([DummyPlayer()], shufflePlayers=False)
        Game([DummyPlayer()], shufflePlayers=True)

class TestNPlayers(unittest.TestCase):
    """Testet Spiele mit verschiedenen Spielerzahlen"""

    def test_one(self):
        game = Game([])
        self.assertRaises(TooFewPlayers, game.init)
        game = Game([DummyPlayer()])
        self.assertRaises(TooFewPlayers, game.init)

    def test_three(self):
        players = [DummyPlayer()] * 3
        self.game = Game(players)
        self.game.init()
        self.game.run()


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


class TestGameEvent(unittest.TestCase):
    def test_gameevent_equals(self):
        e1 = gameevent.EventThrow(1, Throw(1, 2), Throw(1, 2))
        e2 = gameevent.EventThrow(1, Throw(1, 2), Throw(1, 2))
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


class EventListenerPlayer(Player):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.listensToEvents = True

    def getDoubt(lastThrow, *args, **kwargs):
        return False

    def getThrowStated(myThrow, lastThrow, *args, **kwargs):
        return Throw(2, 1) if lastThrow.isMaexchen else lastThrow + 1

    def onEvent(self, event):
        logging.info(f"EventListenerPlayer got Event: {event}")


class TestEventListening(unittest.TestCase):
    def test_methods(self):
        p = EventListenerPlayer()
        p.getDoubt(Throw(2, 1))
    def test_game(self):
        game = Game([RandomPlayer(), EventListenerPlayer()])
        game.init()
        game.run()


class TestTrackingPlayer(unittest.TestCase):
    def test_normal_functionality(self):
        tracking_player = TrackingPlayer()
        players = [DummyPlayer(), RandomPlayer(), ThresholdPlayer(), tracking_player]
        game = Game(players, deepcopy=True)
        tracking_player.onInit(game.players)
        game.init()
        game.run()


class TestAll(unittest.TestCase):
    def test_all(self):
        tr = TrackingPlayer()
        players = [DummyPlayer(),  AdvancedDummyPlayer(), CounterDummyPlayer(), ShowOffPlayer(), RandomPlayer(), ThresholdPlayer(), tr]
        game = Game(players, deepcopy=True)
        tr.onInit(game.players)
        game.init()
        game.run()
