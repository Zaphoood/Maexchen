import sys
from contextlib import suppress
import logging

from game import Game
import player
from evaluate import Evaluation
import constants as c

ARGS_TO_PLAYERS = {
    "dummy": "DummyPlayer",
    "random": "RandomPlayer",
    "show-off": "ShowOffPlayer",
    "prob": "ProbabilisticPlayer",
    "probabilistic": "ProbabilisticPlayer"
}


logging_level = c.LOGGING_LEVEL
args = sys.argv[1:]
n_reps = None
verbose = False
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
    if arg == "-p":
        verbose = True
    elif arg == "-v":
        logging_level = logging.INFO
    elif arg.startswith("--"):
        try:
            p = player.__getattribute__(ARGS_TO_PLAYERS[arg[2:]])
        except:
            raise ValueError(f"Unexpected command line argument \"{arg}\"")
        n = 1
        with suppress(ValueError, IndexError):  # contextlib.suppress
            n = int(args[i + 1])

        players.extend([p() for _ in range(n)])

logging.basicConfig(format='[%(levelname)s] %(message)s', level=logging_level)

print(f"Starting simulation (repetitions={n_reps})...")

if __name__ == '__main__':
    eval = Evaluation(players, n_reps, verbose=verbose)
    eval.run()
    print(eval.prettyResults())
