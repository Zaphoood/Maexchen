from enum import Enum

MAEXCHEN = 21

# Alle möglichen Ergebnisse für einen Wurf (mit der höheren Zahl als erste Stelle),
# geordnet nach ihrem Rang ([31, 32, ..., 65, 11, 22, ..., 66, 21])
THROW_VALUES = [
    *[i * 10 + j for i in range(3, 7) for j in range(1, i)],  # "Normale" Würfe
    *[i * 10 + i for i in range(1, 7)],  # Päsche
    21  # Mäxchen
]
# Weist jedem Wurfergebnisses einen Rang zu
THROW_RANK_BY_VALUE = {val: rank for rank, val in enumerate(THROW_VALUES)}


# TODO: Move this enum to move.py
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

