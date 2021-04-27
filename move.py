from __future__ import annotations  # Notwendig für type hints die die eigene Klasse beinhalten

import constants as c
from throw import Throw


class Move:
    # Klasse die einen Zug beschreibt, der von einem Spieler durchgeführt wird
    move: c.ALL_MOVES
    value: Throw

    def __init__(self, move: c.ALL_MOVES, value: Throw = None) -> None:
        self.move = move  # Art des Zuges die dieser Zug darstellt (DOUBT oder THROW)
        self.value = value  # Wird nur für Züge verwendet, bei denen der Spieler würfelt.
        # Beinhaltet die Angabe des Spielers über das Würfelergebnis

    def __eq__(self, other: Move) -> bool:
        return self.move == other.move and self.value == other.value


class MoveDoubt(Move):
    # Klasse die eine Zug darstellt, bei dem das vorherige Ergebnis angezweifelt wird
    move: c.ALL_MOVES
    value: Throw

    def __init__(self) -> None:
        super().__init__(c.ALL_MOVES.DOUBT)


class MoveThrow(Move):
    # Klasse die eine Zug darstellt, bei dem gewürfelt wird
    move: c.ALL_MOVES
    value: Throw

    def __init__(self, value: Throw) -> None:
        super().__init__(c.ALL_MOVES.THROW, value)
