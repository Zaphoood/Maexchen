"""Spielevaluation

Dient zum wiederholten durchführen eines Games und zur Auswertung"""

import copy

from gamelog import GameLog
from gameevent import EventKick
from player import Player, DummyPlayer, ShowOffPlayer
from game import Game


class IncompleteLogError(Exception):
    pass


def getWinner(log: GameLog) -> Player:
    if log.hasFinished():
        playersAlive = log.players
        for kickEvent in [e for e in log.getEvents() if isinstance(e, EventKick)]:
            for i, player in enumerate(playersAlive):
                if player.id == kickEvent.playerId:
                    playersAlive.pop(i)
        if len(playersAlive) == 1:
            return playersAlive[0]
        else:
            raise IncompleteLogError(f"Couldn't determine winner from GameLog. {len(playersAlive)} left at the end of "
                                     f"evaluation.")
    else:
        return None


class Evaluation:
    """Führt wiederholte Spielsimulationen durch."""

    def __init__(self, players: list[Player], repetitions: int, verbose: bool = False) -> None:
        """
        :param players: Liste der Spielerklassen die simuliert werden sollen
        :param repetitions: Anzahl der Durchführungen der Simulation
        """

        # Verhindern, dass alle Spieler Referenzen zum selben Objekt sind
        # Das kann passieren, wenn eine Liste durch "list = [element] * integer" erstellt wird
        self.players = [copy.copy(p) for p in players]
        self.repetitions = repetitions
        self.assignIds(self.players)

        # Speichern, wie oft jeder Spieler gewonnen hat. Der Index entspricht der id der jeweiligen Spieler.
        self.gamesWon = [0 for _ in range(len(self.players))]
        self.winRounds = [[] for _ in range(len(self.players))]

        self.done = False

        self.verbose = verbose

    def run(self) -> None:
        prg_steps = 20
        prg = 0
        if self.verbose:
            print("[" + "." * prg_steps + "]", end="\r")
        for i in range(self.repetitions):
            if int(i/self.repetitions*prg_steps) > prg:
                prg = int(i / self.repetitions * prg_steps)
                if self.verbose:
                    print("[" + "#"*prg + "."*(prg_steps-prg) + "]", end=("\r" if i<self.repetitions-1 else "\n"))
            game = Game(self.players)
            game.init()
            game.run()
            if game.isRunning():
                print("Error: Game is still running but should have stopped.")
            else:
                winner = getWinner(game.log)
                self.gamesWon[winner.id] += 1
                self.winRounds[winner.id].append(game.log.countRounds())

        self.done = True

    def prettyResults(self) -> str:
        if not self.done:
            return "Simulation hasn't been evaluated yet. Run Evaluation.run() to evaluate."

        prettyString = f"Simulation has been run {self.repetitions} times:\nThe players win rates were:\n"
        playerNameStrings = [str(player) for player in
             self.players]
        maxPlayerLen = max([len(pStr) for pStr in playerNameStrings])
        prettyString += "\n".join(
            [f" - {pStr} {' '*((maxPlayerLen - len(pStr)) % 2)}{'. ' * (int((maxPlayerLen - len(pStr))/2) + 3)}{(self.gamesWon[player.id] / self.repetitions) * 100:.2f}%" for pStr, player in
             zip(playerNameStrings, self.players)])

        return prettyString

    def assignIds(self, players) -> None:
        for i, player in enumerate(players):
            player.id = i

