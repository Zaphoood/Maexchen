import random

import constants as c
from throw import Throw
from move import Move


class Player:
    def __init__(self):
        pass

    def getMove(self, myThrow: Throw, lastThrow: Throw) -> Move:
        # Gibt basierend auf dem Wurf dieses Spielers myThrow
        # und dem des vorherigen Spielers lastThrow einen Zug (Move)
        # zurück. Der eigene Wurf wird zuvor vom Spiel (Game) zufällig gewählt
        # und dieser Funktion übergeben
        raise NotImplementedError


class DummyPlayer(Player):
    """Sehr grundlegende Spielerklasse. Kann das eigene Ergebnis den Vorgänger
    überbieten, wird dieses angegeben. Kann es das nicht, wird der Vorgänger
    entweder angezweifelt oder ein falsches Ergebnis verkündet"""

    def __init__(self) -> None:
        super().__init__()

    def getMove(self, myThrow: Throw, lastThrow: Throw) -> Move:
        if lastThrow is None:
            return Move(c.ALL_MOVES.THROW, myThrow)
        else:
            if myThrow > lastThrow:
                return Move(c.ALL_MOVES.THROW, myThrow)
            else:
                if not lastThrow.isMaexchen:
                    # Vorgänger hatte kein Mäxchen -> Ergebnis kann überboten werden
                    return random.choice([Move(c.ALL_MOVES.THROW, value=lastThrow + 1), Move(c.ALL_MOVES.DOUBT)])
                else:
                    # Vorgänger hatte Mäxchen -> Immer anzweifeln
                    return Move(c.ALL_MOVES.DOUBT)


class ShowOffPlayer(Player):
    """Angeber-Spielerklasse.

    Gibt immer an, einen Pasch oder Mäxchen gewürfelt zu haben, es sei denn, der Vorgänger hat
    Mäxchen gewürfelt"""

    def __init__(self) -> None:
        super().__init__()

    def getMove(self, myThrow: Throw, lastThrow: Throw) -> Move:
        if lastThrow.isMaexchen:
            # Mäxchen kann nicht überboten werden, deswegen anzweifeln
            return Move(c.ALL_MOVES.DOUBT)
        else:
            # Zufälligen Pasch oder Mäxchen generieren, der besser als der Wurf des Vorgängers ist
            rank_11 = c.THROW_RANK_BY_VALUE[11]
            return Move(c.ALL_MOVES.THROW, Throw(random.choice(c.THROW_VALUES[max(lastThrow.rank + 1, rank_11):])))
