from __future__ import annotations  # Notwendig für type hints die die eigene Klasse beinhalten
import contextlib
import copy

from gameevent import Event, EventFinish, EventAbort
from player import Player


class GameLog:
    rounds: list[list[Event]]
    players: list[Player]
    n_players: int  # Gesamtanzahl der Spieler zu Beginn des Spiels

    def __init__(self, players: list[Player] = None):
        players = [] if players is None else players
        # Player-Liste kopieren, damit Player-Instanzen erhalten bleiben
        # wenn Player-Instanzen in Game() verändert werden
        self.players = [copy.copy(p) for p in players]
        self.n_players = len(players)
        self.rounds = []

    def happen(self, event):
        """Ein neues Ereignis zum Log hinzufügen"""
        if not self.rounds:
            self.newRound()
        self.rounds[-1].append(event)

    def newRound(self):
        self.rounds.append([])

    def prettyList(self) -> list[str]:
        """Den Ablauf des Spiels schön formatiert als Liste von strings zurückgeben"""

        prettyList = [f"=== Game initialized with {self.n_players} player{'s' if self.n_players > 1 else ''}: ==="]
        prettyList.extend([f" - {str(player)}" for player in self.players])
        for i, round in enumerate(self.rounds):
            for event in round:
                prettyList.append(f"[Round {i}] {str(event)}")

        # Überprüfen, ob das Spiel noch im Gange ist
        if not self.hasFinished():
            prettyList.append("(Game is still ongoing)")

        return prettyList

    def hasFinished(self):
        """Gibt zurück, ob das Spiel, zu dem dieser GameLog gehört, (ordnungsgemäß) beendet wurde"""

        with contextlib.suppress(IndexError):
            return isinstance(self.rounds[-1][-1], (EventFinish, EventAbort))
        return False

    def pretty(self) -> str:
        """Den von prettyList() Spielablauf als string zurückgeben"""

        return "\n".join(self.prettyList())

    def getEvents(self) -> list[Event]:
        """Alle Ereignisse des Spiels in einer flachen Liste zurückgeben"""

        return [event for round in self.rounds for event in round]

    def countRounds(self) -> int:
        """Gibt die Anzahl der Runden des Spiels an."""
        return len(self.rounds)

    def __eq__(self, other: GameLog) -> bool:
        if not isinstance(other, GameLog):
            raise NotImplementedError
        return self.players == other.players and self.n_players == other.n_players and self.rounds == other.rounds
