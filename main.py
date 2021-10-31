import sys
from contextlib import suppress
import logging

from game import Game
import player
# Import individually for now
from player import DummyPlayer, ProbabilisticPlayer
from evaluate import Evaluation
import constants as c

ARGS_TO_PLAYERS = {
    "dummy": "DummyPlayer",
    "show-off": "ShowOffPlayer",
    "random": "RandomPlayer",
    "prob": "ProbabilisticPlayer",
    "probabilistic": "ProbabilisticPlayer"
}


logging_level = c.LOGGING_LEVEL
args = sys.argv[1:]
n_reps = None
quiet = False
players = []

# Don't need args now
"""
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
        try:
            player_class = ARGS_TO_PLAYERS[arg[2:]]
        except KeyError:
            raise ValueError(f"Unexpected command line argument \"{arg}\"")
        p = player.__getattribute__(player_class)
        n = 1
        with suppress(ValueError, IndexError):  # contextlib.suppress
            n = int(args[i + 1])

        players.extend([p() for _ in range(n)])
"""

logging.basicConfig(format='[%(levelname)s] %(message)s', level=logging_level)

# Use custom config for now
n_reps = 1000
players = [DummyPlayer(), DummyPlayer(), ProbabilisticPlayer(), ProbabilisticPlayer()]

print(f"Starting simulation (repetitions={n_reps})...")

if __name__ == '__main__':
    for t in c.THROW_VALUES:
        # Set new treshold
        for p in players:
            if isinstance(p, ProbabilisticPlayer):
                p.thershold = t
        eval = Evaluation(players, n_reps, showProgress=not quiet)
        eval.run()
        print(f"Results for threshold={t}")
        print(eval.prettyResults())
