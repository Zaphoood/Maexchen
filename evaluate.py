"""Spielevaluation

Dient zum wiederholten durchführen eines Games und zur Auswertung"""

import copy
import time
from contextlib import suppress
import logging
from typing import List, Tuple, Dict, Optional, Union

from gameevent import EventKick
from player import Player
from game import Game
from gameevent import KICK_REASON
from formatting import formatTable, printProgress
from disk import writeLog
from plot import plotWinRate, plotLossReason, plotWRandLR
import constants as c


class IncompleteLogError(Exception):
    pass


class Evaluation:
    """Führt wiederholte Spielsimulationen durch."""

    def __init__(self, players: List[Player], n_repetitions: int, showProgress: bool = False, deepcopy: bool = True) -> None:
        """
        :param players: Liste der Spielerklassen die simuliert werden sollen
        :param n_repetitions: Anzahl der Durchführungen der Simulation
        """

        # Verhindern, dass alle Spieler Referenzen zum selben Objekt sind
        # Das kann passieren, wenn eine Liste durch "list = [element] * integer" erstellt wird
        self.players = [copy.copy(p) for p in players] if deepcopy else players
        self.n_repetitions = n_repetitions
        self.assignIds(self.players)
        for player in self.players:
            player.onInit(self.players)

        # Speichert, wie oft jeder Spieler gewonnen hat. Der Index entspricht der id der jeweiligen Spieler.
        self.gamesWon = [0 for _ in range(len(self.players))]
        # Store the indexes of the moves at which the player won
        self.winRounds: Dict[Optional[int], List[int]] = {p.id: [] for p in self.players}
        # Store how many times the player was kicked for each reason
        self.lossReason: Dict[Optional[int], Dict[KICK_REASON, int]] = {p.id: {reason: 0 for reason in KICK_REASON} for p in self.players}

        self.done = False
        self._prettyResultsCached: Optional[str] = None

        self.showProgress = showProgress

        self.t_start: float = -1.0  # Zeitpunkt an dem die Simulation gestartet wurde
        self.t_end: float = -1.0

    def run(self) -> None:
        if len(self.players) < 2:
            logging.warning(f"Running evaluation with only {len(self.players)} players.")

        self.t_start = time.time()
        prg = 0
        prg_steps = c.EVAL_PRG_STEPS

        if self.showProgress:
            printProgress(0, prg_steps, end="\r")
        for i in range(self.n_repetitions):
            if self.showProgress:
                if prg < (prg := i * prg_steps // self.n_repetitions):
                    printProgress(prg, prg_steps, end=(
                        "\r" if i < self.n_repetitions - 1 else "\n"))
            # No need to deepcopy here since we already did that in __init__
            game = Game(self.players, deepcopy=False, disableAssignIds=True)
            game.init()
            game.run()
            if game.running:
                logging.warn(
                    "Error: Game is still running but should have stopped.")
            else:
                self.evalLog(game)

        self.t_end = time.time()
        self.done = True

    def evalLog(self, game: Game):
        if (winner_id := game.log.winner_id):
            self.gamesWon[winner_id] += 1
            self.winRounds[winner_id].append(game.log.countRounds())
        for event in game.log.getEvents():
            if isinstance(event, EventKick):
                self.lossReason[event.playerId][event.reason] += 1

    def getPlayerStats(self, player_id) -> Tuple[float, ...]:
        winRate: float = 0.
        avgWinRound: float = 0.
        roundsWon = len(self.winRounds[player_id])
        roundsLost = self.n_repetitions - roundsWon
        lossReasonPerc: List[float] = [0.0 for _ in KICK_REASON]
        with suppress(ZeroDivisionError):  # contextlib.suppress
            winRate = self.gamesWon[player_id] / self.n_repetitions
            avgWinRound = sum(self.winRounds[player_id]) / roundsWon
            lossReasonPerc = [self.lossReason[player_id][reason] / roundsLost for reason in KICK_REASON]

        return winRate, avgWinRound, *lossReasonPerc

    def getWinRates(self) -> List[float]:
        """Die Gewinnraten für alle Spieler zurückgeben."""
        return [self.getPlayerStats(p.id)[0] for p in self.players]

    def getLossReasons(self) -> List[Tuple[float, ...]]:
        """Die Gründe fürs Ausscheiden für alle Spieler zurückgeben."""
        return [self.getPlayerStats(p.id)[2:] for p in self.players]

    def prettyResults(self, sort_by_winrate=True, force_rerender=False) -> str:
        if force_rerender or self._prettyResultsCached is None:
            self._prettyResultsCached = self._renderPrettyResults(
                sort_by_winrate=sort_by_winrate)

        return self._prettyResultsCached

    def _renderPrettyResults(self, sort_by_winrate=True) -> str:
        assert self.done
        space = 3
        output = f"Ran simulation in {self.t_end-self.t_start:.3f} seconds\n"
        table: List[List[str]] = [
                ["player", "win rate", "avg. win move", "loss causes", "", "", ""],
                ["", "", "", "lie", "false acc", "worse", "no rep"]
        ]
        player_stats: List[Tuple[str, Tuple[float, ...]]] = [(repr(p), self.getPlayerStats(p.id)[:6]) for p in self.players]
        if sort_by_winrate:
            # Sort by first element of the stats tuple, which is win rate
            player_stats.sort(key=lambda row: row[1][1], reverse=True) # type: ignore
        player_stats_formatted = [[name, *[f"{el:.2f}" for el in stats]] for name, stats in player_stats]
        table.extend(player_stats_formatted)
        output += formatTable(table)
        return output

    def saveResultsToDisk(self):
        assert self.done
        writeLog(self.t_start, self.players,
                 self.n_repetitions, self.prettyResults())

    def plotWinRate(self):
        # Using plot.plotWinRate
        plotWinRate(
            [f"{p.__class__.__name__} {p.id}" for p in self.players], self.getWinRates())

    def plotLossReason(self):
        # Using plot.plotLossReason
        plotLossReason(
            [f"{p.__class__.__name__} {p.id}" for p in self.players], self.getLossReasons())

    def plotWRandLR(self):
        # Using plot.plotWRandLR
        player_names = [f"{p.__class__.__name__} {p.id}" for p in self.players]
        plotWRandLR(player_names, self.getWinRates(), self.getLossReasons())

    def assignIds(self, players) -> None:
        for i, player in enumerate(players):
            player.id = i

