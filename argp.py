import sys
import logging
from contextlib import suppress

import constants as c
import player

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

USAGE = "Usage: python3.10 run_sim.py [NUM_REPS] [OPTIONS]"
DESCRIPTION = "The number of the times the simulation will be run \
can be specified with NUM_REPS"
OPTIONS = [
    (["-h", "--help"], "Show this help message and exit"),
    (["-v", "--verbose"], "Enable verbose output"),
    (["-q", "--quuiet"], "Quiet output, i.e. no progress bar"),
    (["-x", "--no-write"], "Don't write to log file"),
    (["-u", "--no-sort"], "Don't sort results by player win rate"),
    (["-p", "--plot-all"], "Show plots for win rate and loss reason"),
    (["--plot-win-rate"], "Show plot for win rate"),
    (["--plot-loss-reason"], "Show plot for loss reason"),
    (["--<PLAYER_CLASS> [N]"], "Add Player(s) to simulation. \
Possible values for PLAYER_CLASS are dummy, c-dummy, adv-dummy, \
random, show-off, thres[hold], tracking"),
]
MAX_LINE_LEN = 70
INDENT = 4


def printIndented(text, indent):
    print("    " * indent + text)


class ArgumentParser:
    def __init__(self) -> None:
        self.logging_level = c.LOGGING_LEVEL
        self.args = sys.argv
        self.n_reps = None
        self.quiet = False
        self.save_to_disk = True
        self.plot_win_rate = False
        self.plot_loss_reason = False
        self.plot_all_simul = False
        self.sort_results = True
        self.players = []

        self.parseArgs()

    def parseArgs(self):
        self.args = self.args[1:]
        if not self.args:
            self.printHelp()
            sys.exit(1)
        try:
            self.n_reps = int(self.args[0])
            self.args = self.args[1:]
        except (ValueError, IndexError) as e:
            print(f"\nExpected number of repetitions, got \"{self.args[0]}\"")
            sys.exit(1)
        skip_arg = False
        for i, arg in enumerate(self.args):
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
            elif arg in ["-s", "--plot-simul"]:
                plot_all_simul = True
            elif arg == "--plot-win-rate":
                plot_win_rate = True
            elif arg == "--plot-loss-reason":
                plot_loss_reason = True
            elif arg.startswith("--") and arg[2:] in ARGS_TO_PLAYERS.keys():
                player_class = ARGS_TO_PLAYERS[arg[2:]]
                p = player.__getattribute__(player_class)
                n = 1
                with suppress(ValueError, IndexError):  # contextlib.suppress
                    n = int(self.args[i + 1])
                    # Next arg is number of players -> skip next arg
                    skip_arg = True
                self.players.extend([p() for _ in range(n)])
            else:
                print(f"Unexpected command line argument \"{arg}\"")
                sys.exit(1)

    def printHelp(self):
        out = []
        out.extend([(USAGE, 0), ("", 0)])
        options_joined = [[", ".join(op), help] for op, help in OPTIONS]
        max_len = max([len(op) for op, _ in options_joined])
        help_pos = (max_len // INDENT + 1) * INDENT
        for op, help_text in options_joined:
            out.append((op + " " * (help_pos - len(op)) + help_text, 1))

        out = splitLines(out, MAX_LINE_LEN)
        for line, ind in out:
            printIndented(line, ind)


def splitLines(lines, max_len):
    """Split the given input of lines so that each line's length is less than max_len"""
    i = 0
    while i < len(lines):
        line, ind = lines[i]
        if ind * INDENT + len(line) > max_len:
            total_len = 0
            for j, word in enumerate(line.split()):
                if total_len + len(word) > max_len:
                    break
                else:
                    total_len += len(word) + 1
            lines.pop(i)
            lines.insert(i, (line[:total_len - 1], ind))
            lines.insert(i + 1, (line[total_len - 1:], ind + 1))
            i += 1
        i += 1
    return lines
