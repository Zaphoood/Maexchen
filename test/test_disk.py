import unittest
from time import time

from disk import writeLog
from player import DummyPlayer


class TestDisk(unittest.TestCase):
    def test_write(self):
        writeLog(time(), [DummyPlayer() for _ in range(10)], 10000, "Results\nbla bla\n...", log_path="results_test.log")
        
