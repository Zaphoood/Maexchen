import unittest
from random import Random

import constants as c
from player import DummyPlayer, RandomPlayer
from throw import Throw
from move import Move


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

if __name__ == '__main__':
    unittest.main()
