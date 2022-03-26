# Necessary for type hints of methods that include their own class
from __future__ import annotations
from typing import Optional, List
from contextlib import suppress
import copy

from gameevent import Event, EventFinish, EventAbort
from player import Player


# One move consists of multiple Events
# An Event is considered part of a new move if it is performed
# by a different Playe than the last one, e. g.
#
# Move 0:
#   Player 0 throws 55, says 66
# Move 1:
#   Player 1 doubts
#   Player 0 is kicked
#   Player 1 throws 45, says 45
# Move 2:
#   Player 2 doesn't doubt
#   ...
Move = List[Event]

class GameLog:
    players: list[Player]
    moves: list[Move]
    # Number of players at the start of the game
    n_players: int
    # ID of the player who wins the game
    winner_id: Optional[int]

    def __init__(self, players: list[Player] = None):
        # Copy list of players since they may be changed by Game
        self.players = [copy.copy(p) for p in players] if players else []
        self.moves = []
        self.n_players = len(self.players)
        self.winner_id = None

    def happen(self, event):
        """Append a new event to the log"""
        if not self.moves:
            self.newRound()
        self.moves[-1].append(event)

        if isinstance(event, EventFinish):
            self.winner_id = event.player_id

    def newRound(self):
        self.moves.append([])

    def pretty(self) -> str:
        """Return the log in a human-readable format"""
        # Correct plurals are important ;)
        lines = []
        player_s = "player" if self.n_players == 1 else "players"
        lines.append(f"=== Game initialized with {self.n_players} {player_s}: ===")
        for player in self.players:
            lines.append(f" - {player!s}")
        for i, move in enumerate(self.moves):
            for event in move:
                lines.append(f"[Round {i}] {event!s}")

        if not self.hasFinished():
            lines.append("Note: Game has not finished.")

        return "\n".join(lines)

    def hasFinished(self):
        """Determine whether the Game that this log corresponds to has finished"""
        with suppress(IndexError): # contextlib.suppress
            return isinstance(self.moves[-1][-1], (EventFinish, EventAbort))
        return False

    def getEvents(self) -> list[Event]:
        """Alle Ereignisse des Spiels in einer flachen Liste zurückgeben"""
        return [event for move in self.moves for event in move]

    def countRounds(self) -> int:
        """Gibt die Anzahl der Runden des Spiels an."""
        return len(self.moves)

