import random

from throw import Throw
from move import Move, MoveThrow, MoveDoubt


class Player:
    def __init__(self):
        pass

    def getMove(self, myThrow: Throw, lastThrow: Throw) -> Move:
        # Gibt basierend auf dem Wurf dieses Spielers myThrow
        # und dem des vorherigen Spielers lastThrow einen Zug (Move)
        # zurück. Der eigene Wurf wird zuvor vom Spiel (Game) zufällig gewählt
        # und dieser Funktion übergeben
        pass


class DummyPlayer(Player):
    # Sehr grundlegende Spielerklasse. Kann das eigene Ergebnis den Vorgänger
    # überbieten, wird dieses angegeben. Kann es das nicht, wird der Vorgänger
    # entweder angezweifelt oder ein falsches Ergebnis verkündet
    def __init__(self):
        super().__init__(self)

    def getMove(self, myThrow: Throw, lastThrow: Throw) -> Move:
        if myThrow > lastThrow:
            return MoveThrow
        else:
            if not lastThrow.isMaexchen:
                # Vorgänger hatte kein Mäxchen -> Ergebnis kann überboten werden
                return random.choice(MoveThrow(lastThrow + 1), MoveDoubt)