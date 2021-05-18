from __future__ import annotations  # Notwendig für type hints die die eigene Klasse beinhalten

import constants as c


class OutOfBoundsError(Exception):
    """Wird gemeldet, wenn eine Addition von Throw und int zu einem nicht definierten Wert
    führen würde (z. B. größer als Mäxchen, kleiner als 31)"""
    pass


class Throw:
    """Stellt ein Würfelergebnis dar."""
    value: int
    rank: int
    isDouble: bool
    isMaexchen: bool

    def __init__(self, *args: int) -> None:
        if len(args) == 1:
            # Ein Argument wurde gegeben, also der Wert des Wurfs (self.value)
            self.value = args[0]
            if self.value not in c.THROW_VALUES:
                raise ValueError(f"Value of {self.value} is not valid.")
            num0 = self.value // 10
            num1 = self.value % 10
        elif len(args) == 2:
            # Zwei Argumente wurden gegeben, i.e. die Ergebnisse der einzelnen Würfel
            num0, num1 = args
            if not 1 <= num0 <= 6 and 1 <= num1 <= 6:
                raise ValueError("Values must be elements of [1, 6].")
            self.value = max(num0, num1) * 10 + min(num0, num1)
        else:
            # Ungültige Anzahl an Argumenten
            raise TypeError(f"Throw() takes either one or two arguments, got {len(args)}")

        self.rank = c.THROW_RANK_BY_VALUE[self.value]
        self.isDouble = num0 == num1  # Pasch
        self.isMaexchen = self.value == c.MAEXCHEN  # Mäxchen

    def __str__(self) -> str:
        return str(self.value)

    def __repr__(self) -> str:
        return f"Throw (value={self.value})"

    def __eq__(self, other: Throw) -> bool:
        # Ist von gleichem Rang
        return self.rank == other.rank

    def __ge__(self, other: Throw) -> bool:
        # Ist von größerem oder gleichem Rang
        return self.rank >= other.rank

    def __gt__(self, other: Throw) -> bool:
        # Ist von größerem Rang
        return self.rank > other.rank

    def __le__(self, other: Throw) -> bool:
        # Ist von kleinerem oder gleichen Rang
        return self.rank <= other.rank

    def __lt__(self, other: Throw) -> bool:
        # Ist von kleinerem Rang
        return self.rank < other.rank

    def __add__(self, other: int) -> Throw:
        """Gibt das nte nächstgrößere Wurfergebnis zurück. n ist als Parameter other gegeben.
        Meldet OutOfBoundsError, sollte dieses Ergebnis nicht existieren."""
        assert isinstance(other, int)
        newRank = self.rank + other
        if 0 <= newRank < len(c.THROW_VALUES):
            return Throw(c.THROW_VALUES[newRank])
        else:
            raise OutOfBoundsError

    def __sub__(self, other: int) -> Throw:
        return self.__add__(-other)
