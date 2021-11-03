from logging import WARN

LOG_PATH = "results.log"
TIME_FORMAT = "%Y-%m-%d %H:%M:%S"

MAEXCHEN = 21

# Alle möglichen Ergebnisse für einen Wurf (mit der höheren Zahl als erste Stelle),
# geordnet nach ihrem Rang ([31, 32, ..., 65, 11, 22, ..., 66, 21])
THROW_VALUES = [
    *[i * 10 + j for i in range(3, 7) for j in range(1, i)],  # "Normale" Würfe
    *[i * 10 + i for i in range(1, 7)],  # Päsche
    MAEXCHEN
]
# Weist jedem Wurfergebnisses einen Rang zu
THROW_RANK_BY_VALUE = {val: rank for rank, val in enumerate(THROW_VALUES)}

LOGGING_LEVEL = WARN  # logging.WARN
EVAL_PRG_STEPS = 20  # Genauigkeit der Fortschrittsanzeige beim Durchführen der Simulation 

START_SIM_USAGE = """Usage: python3.10 run_sim.py [NUMBER-OF-ITERATIONS] [OPTIONS]

    The number of the times the simulation will be run can be specified with NUMBER-OF-ITERATIONS

Options:
    -v                  Enable verbose output
    -p                  Show progress bar
    --player-class [n]  Add (n) Player(s) to simulation. Possible values for player-class:
        dummy, random, show-off, prob[abilistic]"""
