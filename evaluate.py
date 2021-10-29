"""Spielevaluation

Dient zum wiederholten durchführen eines Games und zur Auswertung"""

import copy
from contextlib import suppress

from gamelog import GameLog
from gameevent import EventKick
from player import Player, DummyPlayer, ShowOffPlayer
from game import Game
import constants as c


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

    def __init__(self, players: list[Player], repetitions: int, showProgress: bool = False) -> None:
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

        self.showProgress = showProgress

    def run(self) -> None:
        prg = 0
        prg_steps = c.EVAL_PRG_STEPS  
        if self.showProgress:
            print("[" + "." * prg_steps + "]", end="\r")
        for i in range(self.repetitions):
            if int(i/self.repetitions*prg_steps) > prg:
                prg = int(i / self.repetitions * prg_steps)
                if self.showProgress:
                    print("[" + "#"*prg + "."*(prg_steps-prg) + "]", end=("\r" if i<self.repetitions-1 else "\n"))
            game = Game(self.players)
            game.init()
            game.run()
            if game.isRunning():
                print("Error: Game is still running but should have stopped.")
            else:
                winner_id = game.log.winner_id
                self.gamesWon[winner_id] += 1
                self.winRounds[winner_id].append(game.log.countRounds())

        self.done = True

    def getPlayerStats(self, player_id) -> tuple[float, float]:
        winRate = avgWinRound = 0
        with suppress(ZeroDivisionError):  # contextlib.suppress
            winRate = self.gamesWon[player_id] / self.repetitions
            avgWinRound = sum(self.winRounds[player_id]) / len(self.winRounds[player_id])
        return winRate, avgWinRound

    def prettyResults(self) -> str:
        space = 3
        if not self.done:
            return "Simulation hasn't been evaluated yet. Run Evaluation.run() to evaluate."

        playerNameStrings = [repr(player) for player in
             self.players]
        maxPlayerLen = max([len(pStr) for pStr in playerNameStrings])
        prettyList = [f"Simulation has been run {self.repetitions} times:", "Player" + " "*(maxPlayerLen + 2*space - 5) + "win rate  avg. win round"]

        for pName, p in zip(playerNameStrings, self.players):
            prettyList.append("{} {}{:.2f}      {:.2f}".format(
                pName,
                ' '*((maxPlayerLen - len(pName)) % 2) + '. ' * (int((maxPlayerLen - len(pName))/2) + space),
                *self.getPlayerStats(p.id)[:2])
            )

        return "\n".join(prettyList)

    def assignIds(self, players) -> None:
        for i, player in enumerate(players):
            player.id = i

