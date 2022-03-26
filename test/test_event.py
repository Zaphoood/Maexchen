from unittest import TestCase
from gameevent import Event, EventThrow, EventDoubt, EventKick, EventFinish, EventAbort
from gameevent import EVENT_TYPES, KICK_REASON
from throw import Throw

class TestEvent(TestCase):
    def test_init(self):
        e_throw = EventThrow(0, Throw(21), Throw(21))
        self.assertTrue(e_throw.isTruthful)
        e_throw = EventThrow(0, Throw(21), Throw(66))
        self.assertFalse(e_throw.isTruthful)

        e_doubt = EventDoubt(0)

        e_kick = EventKick(0, KICK_REASON.LYING)

        e_finish = EventFinish(0)

        e_abort = EventAbort()
        e_abort_msg = EventAbort("Abort message")
