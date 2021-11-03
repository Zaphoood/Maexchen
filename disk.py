import time

from collections import Counter
import constants as c
from player import Player

def writeLog(t_start: float, players: list[Player], n_repetitions: int, results: str, log_path=c.LOG_PATH) -> None:
    player_names = [player.__class__.__name__ for player in players]
    players_counted = Counter(player_names)
    to_write = f"\n\n{time.strftime(c.TIME_FORMAT, time.localtime(t_start))} Simulation started.\n"
    to_write += f"n_repetitions = {n_repetitions}\nplayers:\n"
    to_write += "\n".join([f" - {p_name} x {players_counted[p_name]}" for p_name in players_counted])
    to_write += "\nresults:\n"
    to_write += results

    with open(log_path, "a") as log_file:
        log_file.write(to_write)

