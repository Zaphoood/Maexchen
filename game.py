from player import Player
from throw import Throw, randomThrow
import constants as c


class Game:
    players: list[Player]  # Liste aller Spieler
    currentPlayer: int  # Index des Spielers der gerade an der Reihe ist
    lastThrowStated: Throw  # Angabe die der letzte Spieler über sein Wurfergebnis gemacht hat
    lastThrowActual: Throw  # Tatsächlicher Wurf des letzten Spielers
    moveCounter: int  # Zählt die Züge
    running: bool  # Gibt an, ob das Spiel noch läuft

    def __init__(self, players: list[Player]):
        self.players = players
        self.currentPlayer = 0
        self.lastThrowStated = None
        self.lastThrowActual = None
        self.moveCounter = 0

    def move(self) -> None:
        # Führt eine Iteration des Spiels durch

        # incrementCurrentPlayer wird auf False gesetzt, sollte ein Spieler gelöscht werden.
        # Dadurch wird currentPlayer am Ende von move() nicht erhöht
        incrementCurrentPlayer = True

        # Zufälligen Wurf generieren
        currentThrow = randomThrow()
        # Den Spieler, der an der Reihe ist, nach seinem Zug fragen
        move = self.players[self.currentPlayer].getMove(currentThrow, self.lastThrowStated)
        # Den Zug auswerten
        if move.move == c.ALL_MOVES.THROW:
            # Der Spieler akzeptiert das vorherige Ergebnis, würfelt selber und verkündet das Ergebnis
            # Überprüfen, ob der Spieler die Angabe seines Vorgängers überboten hat
            if self.lastThrowStated is None:
                # Es gibt keinen Vorgänger
                lastThrowStated = move.value
                lastThrowActual = currentThrow
            else:
                if move.value > self.lastThrowStated:
                    # Vorgänger wurde überboten
                    # Den angegebenen und tatsächlichen Wurf für die nächste Runde speichern
                    lastThrowStated = move.value
                    lastThrowActual = currentThrow
                else:
                    # Vorgänger wurde nicht überboten
                    self.players.pop(self.currentPlayer)
                    incrementCurrentPlayer = False
        elif move.move == c.ALL_MOVES.DOUBT:
            # Der Spieler zweifelt das vorherige Ergebnis an
            if self.lastThrowStated == self.lastThrowActual:
                # Spieler hat nicht Recht, Vorgänger hat die Wahrheit gesagt
                # Spieler entfernen
                self.players.pop(self.currentPlayer)
                incrementCurrentPlayer = False
            else:
                # Vorherigen Spieler entfernen
                self.players.pop((self.currentPlayer - 1) % len(self.players))
                incrementCurrentPlayer = False
        else:
            raise ValueError(f"Unknown move {move.move}")

        if len(self.players) == 1:
            # Spiel ist vorbei
            self.running = False

        # Den Index, der angibt, welcher Spieler an der Reihe ist, nur erhöhen, falls kein Spieler gelöscht wurde
        if incrementCurrentPlayer:
            self.currentPlayer += 1

    def isRunning(self) -> bool:
        return self.running
