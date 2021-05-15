import logging
import copy
import random

from gamelog import GameLog
import gameevent
from player import Player
from throw import Throw

# logging.basicConfig(format='[%(levelname)s] %(message)s', level=logging.INFO)


class Game:
    """Regelt die Umsetzung der Spielregeln (Würfeln und die Interaktion zwischen Spielern)."""
    players: list[Player]  # Liste aller Spieler
    currentPlayer: int  # Index des Spielers der gerade an der Reihe ist
    lastThrowStated: Throw  # Angabe die der letzte Spieler über sein Wurfergebnis gemacht hat
    lastThrowActual: Throw  # Tatsächlicher Wurf des letzten Spielers
    moveCounter: int  # Zählt die Züge
    initialized: bool  # Gibt an, ob das Spiel initialisiert wurde
    running: bool  # Gibt an, ob das Spiel noch läuft
    log: GameLog
    rng: random.Random  # Pseudozufallszahlengenerator

    def __init__(self, players: list[Player], seed: int = None) -> None:
        # Verhindern, dass alle Spieler Referenzen zum selben Objekt sind
        # Das kann passieren, wenn eine Liste durch "list = [element] * integer" erstellt wird
        self.players = [copy.copy(p) for p in players]
        # Jedem Spieler eine eindeutige ID zuweisen
        ids = set()
        for p in self.players:
            if p.id is None or p.id in ids:
                # 0 als anfängliche ID verwenden falls noch keine zugewiesen wurden
                next_id = max(ids) + 1 if ids else 0
                p.id = next_id
            ids.add(p.id)

        self.currentPlayer = 0
        self.lastThrowStated = None
        self.lastThrowActual = None
        self.moveCounter = 0
        self.initialized = False
        self.running = False

        self.log = GameLog(self.players)

        self.rng = random.Random(seed)

    def init(self) -> None:
        """Überprüft, ob genügend Spieler vorhanden sind und initialisiert das Spiel"""
        if len(self.players) > 1:
            logging.info("Game initialized")
            self.initialized = True
            self.running = True
        else:
            logging.error("Game can't be initialized with only one player.")
            self.log.happen(gameevent.EventAbort(message="Game can't be initialized with only one player."))

    def run(self) -> None:
        """Führt so lange Iterationen des Spiels durch, bis es beendet ist"""
        if not self.initialized:
            logging.error("Game.run() was called even though the game is not yet initialized")
            return
        while self.running:
            self.move()

    def move(self) -> None:
        """Führt eine Iteration des Spiels durch"""
        if not self.initialized:
            logging.error("Game.move() was called even though the game is not yet initialized")
            return
        if not self.running:
            logging.warning("Game.move() was called even though the game is already over")
            return

        logging.info(f"Round {self.moveCounter}")
        self.log.newRound()

        # incrementCurrentPlayer wird auf False gesetzt, sollte ein Spieler gelöscht werden.
        # Dadurch wird currentPlayer am Ende von move() nicht erhöht
        incrementCurrentPlayer = True

        if self.lastThrowStated is None:
            # Erste Runde -> Es gibt keinen Vorgänger
            doubtPred = False
        else:
            # Den Spieler, der an der Reihe ist, fragen, ob er seinen Vorgänger anzweifelt
            doubtPred = self.players[self.currentPlayer].getDoubt(self.lastThrowStated)

        if doubtPred:
            # Der Spieler zweifelt das vorherige Ergebnis an
            logging.info(f"{repr(self.players[self.currentPlayer])} chose to doubt their predecessor.")
            self.log.happen(gameevent.EventDoubt(self.players[self.currentPlayer].id))
            if self.lastThrowStated == self.lastThrowActual:
                # Spieler hat nicht Recht, Vorgänger hat die Wahrheit gesagt -> Aktuellen Spieler entfernen
                playerToKick = self.currentPlayer
                logging.info(
                    f"Previous player was wrongfully doubted, {repr(self.players[self.currentPlayer])} will be removed")
                self.log.happen(gameevent.EventKick(
                    self.players[playerToKick].id, gameevent.KICK_REASON.FALSE_ACCUSATION))
            else:
                # Spieler hat Recht, Vorgänger hat gelogen -> Vorherigen Spieler entfernen
                playerToKick = self.currentPlayer - 1
                logging.info(
                    f"Previous player was rightfully doubted, {repr(self.players[playerToKick % len(self.players)])} will be removed")
                self.log.happen(gameevent.EventKick(
                    self.players[playerToKick].id, gameevent.KICK_REASON.LYING))
            self.players.pop(playerToKick)
            incrementCurrentPlayer = False

            # Nachdem ein Spieler entfernt wurde, beginnt die Runde von neuem, d.h. der nächste Spieler
            # kann irgendein Ergebnis würfeln und musst niemanden überbieten
            logging.info("Value to be beaten is reset.")
            self.lastThrowStated = None
            self.lastThrowActual = None
        else:
            # Der Spieler akzeptiert das vorherige Ergebnis, würfelt selber und verkündet das Ergebnis
            # Zufälligen Wurf generieren
            logging.info(f"{repr(self.players[self.currentPlayer])} chose not to doubt their predecessor.")
            currentThrow = self.randomThrow()
            logging.info(f"{repr(self.players[self.currentPlayer])} threw {str(currentThrow)}")
            # Den Spieler, der an der Reihe ist, nach dem Wurf fragen, den er angeben will
            throwStated = self.players[self.currentPlayer].getThrowStated(currentThrow, self.lastThrowStated)
            logging.info(f"{repr(self.players[self.currentPlayer])} states they threw {throwStated}")
            self.log.happen(gameevent.EventThrow(self.players[self.currentPlayer].id, currentThrow, throwStated))
            # Den Zug auswerten
            # Überprüfen, ob der Spieler die Angabe seines Vorgängers überboten hat
            if self.lastThrowStated is None:
                # Es gibt keinen Vorgänger
                logging.info("First round, automatically beats predecessor")
                self.lastThrowStated = throwStated
                self.lastThrowActual = currentThrow
            else:
                if throwStated > self.lastThrowStated:
                    # Vorgänger wurde überboten
                    # Den angegebenen und tatsächlichen Wurf für die nächste Runde speichern
                    logging.info(
                        f"Stated current throw {throwStated} beats stated previous throw {self.lastThrowStated}")
                    self.lastThrowStated = throwStated
                    self.lastThrowActual = currentThrow
                else:
                    # Vorgänger wurde nicht überboten
                    logging.info(
                        f"Stated current throw {throwStated} doesn't beat stated previous throw {self.lastThrowStated}")
                    self.log.happen(gameevent.EventKick(self.players[self.currentPlayer].id),
                                    gameevent.KICK_REASON.FAILED_TO_BEAT_PREDECESSOR)
                    self.players.pop(self.currentPlayer)
                    incrementCurrentPlayer = False

        if len(self.players) == 0:
            # Dieser Zustand (kein Spieler mehr übrig) sollte nicht eintreten.
            # Das Spiel ist bereits vorbei, wenn nur ein Spieler übrig bleibt.
            logging.warning("Zero players left, game is over. (How did we get here?)")
            self.log.happen(gameevent.EventAbort(message="Zero players left, game is over. (How did we get here?)"))
            self.running = False
        elif len(self.players) == 1:
            # Spiel ist vorbei
            logging.info(f"One player left, game is over")
            logging.info(f"{repr(self.players[0])} won")
            self.log.happen(gameevent.EventFinish(self.players[0]))
            self.running = False
        else:
            logging.info(f"{len(self.players)} players left")

        # Den Index, der angibt, welcher Spieler an der Reihe ist, nur erhöhen, falls kein Spieler gelöscht wurde
        if incrementCurrentPlayer:
            self.currentPlayer += 1
        # Modulo-Operator muss immer angewendet werden, auch wenn der Spielerindex nicht erhöht wurde, für den Fall
        # dass der letzte Spieler aus self.players entfernt wird
        self.currentPlayer %= len(self.players)

        self.moveCounter += 1

    def isRunning(self) -> bool:
        return self.running

    def randomThrow(self) -> Throw:
        """Gibt einen zufälligen Wurf zurück.

        Zum generieren der Werte wird self.rng verwendet."""
        return Throw(self.rng.randint(1, 6), self.rng.randint(1, 6))
