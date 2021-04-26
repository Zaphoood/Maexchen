import constants as c


class Throw:
    num0: int
    num1: int
    value: int
    rank: int
    isDouble: bool
    isMaexchen: bool

    def __init__(self, num0, num1):
        if not 1 <= num0 <= 6 and 1 <= num1 <= 6:
            raise ValueError("Values must be elements of [1, 6].")
        self.num0 = num0
        self.num1 = num1
        self.value = max(num0, num1) * 10 + min(num0, num1)
        self.rank = c.THROW_RANK_BY_VALUE[self.value]
        self.isDouble = num0 == num1  # Pasch
        self.isMaexchen = self.value == c.MAEXCHEN  # Mäxchen

    def __repr__(self):
        return f"Throw (value={self.value})"

    def __eq__(self, other):
        # Ist von gleichem Rang
        return self.rank == other.rank

    def __ge__(self, other):
        # Ist von größerem oder gleichem Rang
        return self.rank >= other.rank

    def __gt__(self, other):
        # Ist von größerem Rang
        return self.rank > other.rank

    def __le__(self, other):
        # Ist von kleinerem oder gleichen Rang
        return self.rank <= other.rank

    def __lt__(self, other):
        # Ist von kleinerem Rang
        return self.rank < other.rank
