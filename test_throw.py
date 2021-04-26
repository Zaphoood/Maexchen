import unittest
from throw import Throw


class TestThrow(unittest.TestCase):
    def setUp(self):
        pass


class TestRankDict(TestThrow):
    def test_rankDict(self):
        for i in range(1, 7):
            for j in range(1, 7):
                t = Throw(i, j)
                self.assertEqual(Throw(2, 1) >= t, True)
                self.assertEqual(Throw(3, 1) <= t, True)
                self.assertEqual(t, t)


if __name__ == '__main__':
    unittest.main()
