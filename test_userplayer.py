from unittest import TestCase

from userplayer import UserPlayer
from throw import Throw

class TestUserPlayer(TestCase):
    def test_get_doubt(self):
        p = UserPlayer()
        print(p.getDoubt(Throw(3, 1)))

    def test_get_throw_stated_beats(self):
        p = UserPlayer()
        print(p.getThrowStated(Throw(5, 4), Throw(3, 2)))

    def test_get_throw_stated_doesnt_beat(self):
        p = UserPlayer()
        print(p.getThrowStated(Throw(5, 4), Throw(2, 1)))
