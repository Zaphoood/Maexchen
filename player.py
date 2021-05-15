import random

import constants as c
from throw import Throw


class Player:
    id: int  # Identification number that is unique among all players in one Game

    def __init__(self, id: int = None):
        self.id = id

    def __str__(self):
        return f"{self.__class__.__name__} with id {self.id}"

    def __repr__(self):
        return f"<{self.__class__.__name__} (id={self.id})>"

    def __eq__(self, other):
        if not isinstance(other, Player):
            raise NotImplementedError
        return isinstance(other, self.__class__) and self.id == other.id

    def getDoubt(self, lastThrow: Throw) -> bool:
        """Fragt den Spieler, ob er dem Wurf seines Vorgängers vertraut"""
        raise NotImplementedError

    def getThrowStated(self, myThrow: Throw, lastThrow: Throw) -> Throw:
        """Gibt basierend auf dem Wurf dieses Spielers myThrow das Würfelergebnis zurück, das der Spieler verkündet.

        Das angegebene Ergebnis muss nicht der Wahrheit entsprechen. Der eigene Wurf wird zuvor vom Spiel (Game)
        zufällig gewählt und dieser Funktion übergeben. Die Funktion muss None als Wert für lastThrow akzeptieren
        können."""
        raise NotImplementedError


class DummyPlayer(Player):
    """Sehr grundlegende Spielerklasse. Kann das eigene Ergebnis den Vorgänger
    überbieten, wird dieses angegeben. Kann es das nicht, wird ein falsches Ergebnis verkündet"""

    def __init__(self, id: int = None) -> None:
        super().__init__(id)

    def getDoubt(self, lastThrow: Throw) -> bool:
        if lastThrow.isMaexchen:
            return True
        else:
            return False

    def getThrowStated(self, myThrow: Throw, lastThrow: Throw) -> Throw:
        if lastThrow is None:
            # Erste Runde
            return myThrow
        else:
            if myThrow > lastThrow:
                # Vorgänger kann überboten werden -> Wahrheitsgemäße Antwort machen
                return myThrow
            else:
                # Vorgänger kann kein Mäxchen gehabt haben, sonst wäre er angezweifelt worden
                # Lügen und nächsthöheres Würfelergebnis angeben
                return lastThrow + 1


class ShowOffPlayer(Player):
    """Angeber-Spielerklasse.

    Gibt immer an, einen Pasch oder Mäxchen gewürfelt zu haben, es sei denn, der Vorgänger hat
    Mäxchen gewürfelt"""

    def __init__(self, id=None) -> None:
        super().__init__(id)

    def getDoubt(self, lastThrow: Throw) -> bool:
        if lastThrow.isMaexchen:
            return True
        else:
            return False

    def getThrowStated(self, myThrow: Throw, lastThrow: Throw) -> Throw:
        """Generiert zufällig ein Pasch oder Mäxchen, um den vorherigen Wurf zu überbieten"""
        rank_11 = c.THROW_RANK_BY_VALUE[11]
        if lastThrow is None:
            return Throw(random.choice(c.THROW_VALUES[rank_11:]))
        else:
            return Throw(random.choice(c.THROW_VALUES[max(lastThrow.rank + 1, rank_11):]))
