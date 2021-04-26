import unittest
from player import DummyPlayer
from throw import Throw, OutOfBoundsError
from move import MoveThrow, MoveDoubt


class TestDummyPlayer(unittest.TestCase):
    def test_get_move(self):
        dummy = DummyPlayer()
        # Eigenes Ergebnis soll wahrheitsgemäß verkündet werden, wenn es den
        # Vorgänger übertrumpft
        throw = Throw(3, 1)
        while throw < Throw(2, 1):
            bigger = throw + 1
            move = dummy.getMove(bigger, throw)
            self.assertEqual(move, MoveThrow(bigger))
            throw += 1

        # Vorgänger, der Mäxchen gewürfelt hat, soll immer angezweifelt werden.
        move = dummy.getMove(Throw(5, 1), Throw(2, 1))
        self.assertEqual(move, MoveDoubt())


if __name__ == '__main__':
    unittest.main()
