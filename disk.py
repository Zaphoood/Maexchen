import time
from os.path import exists, split

from collections import Counter
import constants as c
from player import Player

def writeLog(t_start: float, players: list[Player], n_repetitions: int, results: str, log_path=None) -> None:
    log_path = log_path or c.LOG_PATH
    players_counted = Counter([player.__class__.__name__ for player in players])
    time_formatted = time.strftime(c.TIME_FORMAT, time.localtime(t_start))

    to_write = time_formatted + "\n"
    to_write += f"n_repetitions: {n_repetitions}\n"
    to_write += "players:\n"
    for p_name in players_counted:
        to_write += f"  {p_name} x {players_counted[p_name]}\n"
    to_write += "results:\n"
    to_write += results + "\n\n"

    with open(log_path, "a") as log_file:
        log_file.write(to_write)

def existsPathToFile(path: str) -> bool:
    # os.path.split
    head, tail = split(path)
    # os.path.exists 
    return not head or exists(head)
