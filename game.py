import logging
import copy
import random
import sys
from typing import List, Set, Optional

from gamelog import GameLog
import gameevent
from player import Player
from throw import Throw, NoneThrow

class TooFewPlayers(Exception):
    """Is raised when too few players have been provided to the Game class"""
    def __init__(self, *args):
        if args:
            self.n_players = args[0]
        else:
            self.n_players = None

class DuplicateId(Exception):
    pass

class Game:
    """Regelt die Umsetzung der Spielregeln (Würfeln und die Interaktion zwischen Spielern)."""
    players: List[Player]  # All players participating in the game
    alive_players: List[bool] # For each player, store if it's still in the game
    currentPlayer: int  # Index des Spielers der gerade an der Reihe ist
    incrementCurrentPlayer: bool  # Ob currentPlayer nach dem aktuellen Zug erhöht werden soll (wird ein Spieler entfernt, soll dies nicht geschehen)
    lastThrowStated: Optional[Throw]  # Angabe die der letzte Spieler über sein Wurfergebnis gemacht hat
    lastThrowActual: Optional[Throw]  # Tatsächlicher Wurf des letzten Spielers
    moveCounter: int  # Zählt die Züge
    initialized: bool  # Gibt an, ob das Spiel initialisiert wurde
    _running: bool  # Gibt an, ob das Spiel noch läuft
    log: GameLog
    rng: random.Random  # Pseudozufallszahlengenerator

    def __init__(self, players: List[Player], seed: int = None, shufflePlayers: bool = True, deepcopy: bool = True, disableAssignIds: bool = False) -> None:
        # Verhindern, dass alle Spieler Referenzen zum selben Objekt sind
        # Das kann passieren, wenn eine Liste durch "list = [element] * integer" erstellt wird
        self.players = [copy.copy(p) for p in players] if deepcopy else players
        self.alive_players = [True for _ in self.players]
        if disableAssignIds:
            # If assigning unique IDs was disabled, check if the ones the players have are unique
            # If they are not, exit
            if not self.checkUniqueIds():
                raise DuplicateId()
        else:
            # Assign a unique Id to each player
            self.assignIds()
        # Index of the current move
        self.iMove = -1 
        self.lastThrowStated = None
        self.lastThrowActual = None
        # TODO: Set self._initialized to False; use @property for accessing it!
        self._running = False

        self.log = GameLog(self.players)

        # Initialize PRNG. Use seed if specified, otherwise generate a new seed.
        # The important part is not the randomness source but that the seed is known
        # so that the Game can be reproduced later.
        self._seed = seed if seed else random.randrange(sys.maxsize)
        self.rng = random.Random(self._seed)

        # Yes, the order of self.players changes, while self.alive_players stays the same.
        # This does not introduce any discrepancy because at this point all players are alive anyway.
        # Though, the order of neither of those lists must change throughout the game!
        if shufflePlayers:
            self.rng.shuffle(self.players)

    def init(self) -> None:
        """Überprüft, ob genügend Spieler vorhanden sind und initialisiert das Spiel"""
        if len(self.players) == self.countAlivePlayers() > 1:
            logging.info("=== Game initialized ===")
            self.currentPlayer = self.rng.randrange(0, len(self.players))
            self.initialized = True
            self._running = True
        else:
            self.happen(gameevent.EventAbort(message="Too few players for game (at least 2 are required)"))
            raise TooFewPlayers(len(self.players))

    def run(self) -> None:
        """Führt so lange Iterationen des Spiels durch, bis es beendet ist"""
        if not self.initialized:
            logging.error("Game.run() was called even though the game is not yet initialized")
            return
        while self._running:
            self.move()

    def move(self) -> None:
        """Führt eine Iteration des Spiels durch"""
        if not self.initialized:
            logging.error("Game.move() was called even though the game is not yet initialized")
            return
        if not self._running:
            logging.warning("Game.move() was called even though the game is already over")
            return

        self.iMove += 1
        logging.info(f"Move {self.iMove} | {self.countAlivePlayers()} players left")
        self.log.newRound()

        self.handlePlayerMove()

        
        alive_players = self.countAlivePlayers()
        if alive_players == 0:
            # Dieser Zustand (kein Spieler mehr übrig) sollte nicht eintreten.
            # Das Spiel ist bereits vorbei, wenn nur ein Spieler übrig bleibt.
            logging.warning("Zero players left, game is over. (How did we get here?)")
            self.happen(gameevent.EventAbort(message="Zero players left, game is over. (How did we get here?)"))
            self._running = False
        elif alive_players == 1:
            # Spiel ist vorbei
            logging.info(f"One player left, game is over")
            logging.info(f"{repr(self.players[0])} won")
            assert isinstance(self.players[0].id, int)
            self.happen(gameevent.EventFinish(self.players[0].id))
            self._running = False

        self.currentPlayer = self.nextAlivePlayer(self.currentPlayer + 1)

    def handlePlayerMove(self) -> None:
        """Regelt die Interaktion mit der Spielerklasse"""
        # self.incrementCurrentPlayer wird auf False gesetzt, sollte ein Spieler gelöscht werden.
        # Dadurch wird currentPlayer am Ende von move() nicht erhöht
        self.incrementCurrentPlayer = True

        # Default value, in cases there is no last throw
        doubtPred: Optional[bool] = False
        if self.lastThrowStated is not None:
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
            self.happen(gameevent.EventDoubt(self.players[self.currentPlayer].id)) # type: ignore
            if self.lastThrowStated == self.lastThrowActual:
                # Aktueller Spieler ist im Unrecht, Vorgänger hat die Wahrheit gesagt -> Aktuellen Spieler entfernen
                playerToKick = self.currentPlayer
                self.kickPlayer(playerToKick, gameevent.KICK_REASON.FALSE_ACCUSATION)
                logging.info(f"Previous player was wrongfully doubted, {repr(self.players[playerToKick])} will be removed")
            else:
                # Aktueller Spieler hat Recht, Vorgänger hat gelogen -> Vorherigen Spieler entfernen
                playerToKick = self.prevAlivePlayer(self.currentPlayer - 1)
                self.kickPlayer(playerToKick, gameevent.KICK_REASON.LYING)
                logging.info(f"Previous player was rightfully doubted, {repr(self.players[playerToKick])} will be removed")

        else:
            # Der Spieler hat geantwortet, akzeptiert das vorherige Ergebnis, würfelt selber und verkündet das Ergebnis
            if self.lastThrowStated is not None:
                logging.info(f"{repr(self.players[self.currentPlayer])} chose not to doubt their predecessor.")
            # Zufälligen Wurf generieren
            currentThrow = self.randomThrow()
            # Den Spieler fragen, welchen Wurf er angeben will, gewürfelt zu haben
            throwStated = self.players[self.currentPlayer].getThrowStated(currentThrow, self.lastThrowStated,
                    self.iMove, self.rng)
            if throwStated is None:
                # Spieler hat nicht geantwortet
                self.kickPlayer(self.currentPlayer, gameevent.KICK_REASON.NO_RESPONSE)
                logging.info(f"{repr(self.players[self.currentPlayer])} will be removed (got no response when asked for Throw)")
            else:
                # Spieler hat geantwortet
                logging.info(
                        f"{repr(self.players[self.currentPlayer])} threw {str(currentThrow)}, states they threw {throwStated}")
                # This is the only way mypy will accept that self.players[self.currentPlayer].id is not None....
                id_ = self.players[self.currentPlayer].id
                assert isinstance(id_, int)
                self.happen(gameevent.EventThrow(id_, currentThrow, throwStated))
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
                        self.kickPlayer(self.currentPlayer, gameevent.KICK_REASON.FAILED_TO_BEAT_PREDECESSOR)
                        logging.info(f"Stated current throw {throwStated} doesn't beat stated previous throw {self.lastThrowStated}")

    def kickPlayer(self, i: int, reason: gameevent.KICK_REASON) -> None:
        """Einen Spieler aus der Runde entfernen.

        :param i: Index des Spielers, der entfernt werden soll
        :param reason: Grund für das ausscheiden des Spielers
        :param message: Nachricht, die im log ausgegeben werden soll."""
        assert self.alive_players[i], f"Trying to kick already dead player {repr(self.players[i])}"
        # This is the only way to make mypy understand that id is in fact an int
        id_ = self.players[i].id
        assert isinstance(id_, int)
        self.happen(gameevent.EventKick(id_, reason))
        self.alive_players[i] = False
        self.incrementCurrentPlayer = False
        self.lastThrowStated = None
        self.lastThrowActual = None 
        logging.info("Value to beat has been reset.")

    def happen(self, event: gameevent.Event) -> None:
        """Schreibt ein Event in den log und benachrichtigt Spieler mit listensToEvents==True davon.

        :param event: Ereignis"""
        # Im log speichern
        self.log.happen(event)

        # Andere Spieler benachrichtigen
        if isinstance(event, gameevent.EventThrow):
            # Create new event with throwActual deleted, so that other players can't know what the actual Throw was
            event.throwActual = NoneThrow()
        for player in self.players:
            if player.listensToEvents:
                player.onEvent(event)

    @property
    def running(self) -> bool:
        return self._running

    @property
    def seed(self) -> int:
        return self._seed

    def assignIds(self) -> None:
        # Assign a unique ID to each player
        used_ids: Set[int] = set()
        for p in self.players:
            if not isinstance(p.id, int) or (p.id in used_ids):
                p.id = max(used_ids) + 1 if used_ids else 0
            used_ids.add(p.id)

    def checkUniqueIds(self) -> bool:
        # Check if every player has a unique id
        used_ids: Set[int] = set()
        for p in self.players:
            assert isinstance(p.id, int)
            if p.id in used_ids:
                return False
            used_ids.add(p.id)
        return True

    def nextAlivePlayer(self, start):
        assert any(self.alive_players), "Cannot find next alive player; none are left"
        start %= len(self.players)
        while not self.alive_players[start]:
            start = (start + 1) % len(self.players)
        return start
    
    def prevAlivePlayer(self, start):
        assert any(self.alive_players), "Cannot find next alive player; none are left"
        start %= len(self.players)
        while not self.alive_players[start]:
            start = (start - 1) % len(self.players)
        return start


    def countAlivePlayers(self):
        return sum(self.alive_players)

    def randomThrow(self) -> Throw:
        """Gibt einen zufälligen Wurf zurück.

        Zum generieren der Werte wird self.rng verwendet."""
        return Throw(self.rng.randint(1, 6), self.rng.randint(1, 6))
