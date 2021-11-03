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
    "prob": "ProbabilisticPlayer",
    "probabilistic": "ProbabilisticPlayer",
    "tracking": "TrackingPlayer"
}


logging_level = c.LOGGING_LEVEL
args = sys.argv[1:]
n_reps = None
quiet = False
save_to_disk = True
plot_win_rate = False
plot_loss_reason = False
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
    if arg == "-q":
        quiet = True
    elif arg == "-v":
        logging_level = logging.INFO
    elif arg == "-x":
        save_to_disk = False
    elif arg == "-p":
        plot_win_rate = True
        plot_loss_reason = True
    elif arg == "--no-write":
        save_to_disk = False
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
        players.extend([p() for _ in range(n)])
        # Skip next arg
        skip_arg = True
    else:
        raise ValueError(f"Unexpected command line argument \"{arg}\"")


logging.basicConfig(format='[%(levelname)s] %(message)s', level=logging_level)

print(f"Starting simulation (repetitions={n_reps})...")

if __name__ == '__main__':
    ev = Evaluation(players, n_reps, showProgress=not quiet)
    ev.run()
    if save_to_disk:
        ev.saveResultsToDisk()
    print(ev.prettyResults())
    if plot_win_rate:
        ev.plotWinRate()
    if plot_loss_reason:
        ev.plotLossReason()
