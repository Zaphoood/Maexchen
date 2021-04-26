from unittest import TestCase

from throw import Throw

class TestThrow(TestCase):
    def setUp(self):
        pass

class TestRankDict(TestThrow):
    def test_rankDict(self):
        for i in range(1, 7):
            for j in range(1, 7):
                t = Throw(i, j)
                assert Throw(2, 1) >= t
                assert Throw(3, 1) <= t
                assert t == t
