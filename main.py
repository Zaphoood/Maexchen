from evaluate import Evaluation
from argp import ArgumentParser
from player import FLAGS_TO_PLAYERS
from game import TooFewPlayers
import logging
from disk import existsPathToFile

logging.basicConfig(format='[%(levelname)s] %(message)s', level=logging.ERROR)

parser = ArgumentParser()
parser.parseArgs()

def main_with_catch():
    """Wrap the entire program in a try/except block that catches KeyboardInterrupt and exits nicely."""
    try:
        main()
    except KeyboardInterrupt:
        print("\nAborted")

def main():
    # Set up an Evaluation according to command line arguments
    players = []
    for player_flag, player_class in FLAGS_TO_PLAYERS.items():
        # If the user provided a value after the flag, it is stored in Flag.value -> Use this as the number of players
        # Otherwise, just add one player
        n = parser.getFlag(player_flag).value or (1 & parser.getFlag(player_flag).set)
        players.extend([player_class() for _ in range(n)])
    if not players:
        parser.printHelp()
        logging.error("You must specify at least one player")
        exit(1)
    if not parser.getFlag("no-write").set:
        log_path = None
        log_path_flag = parser.getFlag("out-file")
        if log_path_flag.set:
            log_path = log_path_flag.value
            if not existsPathToFile(log_path):
                logging.error(f"Can't write to {log_path}: Directory doesn't exist.")
                exit(1)
 
    # Perform the Evaluation
    ev = Evaluation(players, parser.n_reps,
                    show_progress=not parser.getFlag("quiet").set)
    try:
        ev.run()
    except TooFewPlayers as e:
        print(e.message)
        exit(1)

    ev.saveResultsToDisk(log_path=log_path)
    print(ev.prettyResults(sort_by_winrate=not parser.getFlag("no-sort").set, force_rerender=True))

    # Plot the results
    if parser.getFlag("plot-all").set:
        ev.plotWRandLR()
    else:
        if parser.getFlag("plot-win-rate").set:
            ev.plotWinRate()
        if parser.getFlag("plot-loss-reason").set:
            ev.plotLossReason()


if __name__ == '__main__':
    main_with_catch()

