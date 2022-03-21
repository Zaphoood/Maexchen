from evaluate import Evaluation
from argp import ArgumentParser
import player
from game import TooFewPlayers

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
        players.extend([player_class() for _ in range(parser.getFlag(player_flag) or 0)])

    try:
        ev = Evaluation(players, parser.n_reps,
                        showProgress=not parser.getFlag("quiet"))
        ev.run()
        if not parser.getFlag("no-write"):
            ev.saveResultsToDisk()
        print(ev.prettyResults(sort_by_winrate=not parser.getFlag("no-sort"), force_rerender=True))

        if parser.getFlag("plot-all"):
            ev.plotWRandLR()
        else:
            if parser.getFlag("plot-win-rate"):
                ev.plotWinRate()
            if parser.getFlag("plot-loss-reason"):
                ev.plotLossReason()
    # TODO: Print Exception's content here instead of `pass`ing
    except TooFewPlayers:
        pass


if __name__ == '__main__':
    main_with_catch()
