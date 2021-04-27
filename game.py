from player import Player
from throw import Throw, randomThrow
import logging

logging.basicConfig(format='[%(levelname)s] %(message)s', level=logging.INFO)


class Game:
    players: list[Player]  # Liste aller Spieler
    currentPlayer: int  # Index des Spielers der gerade an der Reihe ist
    lastThrowStated: Throw  # Angabe die der letzte Spieler über sein Wurfergebnis gemacht hat
    lastThrowActual: Throw  # Tatsächlicher Wurf des letzten Spielers
    moveCounter: int  # Zählt die Züge
    initialized: bool  # Gibt an, ob das Spiel initialisiert wurde
    running: bool  # Gibt an, ob das Spiel noch läuft

    def __init__(self, players: list[Player]) -> None:
        self.players = players
        self.currentPlayer = 0
        self.lastThrowStated = None
        self.lastThrowActual = None
        self.moveCounter = 0
        self.initialized = False
        self.running = False

    def init(self) -> None:
        # Überprüft, ob genügend Spieler vorhanden sind un initialisiert das Spiel
        if len(self.players) > 1:
            logging.info("Game initialized")
            self.initialized = True
            self.running = True
        else:
            logging.error("Game can't be initialized with only one player.")

    def run(self) -> None:
        # Führt Iterationen des Spiels durch, bis es beendet ist
        while self.running:
            self.move()

        if len(self.players) > 0:
            logging.info(f"Player ? won")  # TODO: IDs to identify players

    def move(self) -> None:
        # Führt eine Iteration des Spiels durch

        if not self.initialized:
            logging.error("Game.move() was called even though the game is not yet initialized")
            return
        if not self.running:
            logging.warning("Game.move() was called even though the game is already over")
            return

        logging.info(f"Round {self.moveCounter}")

        # incrementCurrentPlayer wird auf False gesetzt, sollte ein Spieler gelöscht werden.
        # Dadurch wird currentPlayer am Ende von move() nicht erhöht
        incrementCurrentPlayer = True

        if self.lastThrowStated is None:
            # Erste Runde -> Es gibt keinen Vorgänger
            doubtPred = False
        else:
            # Den Spieler, der an der Reihe ist, fragen, ob er seinen Vorgänger anzweifelt
            doubtPred = self.players[self.currentPlayer].getDoubt(self.lastThrowStated)
            logging.info(f"Player {self.currentPlayer} chose " + ("not " if not doubtPred else "")
                         + "to doubt their predecessor.")

        if doubtPred:
            # Der Spieler zweifelt das vorherige Ergebnis an
            if self.lastThrowStated == self.lastThrowActual:
                # Spieler hat nicht Recht, Vorgänger hat die Wahrheit gesagt
                # Aktuellen Spieler entfernen
                logging.info(f"Previous player was wrongfully doubted, Player {self.currentPlayer} will be removed")
                self.players.pop(self.currentPlayer)
                incrementCurrentPlayer = False
            else:
                # Spieler hat Recht, Vorgänger hat gelogen
                # Vorherigen Spieler entfernen
                logging.info(
                    f"Previous player was rightfully doubted, Player {(self.currentPlayer - 1) % len(self.players)} will be removed")
                self.players.pop(self.currentPlayer - 1)
                incrementCurrentPlayer = False

            # Nachdem ein Spieler entfernt wurde, beginnt die Runde von neuem, d.h. der nächste Spieler
            # kann irgendein Ergebnis würfeln und musst niemanden überbieten
            logging.info("Value to be beaten is reset.")
            self.lastThrowStated = None
            self.lastThrowActual = None
        else:
            # Der Spieler akzeptiert das vorherige Ergebnis, würfelt selber und verkündet das Ergebnis
            # Zufälligen Wurf generieren
            currentThrow = randomThrow()
            logging.info(f"Player {self.currentPlayer} threw {str(currentThrow)}")
            # Den Spieler, der an der Reihe ist, nach dem Wurf fragen, den er angeben will
            throwStated = self.players[self.currentPlayer].getThrowStated(currentThrow, self.lastThrowStated)
            logging.info(f"Player {self.currentPlayer} states they threw {throwStated}")
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
                    self.players.pop(self.currentPlayer)
                    incrementCurrentPlayer = False

        if len(self.players) == 0:
            # Dieser Zustand (kein Spieler mehr übrig) sollte nicht eintreten.
            # Das Spiel ist bereits vorbei, wenn nur ein Spieler übrig bleibt.
            logging.warning("Zero players left, game is over. (How did we get here?)")
            self.running = False
        elif len(self.players) == 1:
            # Spiel ist vorbei
            logging.info(f"One player left, game is over")
            self.running = False
        else:
            logging.info(f"{len(self.players)} players left")

        # Den Index, der angibt, welcher Spieler an der Reihe ist, nur erhöhen, falls kein Spieler gelöscht wurde
        if incrementCurrentPlayer:
            self.currentPlayer = (self.currentPlayer + 1) % len(self.players)

        self.moveCounter += 1

    def isRunning(self) -> bool:
        return self.running
