import sys
from contextlib import suppress
import logging

from game import Game
from evaluate import Evaluation
import constants as c
from argp import ArgumentParser

# Wenn True, immer beide Plots gleichzeitig anzeigen
PRESENTATION_MODE = True

parser = ArgumentParser()

print(f"Starting simulation (repetitions={parser.n_reps})...")

if __name__ == '__main__':
    ev = Evaluation(parser.players, parser.n_reps,
                    showProgress=not parser.quiet)
    ev.run()
    if parser.save_to_disk:
        ev.saveResultsToDisk()
    print(ev.prettyResults(sort_by_winrate=parser.sort_results, force_rerender=True))

    if parser.plot_all_simul or PRESENTATION_MODE:
        ev.plotWRandLR()
    else:
        if parser.plot_win_rate:
            ev.plotWinRate()
        if parser.plot_loss_reason:
            ev.plotLossReason()
