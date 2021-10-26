import sys
from contextlib import suppress

from game import Game
from player import DummyPlayer, ShowOffPlayer
from evaluate import Evaluation

args = sys.argv[1:]
n_reps = 1000
verbose = False

for i, arg in enumerate(args):
    if arg == "-n":
        with suppress(ValueError):  # contextlib.suppress
            n_reps = int(args[i + 1])
    elif arg == "-v":
        verbose = True

print(f"Running simulation {n_reps} times...")

if __name__ == '__main__':
    eval = Evaluation([DummyPlayer(), DummyPlayer(), ShowOffPlayer(), ShowOffPlayer()], n_reps, verbose=verbose)
    eval.run()
    print(eval.prettyResults())
