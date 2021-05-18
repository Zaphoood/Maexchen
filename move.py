from __future__ import annotations  # Notwendig für type hints die die eigene Klasse beinhalten
from enum import Enum

from throw import Throw


class ALL_MOVES(Enum):
    """Alle möglichen Arten von Zügen die ein Spieler durchführen kann

    Mögliche Werte sind
    -DOUBT: Das Ergebnis des vorherigen Spielers anzweifeln
    -THROW: Würfeln und das Ergebnis verkünden (Die Möglichkeit des Lügens ist hier beinhaltet)
    """

    DOUBT = 0
    THROW = 1

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}.{self._name_}"

    def __str__(self):
        return f"{self._name_}"


class Move:
    """Klasse die einen Zug beschreibt, der von einem Spieler durchgeführt wird"""

    move: ALL_MOVES
    value: Throw

    def __init__(self, move: ALL_MOVES, value: Throw = None) -> None:
        self.move = move  # Art des Zuges die dieser Zug darstellt (DOUBT oder THROW)
        self.value = value  # Wird nur für Züge verwendet, bei denen der Spieler würfelt.
        # Beinhaltet die Angabe des Spielers über das Würfelergebnis

    def __eq__(self, other: Move) -> bool:
        return self.move == other.move and self.value == other.value
