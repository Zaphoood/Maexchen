from gameevent import Event, EventAbort
from player import Player


class GameLog:
    rounds: list[list[Event]]
    players: list[Player]
    n_players: int  # Gesamtanzahl der Spieler zu Beginn des Spiels

    def __init__(self):
        self.rounds = []
        self.players = []
        self.n_players = 0

    def init(self):
        self.n_players = len(self.players)

    def happen(self, event):
        if not self.rounds:
            self.newRound()

        self.rounds[-1].append(event)

    def newRound(self):
        self.rounds.append([])

    def pretty(self):
        prettyStr = f"Game initialized with {self.n_players}\n"
        for i, round in enumerate(self.rounds):
            prettyStr += f"=== Round {i} ===\n"
            for event in round:
                prettyStr += f"{str(event)}\n"

        if not isinstance(self.rounds[-1][-1], EventAbort):
            prettyStr += f"Game finished regularly.\n"

        return prettyStr
