from dataclasses import dataclass
import sys
from typing import List, Optional, Any

from player import Player, FLAGS_TO_PLAYERS
import constants as c


@dataclass
class Flag:
    name: str
    aliases: List[str]
    help_str: str
    # Whether this flag must be followed by a value.
    # A value of 0 indicates it must not be followed by a value,
    # 1 means optional and 2 means obligatory
    value_after: int = 0
    # What the type the value after the flag should have
    value_after_type: Any = None
    # Name for the flag to use in the help section instead of its actual name
    help_alias: Optional[str] = None
    # Whether to omit this flag in the help section
    hidden: bool = False
    # Whether the flag has been set
    _set: bool = False
    # A value which followed the flag. Whether this value is allowed/obligatory
    # is specified by value_after
    value: Any = None

    @property
    def set(self) -> bool:
        return self._set

    @set.setter
    def set(self, value: bool) -> None:
        assert isinstance(value, bool)
        self._set = value


player_flags = ", ".join(FLAGS_TO_PLAYERS.keys())

PROG = "python3.9 main.py"
USAGE = f"Usage: {PROG} NUM_REPS [OPTIONS]"
DESCRIPTION = "The number of the times the simulation will be run \
is specified by NUM_REPS"

FLAGS: List[Flag] = [
    Flag("help", ["-h", "--help"], "Show this help message and exit"),
    Flag("verbose", ["-v", "--verbose"], "Enable verbose output"),
    Flag("quiet", ["-q", "--quiet"], "Quiet output, i.e. no progress bar"),
    Flag("no-write", ["-x", "--no-write"], "Don't write to log file"),
    Flag("out-file", ["-o", "--out"], "Output file to which simulation results are written", value_after=2, value_after_type=str),
    Flag("no-sort", ["-u", "--no-sort"],
         "Don't sort results by player win rate"),
    Flag("plot-all", ["-p", "--plot-all"],
         "Show plots for win rate and loss reason"),
    Flag("plot-win-rate", ["--plot-win-rate"], "Show plot for win rate"),
    Flag("plot-loss-reason", ["--plot-loss-reason"],
         "Show plot for loss reason"),
    # Only used in help section
    Flag("player-class-dummy", [], help_alias="--<PLAYER_CLASS> [N]",
         help_str=f"Add N Player(s) of PLAYER_CLASS to simulation. Possible values for PLAYER_CLASS are: {player_flags}."),
]
# Add a flag for each player
FLAGS += [Flag(player_arg, [f"--{player_arg}"], "", hidden=True, value_after=1,
               value_after_type=int) for player_arg in FLAGS_TO_PLAYERS.keys()]

MAX_LINE_LEN = 80
INDENT = 2
HELP_TEXT_BORDER = 2
HELP_TEXT_INDENT = 12


class ArgumentParser:
    def __init__(self) -> None:
        self.logging_level: int = c.LOGGING_LEVEL
        self.args: List[str] = sys.argv
        self.n_reps: int = -1
        self.players: List[Player] = []
        self.flags: List[Flag] = FLAGS

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
            if arg in ["-h", "--help"]:
                self.printHelp()
                # Note that here we exit with code 0, compared to when no arguments are passed
                # in which case the exit code is 1
                sys.exit(0)
            else:
                for flag in self.flags:
                    if arg in flag.aliases:
                        flag.set = True
                        if flag.value_after > 0:
                            # Try to convert the value that was passed after the flag to the specified type `flag.value_after_type`
                            try:
                                flag.value = flag.value_after_type(
                                    self.args[i + 1])
                                skip_arg = True
                            except (IndexError, ValueError):
                                # If value_after is 2, a value must follow the flag
                                if flag.value_after == 2:
                                    print(f"Flag `{arg}` must be followed by a value of type {flag.value_after_type.__name__}.")
                                    print(f"Help for `{arg}`: {flag.help_str}")
                                    exit(1)
                        # Found flag, leave loop
                        break
                else:
                    print(f"Unexpected command line argument \"{arg}\"")
                    sys.exit(1)

    def getFlag(self, name):
        try:
            return next(filter(lambda flag: flag.name == name, self.flags))
        except StopIteration:
            raise ValueError(f"Unknown flag `{name}`")

    @staticmethod
    def printHelp():
        lines = []
        lines.append((USAGE, 0))
        lines.append(("", 0))
        lines.append(("Options are:", 0))
        lines.append(("", 0))
        alias_strs = [flag.help_alias or ", ".join(
            flag.aliases) for flag in FLAGS]
        help_pos = HELP_TEXT_INDENT * INDENT
        ind = 1
        for flag, alias in zip(FLAGS, alias_strs):
            alias_len = len(alias) + ind * INDENT
            if not flag.hidden:
                if alias_len > help_pos - HELP_TEXT_BORDER:
                    lines.append((alias, ind))
                    lines.append((flag.help_str, HELP_TEXT_INDENT))
                else:
                    lines.append(
                        (alias + " " * (help_pos - alias_len) + flag.help_str, ind))

        lines = breakLines(lines, MAX_LINE_LEN)
        for line, ind in lines:
            printIndented(line, ind)


def breakLines(lines, max_len):
    """Split the given input of lines so that each line's length is less than max_len"""
    i = 0
    while i < len(lines):
        line, ind = lines[i]
        if ind * INDENT + len(line) > max_len:
            # Split current line across multiple lines
            lines.pop(i)
            # Additional indent is applied to all lines except the first
            additional_indent = 0
            while line:
                total_len = 0
                col = findPred(line, 0, lambda x: not x.isspace())
                while col < len(line):
                    col_end = findPred(line, col + 1, lambda x: x.isspace())
                    if col_end > max_len:
                        break
                    else:
                        total_len = col_end
                    col = findPred(line, col_end + 1,
                                   lambda x: not x.isspace())
                lines.insert(i, (line[:total_len], ind + additional_indent))
                line = line[col:]
                additional_indent = 1
                i += 1
        i += 1
    return lines


def printIndented(text, n_indents):
    # <Space> * <Spaces per indent> * <Number of indents>
    print(" " * (INDENT * n_indents) + text)


def findPred(text, start, pred):
    """Return the position of the first char of the given str that satisfies the predicate"""
    for i in range(start, len(text)):
        if pred(text[i]):
            return i
    return len(text)
