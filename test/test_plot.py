import unittest

from plot import plotWinRate, plotLossReason, plotBoth


class TestPlot(unittest.TestCase):
    def test_plot_win_rate(self):
        player_names = ["AdvancedDummyPlayer 0", "DummyPlayer 1", "CounterDummyPlayer 2"]
        win_rates = [0.67, 0.08, 0.25]

        plotWinRate(player_names, win_rates)

    def test_plot_loss_reason(self):
        player_names = ["AdvancedDummyPlayer 0", "DummyPlayer 1", "CounterDummyPlayer 2"]
        loss_reaons = [
            [0.36, 0.64, 0],
            [0.9, 0.1, 0],
            [0.61, 0.23, 0.16],
        ]

        plotLossReason(player_names, loss_reaons)


if __name__ == "__main__":
    unittest.main()
