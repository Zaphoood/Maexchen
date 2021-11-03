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
    "tracking": "TrackingPlayer",
    "adv-dummy": "AdvancedDummyPlayer"
}


logging_level = c.LOGGING_LEVEL
args = sys.argv[1:]
n_reps = None
quiet = False
save_to_disk = True
players = []

if not args:
    print(c.START_SIM_USAGE)
    sys.exit(1)
    
try:
    n_reps = int(args[0])
except (ValueError, IndexError) as e:
    print(f"\nExpected number of repetitions, got \"{args[0]}\"")
    sys.exit(1)
for i, arg in enumerate(args):
    if arg == "-q":
        quiet = True
    elif arg == "-v":
        logging_level = logging.INFO
    elif arg.startswith("--"):
        if arg == "--no-write":
            write_to_disk = False
        elif arg[2:] in ARGS_TO_PLAYERS.keys():
            player_class = ARGS_TO_PLAYERS[arg[2:]]
            p = player.__getattribute__(player_class)
            n = 1
            with suppress(ValueError, IndexError):  # contextlib.suppress
                n = int(args[i + 1])
            players.extend([p() for _ in range(n)])
        else:
            raise ValueError(f"Unexpected command line argument \"{arg}\"")


logging.basicConfig(format='[%(levelname)s] %(message)s', level=logging_level)

print(f"Starting simulation (repetitions={n_reps})...")

if __name__ == '__main__':
    eval = Evaluation(players, n_reps, showProgress=not quiet)
    eval.run()
    if save_to_disk:
        eval.saveResultsToDisk()
    print(eval.prettyResults())
