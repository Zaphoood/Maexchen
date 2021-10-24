import unittest

import constants as c
from player import DummyPlayer, RandomPlayer
from throw import Throw
from move import Move


class TestDummyPlayer(unittest.TestCase):
    def test_get_move(self):
        dummy = DummyPlayer()
        # Eigenes Ergebnis soll wahrheitsgemäß verkündet werden, wenn es den Vorgänger übertrumpft
        throw = Throw(3, 1)
        while throw < Throw(2, 1):
            bigger = throw + 1
            throwStated = dummy.getThrow(bigger, throw)
            self.assertEqual(throwStated, bigger)
            throw += 1

        # Vorgänger, der Mäxchen gewürfelt hat, soll immer angezweifelt werden.
        move = dummy.getDoubt(Throw(2, 1))
        self.assertEqual(move, Move(c.ALL_MOVES.DOUBT))

class TestRandomPlayer(unittest.TestCase):
    def test_get_doubt(self):
        rand = RandomPlayer()
        rand.getDoubt(Throw(2, 1))
        rand.getThrowStated(Throw(4, 5), Throw(6, 1))

if __name__ == '__main__':
    unittest.main()
