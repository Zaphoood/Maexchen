from unittest import TestCase
from player import DummyPlayer
from throw import Throw

class TestDummyPlayer(TestCase):
    def test_get_move(self):
        dummy = DummyPlayer()
        move = dummy.getMove(Throw(3, 2), Throw(3, 1))