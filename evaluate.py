"""Spielevaluation

Dient zum wiederholten durchführen eines Games und zur Auswertung"""

import copy
from contextlib import suppress

from gamelog import GameLog
from gameevent import EventKick
from player import Player, DummyPlayer, ShowOffPlayer
from game import Game
from gameevent import KICK_REASON
from format import formatTable
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

        # Speichert, wie oft jeder Spieler gewonnen hat. Der Index entspricht der id der jeweiligen Spieler.
        self.gamesWon = [0 for _ in range(len(self.players))]
        # Speichert, bei der wievielten Runde ein Spieler gewonnen hat
        self.winRounds = [[] for _ in range(len(self.players))]
        # Speichert, aus welchem Grund der Spieler entfernt wurde
        self.lossReason = [{reason: 0 for reason in KICK_REASON} for _ in range(len(self.players))]

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
                self.evalLog(game)
                
        self.done = True

    def evalLog(self, game: Game):
        winner_id = game.log.winner_id
        self.gamesWon[winner_id] += 1
        self.winRounds[winner_id].append(game.log.countRounds())
        for round in game.log.rounds:
            for event in round:
                if isinstance(event, EventKick):
                    self.lossReason[event.playerId][event.reason] += 1


    def getPlayerStats(self, player_id) -> tuple[float, float]:
        winRate = avgWinRound = 0
        roundsWon = len(self.winRounds[player_id])
        roundsLost = self.repetitions - roundsWon
        lossReason = [0 for _ in KICK_REASON]
        with suppress(ZeroDivisionError):  # contextlib.suppress
            winRate = self.gamesWon[player_id] / self.repetitions
            avgWinRound = sum(self.winRounds[player_id]) / roundsWon
            lossReason = [self.lossReason[player_id][reason] / roundsLost for reason in KICK_REASON]

        return winRate, avgWinRound, *lossReason

    def prettyResults(self) -> str:
        space = 3
        if not self.done:
            return "Simulation hasn't been evaluated yet. Run Evaluation.run() to evaluate."
        prettyString = f"Simulation has been run {self.repetitions} times:\n"
        table = [
            ["player", "win rate", "avg. win round", "loss causes", "", "", ""],
            ["", "", "", "lie", "false acc", "worse", "no rep"]
        ]
        for player in self.players:
            stats = self.getPlayerStats(player.id)[:6]
            table.append([repr(player), *[f"{el:.2f}" for el in stats]])

        prettyString += formatTable(table)
        return prettyString

    def assignIds(self, players) -> None:
        for i, player in enumerate(players):
            player.id = i

