import unittest

from userplayer import UserPlayer
from throw import Throw

import random


class TestUserPlayer(unittest.TestCase):
    def setUp(self) -> None:
        self.rng = random.Random()

    def test_get_doubt(self):
        p = UserPlayer()
        print(p.getDoubt(Throw(3, 1), 0, self.rng))

    def test_get_throw_stated_first_round(self):
        p = UserPlayer()
        print(p.getThrowStated(Throw(5, 4), None, 0, self.rng))

    def test_get_throw_stated_beats(self):
        p = UserPlayer()
        print(p.getThrowStated(Throw(5, 4), Throw(3, 2), 1, self.rng))

    def test_get_throw_stated_doesnt_beat(self):
        p = UserPlayer()
        print(p.getThrowStated(Throw(5, 4), Throw(2, 1), 1, self.rng))


if __name__ == "__main__":
    unittest.main()
