from __future__ import annotations  # Notwendig für type hints, die die eigene Klasse beinhalten
from typing import Optional, Set
import contextlib
import copy

from gameevent import Event, EventFinish, EventAbort
from player import Player


class GameLog:
    players: list[Player]
    moves: list[list[Event]]  # Ein Zug besteht aus mehreren Ereignissen
    n_players: int  # Gesamtanzahl der Spieler zu Beginn des Spiels

    winner_id: Optional[int]  # ID des Siegers des Spiels

    def __init__(self, players: list[Player] = None):
        players = [] if players is None else players
        # Player-Liste kopieren, damit Player-Instanzen erhalten bleiben
        # wenn Player-Instanzen in Game() verändert werden
        self.players = [copy.copy(p) for p in players]
        self.moves = []
        self.n_players = len(players)

        self.winner_id = None

    def happen(self, event):
        """Ein neues Ereignis zum Log hinzufügen"""
        if not self.moves:
            self.newRound()
        self.moves[-1].append(event)

        if isinstance(event, EventFinish):
            self.winner_id = event.player_id

    def newRound(self):
        self.moves.append([])

    def prettyList(self) -> list[str]:
        """Den Ablauf des Spiels schön formatiert als Liste von strings zurückgeben"""

        prettyList = [f"=== Game initialized with {self.n_players} player{'s' if self.n_players > 1 else ''}: ==="]
        prettyList.extend([f" - {str(player)}" for player in self.players])
        for i, move in enumerate(self.moves):
            for event in move:
                prettyList.append(f"[Round {i}] {str(event)}")

        # Überprüfen, ob das Spiel noch im Gange ist
        if not self.hasFinished():
            prettyList.append("(Game is still ongoing)")

        return prettyList

    def hasFinished(self):
        """Gibt zurück, ob das Spiel, zu dem dieser GameLog gehört, (ordnungsgemäß) beendet wurde"""

        with contextlib.suppress(IndexError):
            return isinstance(self.moves[-1][-1], (EventFinish, EventAbort))
        return False

    def pretty(self) -> str:
        """Den von prettyList() Spielablauf als string zurückgeben"""

        return "\n".join(self.prettyList())

    def getEvents(self) -> list[Event]:
        """Alle Ereignisse des Spiels in einer flachen Liste zurückgeben"""
        return [event for move in self.moves for event in move]

    def countRounds(self) -> int:
        """Gibt die Anzahl der Runden des Spiels an."""
        return len(self.moves)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, GameLog):
            return self.players == other.players and self.n_players == other.n_players and self.moves == other.moves
        else:
            return False
