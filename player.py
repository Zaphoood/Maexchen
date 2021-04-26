import constants
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
        pass

class DummyPlayer(Player):
    def __init__(self):
        super().__init__(self)

    def getMove(self, myThrow: Throw, lastThrow: Throw) -> Move:
        if myThrow > lastThrow:
            return Move(constants.ALL_MOVES)
