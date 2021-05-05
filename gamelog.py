from gameevent import Event, EventThrow, EventDoubt, EventLeave
from player import Player


class GameLog:
    rounds: list[list[Event]]
    players: list[Player]

    def __init__(self):
        pass
