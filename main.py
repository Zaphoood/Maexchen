import sys
from contextlib import suppress

from game import Game
from player import DummyPlayer, ShowOffPlayer, ProbabilisticPlayer
from evaluate import Evaluation

args = sys.argv[1:]
n_reps = None
verbose = False

for i, arg in enumerate(args):
    if arg == "-n":
        with suppress(ValueError, IndexError):  # contextlib.suppress
            n_reps = int(args[i + 1])
    elif arg == "-v":
        verbose = True

if n_reps is None:
    print("Must provide number of repetitions (Syntax: main.py -n [Number of repetitions])")
    sys.exit(1)

print(f"Running simulation {n_reps} times...")

if __name__ == '__main__':
    eval = Evaluation([DummyPlayer(), ShowOffPlayer(), ShowOffPlayer(), ProbabilisticPlayer(), DummyPlayer()], n_reps, verbose=verbose)
    eval.run()
    print(eval.prettyResults())
