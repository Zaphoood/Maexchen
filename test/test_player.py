import unittest
from random import Random

import constants as c
from player import Player, DummyPlayer, RandomPlayer, TrackingPlayer, CounterThresPlayer
from player import PlayerNotInitialized
from throw import Throw
from move import Move
import gameevent
import logging


class TestInit(unittest.TestCase):
    def test_assert_initialized(self):
        p = Player()

        # This shouldn't work
        self.assertRaises(PlayerNotInitialized, p._assertInitialized)

        # Initialize player
        p.onInit([])
        try:
            # This should work
            p._assertInitialized()
        except PlayerNotInitialized:
            self.fail("Player._assertInitialized() fails even though it's onInit() has been called")


class TestDummyPlayer(unittest.TestCase):
    def setUp(self) -> None:
        self.rng = Random()  # random.Random()

    def test_get_move(self):
        dummy = DummyPlayer()
        # Eigenes Ergebnis soll wahrheitsgemäß verkündet werden, wenn es den Vorgänger übertrumpft
        throw = Throw(3, 1)
        while throw < Throw(2, 1):
            biggerThrow = throw + 1
            throwStated = dummy.getThrowStated(biggerThrow, throw, 0, self.rng)
            self.assertEqual(throwStated, biggerThrow)
            throw += 1

        # Vorgänger, der Mäxchen gewürfelt hat, soll immer angezweifelt werden.
        doubt = dummy.getDoubt(Throw(2, 1), 0, self.rng)
        doubt = dummy.getDoubt(Throw(2, 1), 1, self.rng)
        self.assertTrue(doubt)


class TestRandomPlayer(unittest.TestCase):
    def setUp(self) -> None:
        self.rng = Random()  # random.Random()

    def test_get_doubt(self):
        randomPlayer = RandomPlayer()
        randomPlayer.getDoubt(Throw(2, 1), 0, self.rng)
        randomPlayer.getThrowStated(Throw(4, 5), Throw(6, 1), 0, self.rng)

    def test_doubt_reproducibility(self):
        fixed_seed = 12345
        randomPlayer = RandomPlayer()

        last_doubt = None
        for i in range(1000):
            # Assert that the player always makes the same decision using the same rng
            self.rep_rng = Random(fixed_seed)
            doubt = randomPlayer.getDoubt(Throw(2, 1), 0, self.rep_rng)
            if last_doubt == None:
                last_doubt = doubt
            else:
                self.assertEqual(doubt, last_doubt)

    def test_throw_reproducibility(self):
        fixed_seed = 12345
        randomPlayer = RandomPlayer()

        last_throw = None
        for i in range(1000):
            # Assert that the player always makes the same decision using the same rng
            self.rep_rng = Random(fixed_seed)
            throw = randomPlayer.getThrowStated(Throw(2, 1), Throw(2, 1), 0, self.rep_rng)
            if last_throw is None:
                last_throw = throw
            else:
                self.assertEqual(throw, last_throw)


class TestTrackingPlayer(unittest.TestCase):
    def setUp(self):
        self.n_dummies = 10
        self.dummies = [DummyPlayer(playerId=i) for i in range(self.n_dummies)]
        self.tr = TrackingPlayer(playerId=self.n_dummies)
        self.tr.onInit([self.tr, *self.dummies])

    def test_stats_creation(self):
        # Überprüfen, dass leere Statistik korrekt erzeugt wird
        self.assertEqual(list(self.tr.playerStats.keys()), [p.id for p in self.dummies])

    def test_track_last_throw(self):
        # Überprüfen, dass TrackingPlayer den letzten und vorletzten Wurf abspeichert
        throw1 = Throw(3,3)
        throw2 = Throw(2,1)
        # Spieler 0 wirft 33
        self.tr.onEvent(gameevent.EventThrow(0, None, throw1))
        self.assertEqual(self.tr.lastThrow, throw1)
        # Spieler 1 wirft 21
        self.tr.onEvent(gameevent.EventThrow(1, None, throw2))
        self.assertEqual(self.tr.secondLastThrow, throw1)
        self.assertEqual(self.tr.lastThrow, throw2)
 
    def test_track_lying(self):
        # Überprüfen, dass TrackingPlayer bei lügenden Mitspielern eine entsprechende Statistik anlegt
        throw1 = Throw(3,3)
        throw2 = Throw(2,1)
        # Spieler 0 wirft 33
        self.tr.onEvent(gameevent.EventThrow(0, None, throw1))
        # Spieler 1 'wirft' 21 (lügt)
        self.tr.onEvent(gameevent.EventThrow(1, None, throw2))
        # Spieler 2 misstraut Spieler 1, Spieler 2 im Recht -> Spieler 1 wird gekickt
        # Statistik über Spieler 1 sollte jetzt 100% lügen sein, d. h. seine Glaubwürdigkeit sollte 0 sein
        kickEvent = gameevent.EventKick(1, gameevent.KICK_REASON.LYING) 
        self.tr.onEvent(kickEvent)
        self.assertEqual(self.tr.getPlayerCredibility(1), 0)
        # Überprüfen, dass für die anderen Spieler keine Statistik erstellt wurde
        for i in range(self.n_dummies + 1):
            if i != 1:
                self.assertFalse(self.tr.existPlayerStats(i))

    def test_track_truth(self):
        # Überprüfen, dass TrackingPlayer bei lügenden Mitspielern eine entsprechende Statistik anlegt
        throw1 = Throw(3,3)
        throw2 = Throw(4,4)
        # Spieler 0 wirft 33
        self.tr.onEvent(gameevent.EventThrow(0, None, throw1))
        # Spieler 1 wirft 44 (sagt die Wahrheit)
        self.tr.onEvent(gameevent.EventThrow(1, None, throw2))
        # Spieler 2 misstraut Spieler 1, Spieler 1 im Recht -> Spieler 1 wird gekickt
        # Statistik über Spieler 1 sollte jetzt 100% wahrheitsgetreu sein, d. h. seine Glaubwürdigkeit sollte 1 sein
        kickEvent = gameevent.EventKick(2, gameevent.KICK_REASON.FALSE_ACCUSATION) 
        self.tr.onEvent(kickEvent)
        self.assertEqual(self.tr.getPlayerCredibility(1), 1)


class TestCounterThresPlayer(unittest.TestCase):
    def setUp(self):
        self.n_dummies = 2
        self.dummies = [DummyPlayer(i) for i in range(self.n_dummies)]
        self.ctp = CounterThresPlayer(self.n_dummies)
        players = [self.ctp, *self.dummies]
        self.ctp.onInit(players)

    def test_init(self):
        for dummy in self.dummies:
            self.assertEqual(self.ctp.throwStats[dummy.id], [])

    def test_tracking(self):
        # TODO: Finish implementing this test case
        throw1 = Throw(3,3)

        # Spieler 0 wirft 33
        self.ctp.onEvent(gameevent.EventThrow(0, None, throw1))
