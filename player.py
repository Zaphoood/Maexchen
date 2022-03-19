from __future__ import annotations  # Notwendig für type hints, die die eigene Klasse beinhalten
from typing import Callable
from contextlib import suppress
from collections import Counter
import random
import logging

import constants as c
import gameevent
from throw import Throw, throwByRank
from utils import probLT, probGE


class Player:
    # Identifikationsnummer die unter allen Player in einem Game einzigartig sein muss.
    # Wird von Game zugewiesen
    id: int

    def __init__(self, playerId: int = None, listensToEvents: bool = False):
        self.id = playerId
        self.listensToEvents = listensToEvents

    def __str__(self):
        return f"{self.__class__.__name__} with id {self.id}"

    def __repr__(self):
        return f"<{self.__class__.__name__} (id={self.id})>"

    def __eq__(self, other):
        # Falls other kein Player oder eine Unterklasse davon ist, Fehler ausgeben
        if not isinstance(other, Player):
            raise NotImplementedError(f"Can't compare Player to non-Player ({type(other)})")
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

    def onInit(self, players: list[Player]) -> None:
        """Wird von Evaluation vor dem beginn einer Simulation aufgerufen.

        :param players: Liste aller Spieler die am Spiel teilnehmen"""
        pass

    def onEvent(self, event: gameevent.Event) -> None:
        """Wird von Game aufgerufen, wenn ein Ereignis im Spiel passiert und self.listensToEvents==True.

        :param event: Das Ereignis, das passiert ist"""
        pass


class DummyPlayer(Player):
    """Sehr grundlegende Spielerklasse.

    Kann das eigene Ergebnis den Vorgänger überbieten, wird dieses angegeben.
    Kann es das nicht, wird ein falsches Ergebnis verkündet"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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

class AdvancedDummyPlayer(Player):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def getDoubt(self, lastThrow: Throw, iMove: int, rng: random.Random) -> bool:
        if lastThrow.isMaexchen or lastThrow == Throw(66):
            return True
        else:
            return False

    def getThrowStated(self, myThrow: Throw, lastThrow: Throw, iMove: int, rng: random.Random) -> Throw:
        if lastThrow is None or myThrow > lastThrow:
            return myThrow
        else:
            if lastThrow == Throw(66):
                return Throw(21)
            else:
                return Throw(rng.choice(c.THROW_VALUES[lastThrow.rank + 1:-1]))

class CounterDummyPlayer(Player):
    """Möglichst erfolgreich gegen DummyPlayer"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, listensToEvents=True, **kwargs)

        # Den letzten und vorletzten Wurf abspeichern
        self.secondLastThrow = None
        self.lastThrow = None
        # Den Spieler, der den letzten Wurf angegeben hat, abspeichern
        self.lastPlayerId = None

    def onEvent(self, event: gameevent.Event) -> None:
        if event.eventType == gameevent.EVENT_TYPES.THROW:
            self.secondLastThrow = self.lastThrow
            self.lastThrow = event.throwStated
        elif event.eventType == gameevent.EVENT_TYPES.KICK:
            # Wird ein Spieler gekickt, wird der zu überbietende Wert zurückgesetzt,
            # das Spiel beginnt also sozusagen von neuem. Deswegen Tracking-Variablen zurücksetzten
            self.lastThrow = self.secondLastThrow = None

    def getDoubt(self, lastThrow: Throw, iMove: int, rng: random.Random) -> bool:
        if lastThrow.isMaexchen:
            return True
        elif self.secondLastThrow is not None and lastThrow == self.secondLastThrow + 1:
            # Letzter Wurf ist genau eins höher als der vorletzte -> letzter Spieler ist wahrscheinlich
            # lügender DummyPlayer
            return True
        else:
            return False

    def getThrowStated(self, myThrow: Throw, lastThrow: Throw, iMove: int, rng: random.Random) -> Throw:
        if lastThrow is None or myThrow > lastThrow:
            return myThrow
        else:
            # Wenn zum Lügen gezwungen: 66 angeben, sodass der nächste Spieler Mäxchen angeben muss -> übernächster Spieler misstraut
            return Throw(66)

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
    def __init__(self, *args, doubtChance: float = 0.5, **kwargs):
        super().__init__(*args, **kwargs)
        if not 0 <= doubtChance <= 1:
            raise ValueError("Parameter doubtChance must be in range [0., 1.]")
        self.doubtChance = doubtChance

    def getDoubt(self, lastThrow: Throw, iMove: int, rng: random.Random) -> bool:
        return rng.random() < self.doubtChance

    def getThrowStated(self, myThrow: Throw, lastThrow: Throw, iMove: int, rng: random.Random) -> Throw:
        return Throw(rng.choice(c.THROW_VALUES))


class ThresholdPlayer(Player):
    """Schwellenwert-Spielerklasse

    Misstraut und lügt ab bestimmten Schwellenwerten.
    Ist das Ergebnis des Vorgängers größer oder gleich doubtThreshold, wird dem Vorgänger misstraut.
    Ist das eigene Eregebnis höher als dass des Vorgängers und niedriger als lieThreshold, wird gelogen und
    lieThreshold als eigener Wurf zurückgegeben.
    """
    
    def __init__(self, playerId: int = None, doubtThreshold: int = 61, lieThreshold: int = 61):
        super().__init__(playerId)
        if isinstance(doubtThreshold, int):
            self.doubtThreshold = Throw(doubtThreshold)
        elif isinstance(doubtThreshold, Throw):
            self.doubtThreshold = doubtThreshold
        else:
            raise TypeError(f"doubtThreshold must be of type int or Throw (got {type(doubtThreshold)})")
        if isinstance(lieThreshold, int):
            self.lieThreshold = Throw(lieThreshold)
        elif isinstance(lieThreshold, Throw):
            self.lieThreshold = lieThreshold
        else:
            raise TypeError(f"lieThreshold must be of type int or Throw (got {type(lieThreshold)})")

    def getDoubt(self, lastThrow: Throw, iMove: int, rng: random.Random) -> bool:
        if self.doubtThreshold:
            return lastThrow >= self.doubtThreshold
        else:
            return lastThrow.isMaexchen

    def getThrowStated(self, myThrow: Throw, lastThrow: Throw, iMove: int, rng: random.Random) -> Throw:
        if lastThrow is None or myThrow > lastThrow:
            # Erster Zug der Runde oder vorheriger Spieler wurde entfernt -> Zu überbietender Wert wurde zurückgesetzt
            if myThrow <= self.lieThreshold:
                return self.lieThreshold
            else:
                return myThrow
        else:
            # Anderer Zug
            return lastThrow + 1

class CounterThresPlayer(Player):
    """Möglichst effektiv gegen CounterPlayer.

    Speichert die angegebenen Ergebnisse der Mitspieler ab. Wird ein Muster
    erkannt, das dem Verhalten eines CounterPlayer entspricht, wird diesem beim vermuteten
    Schwellenwert immer misstraut"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, listensToEvents=True, **kwargs)

        # Statistik über die Würfe der anderen Spieler. Das Format ist:
        # { player0Id: [wurf0, wurf1, ...],
        #   player1Id: [wurf0, wurf1, ...],
        #   ... }
        # TODO: Use this table structure instead:
        # { player0ID: [0, 0, 0, 0, ..., 0], ... }
        #              ^--- 21 entries --^
        self.throwStats = {}
        # Dasselbe, aber als Counter-Objekt, d. h. kategorisiert und gezählt
        self.throwStatsCounted = {}
        self.recalcCounted = {}
        # Den Spieler, der den letzten Wurf angegeben hat, abspeichern
        self.lastPlayerId = None

        self.minDataPoints = 5
        self.freqThres = 0.4

    def onInit(self, players: list[Player]) -> None:
        # Leere Statistik erstellen
        self.throwStats = {player.id: [] for player in players if player is not self}
        self.throwStatsCounted = {player.id: None for player in players if player is not self}
        self.recalcCounted = {player.id: True for player in players if player is not self}

    def onEvent(self, event: gameevent.Event) -> None:
        if event.eventType == gameevent.EVENT_TYPES.THROW:
            if event.playerId != self.id:
                self.throwStats[event.playerId].append(event.throwStated.value)
                self.lastPlayerId = event.playerId
        elif event.eventType == gameevent.EVENT_TYPES.KICK:
            # Wird ein Spieler gekickt, wird der zu überbietende Wert zurückgesetzt,
            # das Spiel beginnt also sozusagen von neuem. Deswegen Tracking-Variablen zurücksetzten
            self.lastPlayerId = None

    def getDoubt(self, lastThrow: Throw, iMove: int, rng: random.Random) -> bool:
        if lastThrow.isMaexchen:
            return True
        elif self.existThresSuggestion(self.lastPlayerId):
            # Entscheidung Anhand von Statistik über Spieler treffen
            if self.mostFreqThrow(self.lastPlayerId) == lastThrow:
                # Spieler hat entsprechend der Vermutung gehandelt
                return True
        # Vermutung existiert nicht oder konnte nicht bestätigt werden
        return False


    def getThrowStated(self, myThrow: Throw, lastThrow: Throw, iMove: int, rng: random.Random) -> Throw:
        """Verhalten ist dasselbe wie DummyPlayer."""
        if lastThrow is None:
            return myThrow
        else:
            if myThrow > lastThrow:
                return myThrow
            else:
                return lastThrow + 1

    def existThresSuggestion(self, playerId: int):
        """Beurteilen, ob von einem Spieler hinreichend aussagekräftige Statistik existiert,
        um eine Vermutung über dessen Schwellenwert aufzustellen.

        Die Vorraussetzung dafür ist, dass die Anzahl Datenpunkte über diesen Spieler > self.minDataPoints
        und dass ein Ergebnis einen Anteil an allen von diesem Spieler verkündeten Ergebnisse ausmacht,
        der größer als self.freqThres ist.

        :param playerId: Die ID des zu beurteilenden Spielers
        """
        return self.countDataPoints(playerId) > self.minDataPoints and self.mostFreqThrowFreq(playerId) > self.freqThres

    def getPlayerStatsCounted(self, playerId: int):
        if self.recalcCounted[playerId] or self.throwStatsCounted[playerId] is None:
            self.throwStatsCounted[playerId] = Counter(self.throwStats[playerId])
        return self.throwStatsCounted[playerId]

    def mostFreqThrow(self, playerId: int):
        """Den von einem Spieler am häufigsten angegebenen Wurf zurückgeben."""
        return self.getPlayerStatsCounted(playerId).most_common(1)[0][0]

    def mostFreqThrowFreq(self, playerId: int):
        """Die Frequenz des am häufigsten angegebenen Wurfs eines Spielers berechenen."""
        most_freq = self.getPlayerStatsCounted(playerId).most_common(1)
        try:
            total_occs = most_freq[0][1] 
            return total_occs / self.countDataPoints(playerId)
        except IndexError:
            # No data collected for this specific player
            return 0

    def countDataPoints(self, playerId: int):
        """Die Anzahl von aufgezeichneten Datenpunkten über einen bestimmten Spieler zurückgeben."""
        return len(self.throwStats[playerId])

class TrackingPlayer(Player):
    """Spielerklasse, die das Verhalten anderer Spieler beobachtet und dementsprechend handelt"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, listensToEvents=True, **kwargs)

        # Statistik über die Wahrheitstreue der anderen Spieler. Das Format ist:
        # {player0Id: [anzahl_wahrheit0, anzahl_wahrheit0],
        #  player1Id: [anzahl_wahrheit1, anzahl_wahrheit1],
        #  ...}
        self.playerStats = {}
        # Den letzten und vorletzten Wurf abspeichern
        self.secondLastThrow = None
        self.lastThrow = None
        # Den Spieler, der den letzten Wurf angegeben hat, abspeichern
        self.lastPlayerId = None

    def getDoubt(self, lastThrow: Throw, iMove: int, rng: random.Random) -> bool:
        if lastThrow.isMaexchen:
            return True
        else:
            return self.shouldDoubt(lastThrow)

    def getThrowStated(self, myThrow: Throw, lastThrow: Throw, iMove: int, rng: random.Random) -> Throw:
        if lastThrow is None or myThrow > lastThrow:
            return myThrow
        else:
            return lastThrow + 1

    def onInit(self, players: list[Player]) -> None:
        # Leere Statistik erstellen
        self.playerStats = {player.id: [0, 0] for player in players if player is not self}

    def onEvent(self, event: gameevent.Event) -> None:
        if event.eventType == gameevent.EVENT_TYPES.THROW:
            self.secondLastThrow = self.lastThrow
            self.lastThrow = event.throwStated
            self.lastPlayerId = event.playerId
        elif event.eventType == gameevent.EVENT_TYPES.KICK:
            if event.reason == gameevent.KICK_REASON.LYING:
                # Tracken, dass Spieler gelogen hat
                if event.playerId != self.id:
                    self.trackPlayerLie(event.playerId)
            elif event.reason == gameevent.KICK_REASON.FALSE_ACCUSATION:
                # Tracken, dass vorheriger Spieler (-> self.lastPlayerId) die Wahrheit gesagt hat
                # Es wird angenommen dass lastPlayerId!=None, da sonst eine falsche Anschludigung sonst
                # nicht möglich ist
                if self.lastPlayerId != self.id:
                    self.trackPlayerTruth(self.lastPlayerId)
            # Wird ein Spieler gekickt, wird der zu überbietende Wert zurückgesetzt,
            # das Spiel beginnt also sozusagen von neuem. Deswegen Tracking-Variablen zurücksetzten
            self.lastThrow = self.secondLastThrow = self.lastPlayerId = None

    def trackPlayerLie(self, playerId: int) -> None:
        self.savePlayerStat(playerId, 1)

    def trackPlayerTruth(self, playerId: int) -> None:
        self.savePlayerStat(playerId, 0)

    def savePlayerStat(self, playerId: int, event: int) -> None:
        """Abspeichern, dass ein Spieler gelogen hat bzw. die Wahrheit gesagt hat.

        :param playerId: Die ID des Spielers, um den es sich handelt
        :param event: event==0 => Spieler hat die Wahrheit gesagt
                      event==1 => Spieler hat gelogen"""
        if self.playerStats == {}:
            logging.warning(f"TrackingPlayer: No player statistics created (i.e. onInit() wasn't called) for {self.__repr__()}")
        else:
            self.playerStats[playerId][event] += 1

    def getPlayerCredibility(self, playerId: int) -> float:
        """Errechnet anhand der Statistik über einen Spieler dessen Glaubwürdigkeit.

        Die Glaubwürdigkeit berechnet sich wie folgt:
            glaubw = anzahl_wahrheit / (anzahl_wahrheit + anzahl_lüge)

        :param playerId: Die ID des Spielers, dessen Glaubwürdigkeit berechnet werden soll."""
        truths, lies = self.playerStats[playerId]
        return truths / (truths + lies) if self.existPlayerStats(playerId) else None 

    def existPlayerStats(self, playerId: int) -> bool:
        """Gibt zurück, ob für einen Spieler bereits etwas in dessen Statistik aufgezeichnet wurde.

        :param playerId: Die ID des Spielers, dessen Statistik überprüft werden soll."""
        with suppress(KeyError):  # contextlib.suppress
            return sum(self.playerStats[playerId]) > 0
        return False

    def shouldDoubt(self, playerThrow: Throw) -> bool:
        """Einschätzen, ob dem vorherigen Spieler misstraut werden soll.
        Das geschieht auf folgende Weise: Zuerst wird die Wahrscheinlichkeit, dass der Spieler lügt,
        eingeschätzt. Diese errechnet sich aus der Wahrscheinlichkeit, den vorletzten Wurf mit einem zufälligen
        Wurf zu übertreffen mal der Tendenz des Spielers zum Lügen (1 - Glaubwürdigkeit) plus die Wahrscheinlichkeit,
        den vorletzten Wurf mit einem zufälligen Wurf nicht zu übertreffen.
            P_Lüge = P_zufällig_erreichen(Vorletzter Wurf) * P_Lüge + P_nicht_zufällig_erreichen
        Anschließend wird die Wahrscheinlichkeit, dass der Spieler die Wahrheit sagt, eingeschätzt:
        Wahrscheinlichkeit, den vorletyten Wurf mit einem zufällgien Wurf zu übertreffen mal der Wahrscheinlichkeit,
        dass der Spieler die Wahrheit sagt.
            P_Wahrheit = P_zufällig_erreichen(Vorletzter Wurf) * P_Wahrheit

        :param playerId: ID des vorherigen Spielers
        :param playerThrow: Wurf des vorherigen Spielers"""
        if self.secondLastThrow is None:
            # Zweiter Zug der "Runde" (nach letztem Zurücksetzen des zu überbietenden Wertes)
            if self.existPlayerStats(self.lastPlayerId):
                return self.getPlayerCredibility(self.lastPlayerId)
            else:
                return False

        else:
            # Späterer Zug
            if self.existPlayerStats(self.lastPlayerId):
                p_lie = probGE(self.secondLastThrow) * (1 - self.getPlayerCredibility(self.lastPlayerId)) + probLT(self.secondLastThrow) 
                p_truth = probGE(self.secondLastThrow) * self.getPlayerCredibility(self.lastPlayerId)
            else:
                p_lie = probGE(self.secondLastThrow)
                p_truth = probLT(self.secondLastThrow)

            return p_lie > p_truth


# Conversion from command line flags to Player classes
FLAGS_TO_PLAYERS = {
    "dummy": DummyPlayer,
    "c-dummy": CounterDummyPlayer,
    "show-off": ShowOffPlayer,
    "random": RandomPlayer,
    "thres": ThresholdPlayer,
    "threshold": ThresholdPlayer,
    "c-thres": CounterThresPlayer,
    "tracking": TrackingPlayer,
    "adv-dummy": AdvancedDummyPlayer
}
