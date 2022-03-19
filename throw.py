from __future__ import annotations  # Notwendig für type hints die, die eigene Klasse beinhalten

import constants as c


class OutOfBoundsError(Exception):
    """Wird gemeldet, wenn eine Addition von Throw und int zu einem nicht definierten Wert
    führen würde (z. B. größer als Mäxchen, kleiner als 31)"""
    pass


class Throw:
    """Stellt ein Würfelergebnis dar."""
    value: int  # Das Zahlergebnis, das der Wurf repräsentiert
    rank: int
    isDouble: bool
    isMaexchen: bool

    def __init__(self, *args: int) -> None:
        if len(args) == 1:
            # Ein Argument wurde gegeben, also der Wert des Wurfs (self.value)
            self.value = args[0]
            if self.value not in c.THROW_VALUES:
                raise ValueError(f"Got invalid value for initializing Throw: {self.value}.")
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
        return f"Throw {self.value}"

    def __repr__(self) -> str:
        return f"Throw (value={self.value})"

    def __eq__(self, other: object) -> bool:
        """Evaluate equality with Throw or int.
        
        If other is of type int, self.value is compared to it, if it is a
        Throw instance, self.rank is compared to other.rank.

        :param other: Object to compare"""
        if isinstance(other, Throw):
            return self.rank == other.rank
        elif isinstance(other, int):
            return other == self.value
        else:
            return False

    def __gt__(self, other: Throw) -> bool:
        """Überprüfen, ob eine anderer Throw von höherem Rang ist

        :param other: Zu vergleichender Throw"""
        if not isinstance(other, Throw):
            return False
        return self.rank > other.rank

    def __lt__(self, other: Throw) -> bool:
        """Überprüfen, ob eine anderer Throw von niedrigerem Rang ist

        :param other: Zu vergleichender Throw"""
        if not isinstance(other, Throw):
            return False
        return self.rank < other.rank

    def __ge__(self, other: Throw) -> bool:
        """Überprüfen, ob eine anderer Throw von höherem oder gleichen Rang ist

        :param other: Zu vergleichender Throw"""
        # a !< b  <=>  a >= b
        return not self < other

    def __le__(self, other: Throw) -> bool:
        """Überprüfen, ob eine anderer Throw von niedrigerem oder gleichen Rang ist

        :param other: Zu vergleichender Throw"""
        if not isinstance(other, Throw):
            return False
        # a !> b  <=>  a <= b
        return not self > other

    def __add__(self, other: int) -> Throw:
        """Gibt das nte nächstgrößere Wurfergebnis zurück.
        Meldet OutOfBoundsError, sollte dieses Ergebnis nicht existieren.

        :param other: Um wie viel der Rang des zurückgegebenen Throws größer ist als der Rang von self"""
        if not isinstance(other, int):
            return False
        newRank = self.rank + other
        if 0 <= newRank < len(c.THROW_VALUES):
            return Throw(c.THROW_VALUES[newRank])
        else:
            raise OutOfBoundsError

    def __sub__(self, other: int) -> Throw:
        """Gibt das nte nächstniedrigere Wurfergebnis zurück.
        Meldet OutOfBoundsError, sollte dieses Ergebnis nicht existieren.

        :param other: Um wie viel der Rang des zurückgegebenen Throws kleiner ist als der Rang von self"""
        return self.__add__(-other)


class NoneThrow(Throw):
    """Placeholder for a Throw that has no information"""
    def __init__(self):
        self.value = 0
        self.rank = -1 
        self.isMaexchen = False
        self.isDouble = False

    def __str__(self):
        return "NoneThrow"

    def __repr__(self):
        return "<NoneThrow>"

    def __eq__(self, other: object):
        return isinstance(other, self.__class__)

    def __lt__(self, other: object):
        raise Exception("Cannot compare NoneThrow")

    def __gt__(self, other: object):
        raise Exception("Cannot compare NoneThrow")

    def __le__(self, other: object):
        raise Exception("Cannot compare NoneThrow")

    def __ge__(self, other: object):
        raise Exception("Cannot compare NoneThrow")

    def __add__(self, other: object):
        raise Exception("Cannot perform arithmetics on NoneThrow")

    def __sub__(self, other: object):
        raise Exception("Cannot perform arithmetics on NoneThrow")


def throwByRank(rank: int) -> Throw:
    """Erzeugt ein Throw-Objekt, das den angegebenen Rang hat"""
    return Throw(c.THROW_VALUES[rank])
