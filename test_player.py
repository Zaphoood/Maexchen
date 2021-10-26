import unittest

import constants as c
from player import DummyPlayer
from throw import Throw, OutOfBoundsError
from move import Move


class TestDummyPlayer(unittest.TestCase):
    def test_get_move(self):
        dummy = DummyPlayer()
        # Eigenes Ergebnis soll wahrheitsgemäß verkündet werden, wenn es den Vorgänger übertrumpft
        throw = Throw(3, 1)
        while throw < Throw(2, 1):
            bigger = throw + 1
            throwStated = dummy.getThrowStated(bigger, throw, 0)
            self.assertEqual(throwStated, bigger)
            throw += 1

        # Vorgänger, der Mäxchen gewürfelt hat, soll immer angezweifelt werden.
        move = dummy.getDoubt(Throw(2, 1), 0)
        self.assertTrue(move)


if __name__ == '__main__':
    unittest.main()
