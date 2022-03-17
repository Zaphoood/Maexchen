import logging
import copy
import random
import sys

from gamelog import GameLog
import gameevent
from player import Player
from throw import Throw

class TooFewPlayers(Exception):
    """Is raised when too few players have been provided to the Game class"""
    def __init__(self, *args):
        if args:
            self.n_players = args[0]
        else:
            self.n_players = None


class Game:
    """Regelt die Umsetzung der Spielregeln (Würfeln und die Interaktion zwischen Spielern)."""
    players: list[Player]  # Liste aller Spieler
    currentPlayer: int  # Index des Spielers der gerade an der Reihe ist
    incrementCurrentPlayer: bool  # Ob currentPlayer nach dem aktuellen Zug erhöht werden soll (wird ein Spieler entfernt, soll dies nicht geschehen)
    lastThrowStated: Throw  # Angabe die der letzte Spieler über sein Wurfergebnis gemacht hat
    lastThrowActual: Throw  # Tatsächlicher Wurf des letzten Spielers
    moveCounter: int  # Zählt die Züge
    initialized: bool  # Gibt an, ob das Spiel initialisiert wurde
    running: bool  # Gibt an, ob das Spiel noch läuft
    log: GameLog
    rng: random.Random  # Pseudozufallszahlengenerator

    def __init__(self, players: list[Player], seed: int = None, shufflePlayers: bool = False, disableDeepcopy: bool = False) -> None:
        if disableDeepcopy:
            self.players = players
        else:
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

        self.iMove = -1  # Gibt den Zug seit dem Anfang der Runde bzw. dem letzten zurücksetzten des zu überbietenden Wertes an
        # TODO: Auch so wie beschrieben implementieren!
        self.lastThrowStated = None
        self.lastThrowActual = None
        self.initialized = False
        self.running = False

        self.log = GameLog(self.players)

        # Pseudo-Zufallszahlengenerator (RNG) initialisieren. Falls ein Seed als Parameter angegeben ist, diesen
        # verwenden, ansonsten einen neuen Seed generieren. Dadurch ist der Seed immer bekannt und kann verwendet
        # werden, um Spiele zu reproduzieren
        if seed is None:
            seed = random.randrange(sys.maxsize)
        self._seed = seed
        self.rng = random.Random(seed)

        self.rng.shuffle(self.players)

    def init(self) -> None:
        """Überprüft, ob genügend Spieler vorhanden sind und initialisiert das Spiel"""
        if len(self.players) > 1:
            logging.info("=== Game initialized ===")
            self.currentPlayer = self.rng.randrange(0, len(self.players))
            self.initialized = True
            self.running = True
        else:
            self.happen(gameevent.EventAbort(message="Too few players for game (at least 2 are required)"))
            raise TooFewPlayers(len(self.players))

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

        self.iMove = 0 if self.iMove == -1 else self.iMove + 1
        logging.info(f"Move {self.iMove}")
        self.log.newRound()

        self.handlePlayerMove()

        if len(self.players) == 0:
            # Dieser Zustand (kein Spieler mehr übrig) sollte nicht eintreten.
            # Das Spiel ist bereits vorbei, wenn nur ein Spieler übrig bleibt.
            logging.warning("Zero players left, game is over. (How did we get here?)")
            self.happen(gameevent.EventAbort(message="Zero players left, game is over. (How did we get here?)"))
            self.running = False
        elif len(self.players) == 1:
            # Spiel ist vorbei
            logging.info(f"One player left, game is over")
            logging.info(f"{repr(self.players[0])} won")
            self.happen(gameevent.EventFinish(self.players[0].id))
            self.running = False
        else:
            logging.info(f"{len(self.players)} players left")

        # Den Index, der angibt, welcher Spieler an der Reihe ist, nur erhöhen, falls kein Spieler gelöscht wurde
        if self.incrementCurrentPlayer:
            self.currentPlayer += 1
        # Modulo-Operator muss immer angewendet werden, auch wenn der Spielerindex nicht erhöht wurde, für den Fall
        # dass der letzte Spieler aus self.players entfernt wird
        self.currentPlayer %= len(self.players)

    def handlePlayerMove(self) -> bool:
        """Regelt die Interaktion mit der Spielerklasse"""
        # self.incrementCurrentPlayer wird auf False gesetzt, sollte ein Spieler gelöscht werden.
        # Dadurch wird currentPlayer am Ende von move() nicht erhöht
        self.incrementCurrentPlayer = True

        if self.lastThrowStated is None:
            # Erste Runde -> Es gibt keinen Vorgänger
            doubtPred = False
        else:
            # Den Spieler, der an der Reihe ist, fragen, ob er seinen Vorgänger anzweifelt
            doubtPred = self.players[self.currentPlayer].getDoubt(self.lastThrowStated, self.iMove, self.rng)

        if doubtPred is None:
            # Spieler hat nicht geantwortet
            logging.info(
                    f"{repr(self.players[self.currentPlayer])} will be removed (got no response when asked for doubt)")
            self.kickPlayer(self.currentPlayer, gameevent.KICK_REASON.NO_RESPONSE)
        elif doubtPred:
            # Spieler hat geantwortet, zweifelt das vorherige Ergebnis an
            logging.info(f"{repr(self.players[self.currentPlayer])} chose to doubt their predecessor.")
            self.happen(gameevent.EventDoubt(self.players[self.currentPlayer].id))
            if self.lastThrowStated == self.lastThrowActual:
                # Aktueller Spieler ist im Unrecht, Vorgänger hat die Wahrheit gesagt -> Aktuellen Spieler entfernen
                playerToKick = self.currentPlayer
                self.kickPlayer(self.currentPlayer, gameevent.KICK_REASON.FALSE_ACCUSATION, message=f"Previous {repr(self.players[(self.currentPlayer - 1) % len(self.players)])} was wrongfully doubted, {repr(self.players[playerToKick])} will be removed")
            else:
                # Aktueller Spieler hat Recht, Vorgänger hat gelogen -> Vorherigen Spieler entfernen
                playerToKick = (self.currentPlayer - 1) % len(self.players)
                self.kickPlayer(playerToKick, gameevent.KICK_REASON.LYING, message=f"Previous player was rightfully doubted, {repr(self.players[playerToKick % len(self.players)])} will be removed")

        else:
            # Der Spieler hat geantwortet, akzeptiert das vorherige Ergebnis, würfelt selber und verkündet das Ergebnis
            # Zufälligen Wurf generieren
            logging.info(f"{repr(self.players[self.currentPlayer])} chose not to doubt their predecessor.")
            currentThrow = self.randomThrow()
            # Den Spieler fragen, welchen Wurf er angeben will, gewürfelt zu haben
            throwStated = self.players[self.currentPlayer].getThrowStated(currentThrow, self.lastThrowStated,
                    self.iMove, self.rng)
            if throwStated is None:
                # Spieler hat nicht geantwortet
                self.kickPlayer(self.currentPlayer, gameevent.KICK_REASON.NO_RESPONSE, message=f"{repr(self.players[self.currentPlayer])} will be removed (got no response when asked for Throw)")
            else:
                # Spieler hat geantwortet
                logging.info(
                        f"{repr(self.players[self.currentPlayer])} threw {str(currentThrow)}, states they threw {throwStated}")
                self.happen(gameevent.EventThrow(self.players[self.currentPlayer].id, currentThrow, throwStated))
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
                        self.kickPlayer(self.currentPlayer, gameevent.KICK_REASON.FAILED_TO_BEAT_PREDECESSOR, message=f"Stated current throw {throwStated} doesn't beat stated previous throw {self.lastThrowStated}")

    def kickPlayer(self, i: int, reason: gameevent.KICK_REASON, message: str = "") -> None:
        """Einen Spieler aus der Runde entfernen.

        :param i: Index des Spielers, der entfernt werden soll
        :param reason: Grund für das ausscheiden des Spielers
        :param message: Nachricht, die im log ausgegeben werden soll."""
        self.happen(gameevent.EventKick(self.players[i].id, reason))
        self.players.pop(i)
        self.incrementCurrentPlayer = False
        # Nachdem ein Spieler entfernt wurde, beginnt die Runde von neuem, d.h. der nächste Spieler
        # kann irgendein Ergebnis würfeln und musst niemanden überbieten
        logging.info("Value to be beaten is reset.")
        self.lastThrowStated = None
        self.lastThrowActual = None 
        if message:
            logging.info(message)

    def happen(self, event: gameevent.Event) -> None:
        """Schreibt ein Event in den log und benachrichtigt Spieler mit listensToEvents==True davon.

        :param event: Ereignis"""
        # Im log speichern
        self.log.happen(event)

        # Andere Spieler benachrichtigen
        if event.eventType == gameevent.EVENT_TYPES.THROW:
            # Neues Event ohne event.throwActual erzeugen
            event = gameevent.EventThrow(event.playerId, None, event.throwStated)
        for player in self.players:
            if player.listensToEvents:
                player.onEvent(event)

    def isRunning(self) -> bool:
        return self.running

    def getSeed(self):
        return self._seed

    def randomThrow(self) -> Throw:
        """Gibt einen zufälligen Wurf zurück.

        Zum generieren der Werte wird self.rng verwendet."""
        return Throw(self.rng.randint(1, 6), self.rng.randint(1, 6))
