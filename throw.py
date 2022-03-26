from __future__ import annotations  # Notwendig für type hints die, die eigene Klasse beinhalten

import constants as c


class ThrowOutOfBounds(Exception):
    """Raised when addition/substraction of Throw and int leads to an impossible value.

    Possible values are only those between the lowest throw of 31 and the highest, which is Mäxchen.
    """
    pass


class Throw:
    """Represents the result of a dice throw"""
    # The integer value that is formed by according to Mäxchen rules
    value: int
    # Used to compare two Throws
    rank: int
    is_double: bool
    is_maexchen: bool

    def __init__(self, *args: int) -> None:
        if len(args) == 1:
            # Got one argument -> must be the value of the Throw
            self.value = args[0]
            if self.value not in c.THROW_VALUES:
                raise ValueError(f"Got invalid value for initializing Throw: {self.value}.")
            num0 = self.value // 10
            num1 = self.value % 10
        elif len(args) == 2:
            # Got two arguments -> must be the results of two individual dice throws
            num0, num1 = args
            if not 1 <= num0 <= 6 and 1 <= num1 <= 6:
                raise ValueError("Values must be elements of [1, 6].")
            self.value = max(num0, num1) * 10 + min(num0, num1)
        else:
            raise TypeError(f"Throw() takes either one or two arguments, got {len(args)}")

        self.rank = c.THROW_RANK_BY_VALUE[self.value]
        self.is_double = num0 == num1  # Pasch
        self.is_maexchen = self.value == c.MAEXCHEN  # Mäxchen

    def __str__(self) -> str:
        return str(self.value)

    def __repr__(self) -> str:
        return f"Throw (value={self.value})"

    def __eq__(self, other: object) -> bool:
        """Evaluate equality with Throw or int.
        
        If other is of type int, self.value is compared to it
        If it is a Throw instance, self.rank is compared to other.rank.

        :param other: Object to compare"""
        if isinstance(other, Throw):
            return self.rank == other.rank
        elif isinstance(other, int):
            return other == self.value
        else:
            return False

    def __gt__(self, other: Throw) -> bool:
        """Check if another Throw is of a higher rank

        :param other: Throw to compare"""
        if not isinstance(other, Throw):
            return False
        return self.rank > other.rank

    def __lt__(self, other: Throw) -> bool:
        """Check if another Throw is of a lower rank

        :param other: Throw to compare"""
        if not isinstance(other, Throw):
            return False
        return self.rank < other.rank

    def __ge__(self, other: Throw) -> bool:
        """Check if another Throw is of a greater or equal rank

        :param other: Throw to compare"""
        # a !< b  <=>  a >= b
        return not self < other

    def __le__(self, other: Throw) -> bool:
        """Check if another Throw is of a lower or equal rank

        :param other: Throw to compare"""
        if not isinstance(other, Throw):
            return False
        # a !> b  <=>  a <= b
        return not self > other

    def __add__(self, other: int) -> Throw:
        """Return the n'th next Throw.  
        Raise ThrowOutOfBounds if such a Throw does not exist.
        An example for such a case would be Throw(21) + 1.

        :param other: Offset n by which the returned Throw's is greater than self.rank"""
        if not isinstance(other, int):
            return False
        newRank = self.rank + other
        if 0 <= newRank < len(c.THROW_VALUES):
            return Throw(c.THROW_VALUES[newRank])
        else:
            raise ThrowOutOfBounds

    def __sub__(self, other: int) -> Throw:
        """Return the n'th next lowest Throw .
        Raise ThrowOutOfBounds if such a Throw does not exist.
        An example for such a case would be Throw(31) - 1.

        :param other: Offset by which the returned Throw's is lower than self.rank"""
        return self.__add__(-other)


class NoneThrow(Throw):
    """Placeholder for a Throw that has no information"""
    def __init__(self):
        self.value = 0
        self.rank = -1 
        self.is_maexchen = False
        self.is_double = False

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
    """Return a Throw with the given rank"""
    return Throw(c.THROW_VALUES[rank])
