import unittest
from throw import Throw, OutOfBoundsError


class TestThrow(unittest.TestCase):
    def setUp(self):
        pass


class TestRankDict(TestThrow):
    def test_rankDict(self):
        for i in range(1, 7):
            for j in range(1, 7):
                t = Throw(i, j)
                self.assertTrue(Throw(2, 1) >= t)
                self.assertTrue(Throw(3, 1) <= t)
                self.assertEqual(t, t)

    def test_validityChecks(self):
        invalidValues = [34, 35, 36, 45, 46, 56, 71]
        for value in invalidValues:
            with self.assertRaises(ValueError):
                Throw(value)

    def test_arithmetic(self):
        pairs = [(31, 32), (32, 41), (65, 11), (11, 22), (66, 21)]
        for a, b in pairs:
            first, second = Throw(a), Throw(b)
            self.assertEqual(first + 1, second)
            self.assertEqual(first, second - 1)

        # Kleinstmöglicher Wert
        small = Throw(3, 1)
        self.assertRaises(OutOfBoundsError, small.__sub__, 1)
        # Größtmöglicher Wert
        big = Throw(2, 1)
        self.assertRaises(OutOfBoundsError, big.__add__, 1)
