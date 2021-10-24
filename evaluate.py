"""Spielevaluation

Dient zum wiederholten durchführen eines Games und zur Auswertung"""

import copy

from gamelog import GameLog
from gameevent import EventKick
from player import Player, DummyPlayer
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

    def __init__(self, players: list[Player], repetitions: int) -> None:
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
        print(self.winRounds)

        self.done = False

    def run(self) -> None:
        for i in range(self.repetitions):
            game = Game(self.players)
            game.init()
            game.run()
            if game.isRunning():
                print("Error: Game is still running but should have stopped.")
            else:
                winner = getWinner(game.log)
                self.gamesWon[winner.id] += 1

        self.done = True

    def prettyResults(self):
        if not self.done:
            return "Simulation hasn't been evaluated yet. Run Evaluation.run() to evaluate."

        prettyString = f"Simulation has been run {self.repetitions} times:\nThe players win rates were:"
        prettyString += "\n".join(
            [f" - {str(player)} | {(self.gamesWon[player.id] / self.repetitions) * 100:.2f}%" for player in
             self.players])

    def assignIds(self, players) -> None:
        for i, player in enumerate(players):
            player.id = i

if __name__ == '__main__':
    eval = Evaluation([DummyPlayer() for _ in range(3)], 1000)
