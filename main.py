from evaluate import Evaluation
from argp import ArgumentParser
import player
from game import TooFewPlayers
import logging

logging.basicConfig(format='[%(levelname)s] %(message)s', level=logging.ERROR)

parser = ArgumentParser()
parser.parseArgs()

def main_with_catch():
    """Warp the program in a try/except block that catches KeyboardInterrupt and exits nicely."""
    try:
        main()
    except KeyboardInterrupt:
        print("\nAborted")


def main():
    players = []
    for player_flag, player_class in player.FLAGS_TO_PLAYERS.items():
        # If the user provided a value after the flag, it is stored in Flag.value -> Use this as the number of players
        # Otherwise, just add one player
        n = parser.getFlag(player_flag).value or (1 & parser.getFlag(player_flag).set)
        players.extend([player_class() for _ in range(n)])
    if not players:
        parser.printHelp()
        logging.error("You must specify at least one player")
        exit(1)

    try:
        ev = Evaluation(players, parser.n_reps,
                        showProgress=not parser.getFlag("quiet").set)
        ev.run()
        if not parser.getFlag("no-write").set:
            ev.saveResultsToDisk()
        print(ev.prettyResults(sort_by_winrate=not parser.getFlag("no-sort").set, force_rerender=True))

        if parser.getFlag("plot-all").set:
            ev.plotWRandLR()
        else:
            if parser.getFlag("plot-win-rate").set:
                ev.plotWinRate()
            if parser.getFlag("plot-loss-reason").set:
                ev.plotLossReason()
    except TooFewPlayers as e:
        print(e.message)
        exit(1)


if __name__ == '__main__':
    main_with_catch()
