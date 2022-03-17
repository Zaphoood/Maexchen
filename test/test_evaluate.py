import unittest

from game import Game
from player import Player, DummyPlayer, AdvancedDummyPlayer, CounterDummyPlayer, ShowOffPlayer, RandomPlayer, ThresholdPlayer, TrackingPlayer, CounterThresPlayer
from gamelog import GameLog
from evaluate import Evaluation


class TestEvaluate(unittest.TestCase):
    def test_get_player_stats(self):
        ev = Evaluation([DummyPlayer()], 0, showProgress=False)
        ev.getPlayerStats(0)
        ev.run()
        print(ev.prettyResults())

    def test_randoms(self):
        ev = Evaluation([RandomPlayer() for _ in range(3)], 1000, showProgress=False)
        ev.run()
        print(ev.prettyResults())

class TestOnInitPlayer(Player):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.playersReceived = None

    def onInit(self, players: list[Player]):
        print("TestOnInitPlayer got these players:")
        print("\n".join([repr(player) for player in players]))
        self.playersReceived = players

class TestOnInit(unittest.TestCase):
    def test_player_on_init(self):
        test_player = TestOnInitPlayer()
        ev = Evaluation([DummyPlayer(), test_player], 1, disableDeepcopy = True)
        self.assertEqual(ev.players, test_player.playersReceived)

class TestAll(unittest.TestCase):
    def test_all(self):
        players = [DummyPlayer(),  AdvancedDummyPlayer(), CounterDummyPlayer(), ShowOffPlayer(), RandomPlayer(), ThresholdPlayer(), TrackingPlayer(), CounterThresPlayer()]
        ev = Evaluation(players, 1000, showProgress = True)
        ev.run()
        print(ev.prettyResults())
        ev.plotWinRate()
        ev.plotLossReason()

class TestCounterThres(unittest.TestCase):
    def test_dummy(self):
        self.ctp = CounterThresPlayer()
        self.players = [self.ctp, *[DummyPlayer() for _ in range(2)]]
        self.runSim()

    def test_thres(self):
        self.ctp = CounterThresPlayer()
        tr1 = ThresholdPlayer(lieThreshold=21) 
        tr2 = ThresholdPlayer(lieThreshold=61) 
        print(f"\nSimulation with: \n{tr1.lieThreshold=}")
        print(f"{tr2.lieThreshold=}")
        self.players = [self.ctp, tr1, tr2]
        self.runSim()

    def runSim(self):
        ev = Evaluation(self.players, 1000, showProgress = True, disableDeepcopy=True)
        ev.run()
        print(ev.prettyResults())
        print(f"CounterThresPlayer judgement:")
        for p in ev.players:
            if p is self.ctp:
                continue
            if self.ctp.existThresSuggestion(p.id):
                print(f"  {repr(p)} Is a ThresPlayer: lieThres={self.ctp.mostFreqThrow(p.id)}\t({self.ctp.mostFreqThrowFreq(p.id):.3f})")
            else:
                print(f"  {repr(p)} Is not a ThresPlayer\t\t\t({self.ctp.mostFreqThrowFreq(p.id):.3f})")



if __name__ == '__main__':
    unittest.main()
