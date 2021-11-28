import sys
from contextlib import suppress
import logging

from game import Game
import player
from evaluate import Evaluation
import constants as c

ARGS_TO_PLAYERS = {
    "dummy": "DummyPlayer",
    "c-dummy": "CounterDummyPlayer",
    "show-off": "ShowOffPlayer",
    "random": "RandomPlayer",
    "thres": "ThresholdPlayer",
    "threshold": "ThresholdPlayer",
    "c-thres": "CounterThresPlayer",
    "tracking": "TrackingPlayer",
    "adv-dummy": "AdvancedDummyPlayer"
}

# Wenn True, immer beide Plots gleichzeitig anzeigen
PRESENTATION_MODE = True


logging_level = c.LOGGING_LEVEL
args = sys.argv[1:]
n_reps = None
quiet = False
save_to_disk = True
plot_win_rate = False
plot_loss_reason = False
sort_results = True
players = []

if not args:
    print(c.START_SIM_USAGE)
    sys.exit(1)
try:
    n_reps = int(args[0])
    args = args[1:]
except (ValueError, IndexError) as e:
    print(f"\nExpected number of repetitions, got \"{args[0]}\"")
    sys.exit(1)
skip_arg = False
for i, arg in enumerate(args):
    if skip_arg:
        skip_arg = False
        continue
    if arg in ["-q", "--quiet"]:
        quiet = True
    elif arg in ["-v", "--verbose"]:
        logging_level = logging.INFO
    elif arg in ["-x", "--no-write"]:
        save_to_disk = False
    elif arg in ["-u", "--no-sort"]:
        sort_results = False
    elif arg in ["-p", "--plot-all"]:
        plot_win_rate = True
        plot_loss_reason = True
    elif arg == "--plot-win-rate":
        plot_win_rate = True
    elif arg == "--plot-loss-reason":
        plot_loss_reason = True
    elif arg.startswith("--") and arg[2:] in ARGS_TO_PLAYERS.keys():
        player_class = ARGS_TO_PLAYERS[arg[2:]]
        p = player.__getattribute__(player_class)
        n = 1
        with suppress(ValueError, IndexError):  # contextlib.suppress
            n = int(args[i + 1])
            # Next arg is number of players -> skip next arg
            skip_arg = True
        players.extend([p() for _ in range(n)])
    else:
        print(f"Unexpected command line argument \"{arg}\"")
        sys.exit(1)

print(f"Starting simulation (repetitions={n_reps})...")

if __name__ == '__main__':
    ev = Evaluation(players, n_reps, showProgress=not quiet)
    ev.run()
    if save_to_disk:
        ev.saveResultsToDisk()
    print(ev.prettyResults(sort_by_winrate=sort_results, force_rerender=True))
    if PRESENTATION_MODE:
        ev.plotWinRate()
        ev.plotLossReason()
    else:
        if plot_win_rate:
            ev.plotWinRate()
        if plot_loss_reason:
            ev.plotLossReason()

