"""Spielevaluation

Dient zum wiederholten durchführen eines Games und zur Auswertung"""

import copy
import time
from contextlib import suppress
import logging

from gameevent import EventKick
from player import Player
from game import Game
from gameevent import KICK_REASON
from format import formatTable
from disk import writeLog
from plot import plotWinRate, plotLossReason, plotWRandLR
import constants as c


class IncompleteLogError(Exception):
    pass


class Evaluation:
    """Führt wiederholte Spielsimulationen durch."""

    def __init__(self, players: list[Player], n_repetitions: int, showProgress: bool = False, disableDeepcopy: bool = False) -> None:
        """
        :param players: Liste der Spielerklassen die simuliert werden sollen
        :param n_repetitions: Anzahl der Durchführungen der Simulation
        """

        if disableDeepcopy:
            self.players = players
        else:
            # Verhindern, dass alle Spieler Referenzen zum selben Objekt sind
            # Das kann passieren, wenn eine Liste durch "list = [element] * integer" erstellt wird
            self.players = [copy.copy(p) for p in players]
        self.n_repetitions = n_repetitions
        self.assignIds(self.players)
        for player in self.players:
            player.onInit(self.players)

        # Speichert, wie oft jeder Spieler gewonnen hat. Der Index entspricht der id der jeweiligen Spieler.
        self.gamesWon = [0 for _ in range(len(self.players))]
        # Speichert, bei der wievielten Runde ein Spieler gewonnen hat
        self.winRounds = [[] for _ in range(len(self.players))]
        # Speichert, aus welchem Grund der Spieler entfernt wurde
        self.lossReason = [{reason: 0 for reason in KICK_REASON} for _ in range(len(self.players))]

        self.done = False
        self._prettyResultsCached = None

        self.showProgress = showProgress

        self.t_start = -1  # Zeitpunkt an dem die Simulation gestartet wurde
        self.t_end = -1

    def run(self) -> None:
        self.t_start = time.time()
        prg = 0
        prg_steps = c.EVAL_PRG_STEPS  
        if self.showProgress:
            print("[" + "." * prg_steps + "]", end="\r")
        for i in range(self.n_repetitions):
            if int(i/self.n_repetitions*prg_steps) > prg:
                prg = int(i / self.n_repetitions * prg_steps)
                if self.showProgress:
                    print("[" + "#"*prg + "."*(prg_steps-prg) + "]", end=("\r" if i<self.n_repetitions-1 else "\n"))
            game = Game(self.players)
            game.init()
            game.run()
            if game.isRunning():
                logging.warn("Error: Game is still running but should have stopped.")
            else:
                self.evalLog(game)

        self.t_end = time.time()
        self.done = True

    def evalLog(self, game: Game):
        winner_id = game.log.winner_id
        self.gamesWon[winner_id] += 1
        self.winRounds[winner_id].append(game.log.countRounds())
        for event in game.log.getEvents():
            if isinstance(event, EventKick):
                self.lossReason[event.playerId][event.reason] += 1

    def getPlayerStats(self, player_id) -> tuple[float, float]:
        winRate = avgWinRound = 0
        roundsWon = len(self.winRounds[player_id])
        roundsLost = self.n_repetitions - roundsWon
        lossReason = [0 for _ in KICK_REASON]
        with suppress(ZeroDivisionError):  # contextlib.suppress
            winRate = self.gamesWon[player_id] / self.n_repetitions
            avgWinRound = sum(self.winRounds[player_id]) / roundsWon
            lossReason = [self.lossReason[player_id][reason] / roundsLost for reason in KICK_REASON]

        return winRate, avgWinRound, *lossReason

    def getWinRates(self) -> list[float]:
        """Die Gewinnraten für alle Spieler zurückgeben."""
        return [self.getPlayerStats(p.id)[0] for p in self.players]

    def getLossReasons(self) -> list[list[float]]:
        """Die Gründe fürs Ausscheiden für alle Spieler zurückgeben."""
        return [self.getPlayerStats(p.id)[2:] for p in self.players]

    def prettyResults(self, sort_by_winrate=True, force_rerender=False) -> str:
        if force_rerender or not self._prettyResultsCached:
            self._prettyResultsCached = self._renderPrettyResults(sort_by_winrate=sort_by_winrate)

        return self._prettyResultsCached

    def _renderPrettyResults(self, sort_by_winrate=True) -> str:
        if not self.assertFinished():
            return
        space = 3
        output = f"Ran simulation in {self.t_end-self.t_start:.3f} seconds\n"
        table = [
                ["player", "win rate", "avg. win move", "loss causes", "", "", ""],
                ["", "", "", "lie", "false acc", "worse", "no rep"]
                ]
        players_stats = []
        for player in self.players:
            stats = self.getPlayerStats(player.id)[:6]
            players_stats.append([repr(player), *stats])
        if sort_by_winrate:
            players_stats.sort(key=lambda row: row[1], reverse=True)
        players_stats = [[row[0], *[f"{el:.2f}" for el in row[1:]]] for row in players_stats]
        table.extend(players_stats)
        output += formatTable(table)
        return output

    def saveResultsToDisk(self):
        if not self.assertFinished():
            return
        writeLog(self.t_start, self.players, self.n_repetitions, self.prettyResults())

    def plotWinRate(self):
        # Using plot.plotWinRate
        plotWinRate([f"{p.__class__.__name__} {p.id}" for p in self.players], self.getWinRates())
        
    def plotLossReason(self):
        # Using plot.plotLossReason
        plotLossReason([f"{p.__class__.__name__} {p.id}" for p in self.players], self.getLossReasons())

    def plotWRandLR(self):
        # Using plot.plotWRandLR
        player_names = [f"{p.__class__.__name__} {p.id}" for p in self.players]
        plotWRandLR(player_names, self.getWinRates(), self.getLossReasons())
        
    def assignIds(self, players) -> None:
       for i, player in enumerate(players):
           player.id = i

    def assertFinished(self) -> bool:
        if not self.done:
            logging.warning("Simulation hasn't been evaluated yet. Run Evaluation.run() to evaluate.")
            return False
        else:
            return True


