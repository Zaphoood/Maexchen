import constants as c
from throw import Throw


class Move:
    # Klasse die einen Zug beschreibt, der von einem Spieler durchgeführt wird
    move: c.ALL_MOVES
    value: Throw

    def __init__(self, move: c.ALL_MOVES, value: Throw = None):
        self.move = move  # Art des Zuges die dieser Zug darstellt (DOUBT oder THROW)
        self.value = value  # Wird nur für Züge verwendet, bei denen der Spieler würfelt.
        # Beinhaltet die Angabe des Spielers über das Würfelergebnis


class MoveDoubt(Move):
    # Klasse die eine Zug darstellt, bei dem das vorherige Ergebnis angezweifelt wird
    move: c.ALL_MOVES
    value: Throw

    def __init__(self, move: c.ALL_MOVES):
        super().__init__(c.ALL_MOVES.DOUBT, None)


class MoveThrow(Move):
    # Klasse die eine Zug darstellt, bei dem gewürfelt wird
    move: c.ALL_MOVES
    value: Throw

    def __init__(self, move: c.ALL_MOVES, value: Throw = None):
        super().__init__(c.ALL_MOVES.THROW, value)
