import random
import logging

import constants as c
from throw import Throw


class Player:
    id: int  # Identification number that is unique among all players in one Game

    def __init__(self, playerId: int = None):
        self.id = playerId

    def __str__(self):
        return f"{self.__class__.__name__} with id {self.id}"

    def __repr__(self):
        return f"<{self.__class__.__name__} (id={self.id})>"

    def __eq__(self, other):
        # Falls other kein Player oder eine Unterklasse davon ist, Fehler ausgeben
        if not isinstance(other, Player):
            raise NotImplementedError
        # Überprüfen, ob other von der gleiche Klasse oder einer Unterklasse wie self ist.
        # Falls other und self Instanzen von verschiedenen Unterklassen von Player sind, wird
        # das oben nicht erkannt, deswegen hier überprüfen.
        return isinstance(other, self.__class__) and self.id == other.id

    def getDoubt(self, lastThrow: Throw, iRound: int) -> bool:
        """Fragt den Spieler, ob er dem Wurf seines Vorgängers vertraut

        :param lastThrow: Wurf des vorherigen Spielrs
        :param iRound: In der wievielten Runde befinden wir uns"""
        raise NotImplementedError

    def getThrowStated(self, myThrow: Throw, lastThrow: Throw, iRound: int) -> Throw:
        """Gibt basierend auf dem Wurf dieses Spielers myThrow das Würfelergebnis zurück, das der Spieler verkündet.

        Das angegebene Ergebnis muss nicht der Wahrheit entsprechen. Der eigene Wurf wird zuvor vom Spiel (Game)
        zufällig gewählt und dieser Funktion übergeben. Die Funktion muss None als Wert für lastThrow akzeptieren
        können.

        :param myThrow: Wurf dieses Spielers
        :param lastThrow: Wurf des vorherigen Spielrs
        :param iRound: In der wievielten Runde befinden wir uns
"""
        raise NotImplementedError


class DummyPlayer(Player):
    """Sehr grundlegende Spielerklasse.

    Kann das eigene Ergebnis den Vorgänger überbieten, wird dieses angegeben.
    Kann es das nicht, wird ein falsches Ergebnis verkündet"""

    def __init__(self, playerId: int = None) -> None:
        super().__init__(playerId)

    def getDoubt(self, lastThrow: Throw, iRound: int) -> bool:
        if lastThrow.isMaexchen:
            return True
        else:
            return False

    def getThrowStated(self, myThrow: Throw, lastThrow: Throw, iRound: int) -> Throw:
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

    def __init__(self, playerId=None) -> None:
        super().__init__(playerId)

    def getDoubt(self, lastThrow: Throw, iRound: int) -> bool:
        if lastThrow.isMaexchen:
            return True
        else:
            return False

    def getThrowStated(self, myThrow: Throw, lastThrow: Throw, iRound: int) -> Throw:
        """Generiert zufällig ein Pasch oder Mäxchen, um den vorherigen Wurf zu überbieten"""
        rank_11 = c.THROW_RANK_BY_VALUE[11]
        if lastThrow is None:
            return Throw(random.choice(c.THROW_VALUES[rank_11:]))
        else:
            return Throw(random.choice(c.THROW_VALUES[max(lastThrow.rank + 1, rank_11):]))


class ProbabilisticPlayer(Player):
    """Wahrscheinlichkeits-Spielerklasse

    Handelt nach den Erkenntnissen aus 2.1 und 2.2
    """
    
    def getDoubt(self, lastThrow: Throw, iRound: int) -> bool:
        if iRound == 0:
            # Sollte nie eintreten
            logging.warn("Player.getDoubt() called on first round (iRound = 0)")
            return
        elif iRound == 1:
            if lastThrow <= Throw(61):
                return False
            else:
                return True
        else:
            return random.choice([True, False])

    def getThrowStated(self, myThrow: Throw, lastThrow: Throw, iRound: int) -> Throw:
        if iRound == 0:
            print(myThrow, lastthrow)
            # Erster Spieler der Runde
            if myThrow <= Throw(61):
                return Throw(61)
            else:
                return myThrow
        elif iRound == 1:
            # Zweiter Spieler der Runde
            return myThrow
        else:
            # Andere Position
            return myThrow
