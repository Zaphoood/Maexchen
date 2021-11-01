from __future__ import annotations  # Notwendig für type hints, die die eigene Klasse beinhalten
from typing import Callable
import random
import logging

import constants as c
import gameevent
from throw import Throw, throwByRank


class Player:
    id: int  # Identifikationsnummer die unter allen Player in einem Game einzigartig sein muss; wird von Game

    # zugewiesen

    def __init__(self, playerId: int = None):
        self.id = playerId
        self.listensToEvents = False

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

    def getDoubt(self, lastThrow: Throw, iMove: int, rng: random.Random) -> bool:
        """Fragt den Spieler, ob er dem Wurf seines Vorgängers vertraut

        :param lastThrow: Wurf des vorherigen Spielrs
        :param iMove: Um den wievielten Zug der Runde handelt es sich
        """
        raise NotImplementedError

    def getThrowStated(self, myThrow: Throw, lastThrow: Throw, iMove: int, rng: random.Random) -> Throw:
        """Gibt basierend auf dem Wurf dieses Spielers myThrow das Würfelergebnis zurück, das der Spieler verkündet.

        Das angegebene Ergebnis muss nicht der Wahrheit entsprechen. Der eigene Wurf wird zuvor vom Spiel (Game)
        zufällig gewählt und dieser Funktion übergeben. Die Funktion muss None als Wert für lastThrow akzeptieren
        können.

        :param myThrow: Wurf dieses Spielers
        :param lastThrow: Wurf des vorherigen Spielers
        :param iMove: Um den wievielten Zug der Runde handelt es sich"""
        raise NotImplementedError

   def onInit(self, players: list[Player]):
        """Wird von Evaluation vor dem beginn einer Simulation aufgerufen.

        :param players: Liste aller Spieler die am Spiel teilnehmen"""
        pass

    def onEvent(self, event: gameevent.Event):
        """Wird von Game aufgerufen, wenn ein Ereignis im Spiel passiert und self.listensToEvents==True.

        :param event: Das Ereignis, das passiert ist"""
        pass


class DummyPlayer(Player):
    """Sehr grundlegende Spielerklasse.

    Kann das eigene Ergebnis den Vorgänger überbieten, wird dieses angegeben.
    Kann es das nicht, wird ein falsches Ergebnis verkündet"""

    def __init__(self, playerId: int = None) -> None:
        super().__init__(playerId)

    def getDoubt(self, lastThrow: Throw, iMove: int, rng: random.Random) -> bool:
        if lastThrow.isMaexchen:
            return True
        else:
            return False

    def getThrowStated(self, myThrow: Throw, lastThrow: Throw, iMove: int, rng: random.Random) -> Throw:
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

    def getDoubt(self, lastThrow: Throw, iMove:int, rng: random.Random) -> bool:
        if lastThrow.isMaexchen:
            return True
        else:
            return False

    def getThrowStated(self, myThrow: Throw, lastThrow: Throw, iMove: int, rng: random.Random) -> Throw:
        """Generiert zufällig ein Pasch oder Mäxchen, um den vorherigen Wurf zu überbieten"""
        rank_11 = c.THROW_RANK_BY_VALUE[11]
        if lastThrow is None:
            return Throw(random.choice(c.THROW_VALUES[rank_11:]))
        else:
            return Throw(random.choice(c.THROW_VALUES[max(lastThrow.rank + 1, rank_11):]))


class RandomPlayer(Player):
    def __init__(self, playerId: int = None, doubtChance: float = 0.5) -> None:
        super().__init__(playerId)
        if not 0 <= doubtChance <= 1:
            raise ValueError("Parameter doubtChance must be in range [0., 1.]")
        self.doubtChance = doubtChance

    def getDoubt(self, lastThrow: Throw, iMove: int, rng: random.Random) -> bool:
        return rng.random() < self.doubtChance

    def getThrowStated(self, myThrow: Throw, lastThrow: Throw, iMove: int, rng: random.Random) -> Throw:
        return Throw(rng.choice(c.THROW_VALUES))


class ProbabilisticPlayer(Player):
    """Wahrscheinlichkeits-Spielerklasse

    Handelt teilweise nach den Erkenntnissen aus 2.1 und 2.2, ansonsten ähnlich
    wie DummyPlayer.
    """
    
    def getDoubt(self, lastThrow: Throw, iMove: int, rng: random.Random) -> bool:
        if iMove == 0:
            # Sollte nie eintreten
            logging.warn("Player.getDoubt() called on first round (iMove = 0)")
            return
        elif iMove == 1:
            if lastThrow <= Throw(61):
                return False
            else:
                return True
        else:
            if lastThrow.isMaexchen:
                return True
            return random.choice([True, False])

    def getThrowStated(self, myThrow: Throw, lastThrow: Throw, iMove: int, rng: random.Random) -> Throw:
        if lastThrow is None:
            # Erster Zug der Runde oder vorheriger Spieler wurde entfernt -> Zu überbietender Wert wurde zurückgesetzt
            if myThrow <= Throw(61):
                return Throw(61)
            else:
                return myThrow
        else:
            # Anderer Zug
            if myThrow > lastThrow:
                return myThrow
            else:
                # Wenn schon lügen, dann richtig: Mittelwert zwischen zu überbietendem Wert und Mäxchen zurückgeben
                lieRank = min(int((lastThrow.rank + c.THROW_RANK_BY_VALUE[21]) / 2),
                    lastThrow.rank + 1)
                return throwByRank(lieRank)


class TrackingPlayer(self):
    """Spielerklasse, die das Verhalten anderer Spieler beobachtet und dementsprechend handelt"""
    def __init__(self, playerId: int):
        super().__init__(playerId)
        self.listensToEvents = True
        
        # Den letzten und vorletzten Wurf abspeichern
        self.secondLastThrow = None
        self.lastThrow = None
        # Den Spieler, der den letzten Wurf angegeben hat, abspeichern
        self.lastPlayerId = None

    def getDoubt(self, lastThrow: Throw, iMove: int, rng: random.Random) -> bool:
        pass

    def getThrowStated(self, myThrow: Throw, lastThrow: Throw, iMove: int, rng: random.Random) -> Throw:
        pass

    def onEvent(self, event: gameevent.Event) -> None:
        if event.eventType == gameevent.EVENT_TYPES.THROW:
            self.secondLastThrow = self.lastThrow
            self.lastThrow = event.throwStated
            self.lastPlayerId = event.playerId
        elif event.eventType == gameevent.EVENT_TYPES.KICK:
            if event.reason == gameevent.KICK_REASON.LYING:
                # tracken, dass spieler gelogen hat
                pass
            elif event.reason == gameevent.KICK_REASON.FALSE_ACCUSATION:
                # tracken, dass vorheriger spieler (-> self.lastPlayer) die wahrheit gesagt hat
                pass
            # Wird ein Spieler gekickt, wird der zu überbietende Wert zurückgesetzt,
            # das Spiel beginnt also sozusagen von neuem. Deswegen Tracking-Variablen zurücksetzten
            self.lastThrow = self.secondLastThrow = self.lastPlayerId = None

