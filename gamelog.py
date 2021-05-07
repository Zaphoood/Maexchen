import contextlib

from gameevent import Event, EventFinish, EventAbort
from player import Player


class GameLog:
    rounds: list[list[Event]]
    players: list[Player]
    n_players: int  # Gesamtanzahl der Spieler zu Beginn des Spiels

    def __init__(self, players: list[Player] = []):
        self.players = players
        self.n_players = len(players)
        self.rounds = []

    def happen(self, event):
        if not self.rounds:
            self.newRound()

        self.rounds[-1].append(event)

    def newRound(self):
        self.rounds.append([])

    def pretty(self):
        prettyList = [f"=== Game initialized with {self.n_players} player{'s' if self.n_players > 1 else ''}: ==="]
        prettyList.extend([f" - {str(player)}" for player in self.players])
        for i, round in enumerate(self.rounds):
            prettyList.append(f"== Round {i} ==")
            for event in round:
                prettyList.append(f"{str(event)}")

        ongoing = True
        with contextlib.suppress(IndexError):
            if isinstance(self.rounds[-1][-1], (EventFinish, EventAbort)):
                ongoing = False
        if ongoing:
            prettyList.append("(Game is still ongoing)")

        return "\n".join(prettyList)
