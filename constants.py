from logging import WARN

LOG_PATH = "results.log"
LOGGING_LEVEL = WARN  # logging.WARN
TIME_FORMAT = "%Y-%m-%d %H:%M:%S"

MAEXCHEN = 21
# All possible values of a two-dice throw according to Mäxchen rules, ordered by their rank
THROW_VALUES = [31, 32, 41, 42, 43, 51, 52, 53, 54, 61, 62, 63, 64, 65, 11, 22, 33, 44, 55, 66, 21]
# Number of possible values
N_THROW_VALUES = len(THROW_VALUES)
# Map values to their ranks. This is a frequent operation, so the ranks are pre-calucalted
# instead of calling THROW_VALUES.index() when needed
THROW_RANK_BY_VALUE = {val: rank for rank, val in enumerate(THROW_VALUES)}

# Width of the progress bar in characters
PROGRESS_BAR_WIDTH = 20
