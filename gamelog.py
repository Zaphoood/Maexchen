from __future__ import annotations  # Notwendig für type hints die die eigene Klasse beinhalten
import contextlib
import copy

from gameevent import Event, EventFinish, EventAbort
from player import Player


class GameLog:
    rounds: list[list[Event]]
    players: list[Player]
    n_players: int  # Gesamtanzahl der Spieler zu Beginn des Spiels

    def __init__(self, players: list[Player] = []):
        # Player-Liste kopieren, damit Player-Instanzen erhalten bleiben
        # wenn Player-Instanzen in Game() verändert werden
        self.players = [copy.copy(p) for p in players]
        self.n_players = len(players)
        self.rounds = []

    def happen(self, event):
        if not self.rounds:
            self.newRound()

        self.rounds[-1].append(event)

    def newRound(self):
        self.rounds.append([])

    def prettyList(self):
        # Output is stored as a list of strings
        prettyList = [f"=== Game initialized with {self.n_players} player{'s' if self.n_players > 1 else ''}: ==="]
        prettyList.extend([f" - {str(player)}" for player in self.players])
        for i, round in enumerate(self.rounds):
            for event in round:
                prettyList.append(f"[Round {i}] {str(event)}")

        # Check whether the game has finished yet
        ongoing = True
        with contextlib.suppress(IndexError):
            if isinstance(self.rounds[-1][-1], (EventFinish, EventAbort)):
                ongoing = False
        if ongoing:
            prettyList.append("(Game is still ongoing)")

        return prettyList

    def pretty(self):
        # Join return value from prettyList() to make a string
        return "\n".join(self.prettyList())

    def __eq__(self, other: GameLog) -> bool:
        if not isinstance(other, GameLog):
            raise NotImplementedError
        return self.players == other.players and self.n_players == other.n_players and self.rounds == other.rounds
