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
    """Run Games repeatedly"""

    def __init__(self, players: List[Player], n_repetitions: int, show_progress: bool = False, deepcopy: bool = True) -> None:
        """
        :param players: List of player instances to simulate
        :param n_repetitions: Number of games to simulate
        """

        # TODO: This isn't really needed anymore
        # Verhindern, dass alle Spieler Referenzen zum selben Objekt sind
        # Das kann passieren, wenn eine Liste durch "list = [element] * integer" erstellt wird
        self.players = [copy.copy(p) for p in players] if deepcopy else players
        self.n_repetitions = n_repetitions
        self.assignIds(self.players)
        for player in self.players:
            player.onInit(self.players)

        # Speichert, wie oft jeder Spieler gewonnen hat. Der Index entspricht der id der jeweiligen Spieler.
        self.games_won = [0 for _ in range(len(self.players))]
        # Store the indexes of the moves at which the player won
        self.win_rounds: Dict[Optional[int], List[int]] = {p.id: [] for p in self.players}
        # Store how many times the player was kicked for each reason
        self.loss_reason: Dict[Optional[int], Dict[KICK_REASON, int]] = {p.id: {reason: 0 for reason in KICK_REASON} for p in self.players}

        self.done = False
        self._pretty_results_cached: Optional[str] = None

        self.show_progress = show_progress

        self.t_start: float = -1.0  # Zeitpunkt an dem die Simulation gestartet wurde
        self.t_end: float = -1.0

    def run(self) -> None:
        if len(self.players) < 2:
            logging.warning(f"Running evaluation with only {len(self.players)} players.")

        self.t_start = time.time()
        prg = 0
        prg_steps = c.PROGRESS_BAR_WIDTH

        if self.show_progress:
            printProgress(0, prg_steps, end="\r")
        for i in range(self.n_repetitions):
            if self.show_progress:
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
            self.games_won[winner_id] += 1
            self.win_rounds[winner_id].append(game.log.countRounds())
        for event in game.log.getEvents():
            if isinstance(event, EventKick):
                self.loss_reason[event.playerId][event.reason] += 1

    def getPlayerStats(self, player_id) -> Tuple[float, ...]:
        win_rate: float = 0.
        average_win_round: float = 0.
        rounds_won = len(self.win_rounds[player_id])
        loss_reasons_freq: List[float] = [0.0 for _ in KICK_REASON]
        rounds_lost = self.n_repetitions - rounds_won
        # `if`s are necessary in order to avoid division by zero
        if self.n_repetitions > 0:
            win_rate = self.games_won[player_id] / self.n_repetitions
        if rounds_won > 0:
            average_win_round = sum(self.win_rounds[player_id]) / rounds_won
        if rounds_lost > 0:
            loss_reasons_freq = [self.loss_reason[player_id][reason] / rounds_lost for reason in KICK_REASON]

        # TODO: Unpacking this tuple is bad; just return the tuple itself
        return win_rate, average_win_round, *loss_reasons_freq

    def getWinRates(self) -> List[float]:
        """Return win rate of players"""
        return [self.getPlayerStats(p.id)[0] for p in self.players]

    def getLossReasons(self) -> List[Tuple[float, ...]]:
        """Return frequency for each loss reason of all players"""
        return [self.getPlayerStats(p.id)[2:] for p in self.players]

    def prettyResults(self, force_rerender=False, sort_by_winrate=True) -> str:
        if self._pretty_results_cached is None or force_rerender:
            self._pretty_results_cached = self._renderPrettyResults(
                    sort_by_winrate=sort_by_winrate)
        return self._pretty_results_cached

    def _renderPrettyResults(self, sort_by_winrate=True) -> str:
        """Format simulation results into human-readable text"""
        assert self.done
        pretty_string = f"Ran simulation in {self.t_end-self.t_start:.3f} seconds\n"
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
        pretty_string += formatTable(table)
        return pretty_string

    def saveResultsToDisk(self, log_path=None):
        assert self.done
        # disk.writeLog
        writeLog(self.t_start, self.players,
                 self.n_repetitions, self.prettyResults(), log_path=log_path)

    def plotWinRate(self):
        # plot.plotWinRate
        plotWinRate(
            [f"{p.__class__.__name__} {p.id}" for p in self.players], self.getWinRates())

    def plotLossReason(self):
        # plot.plotLossReason
        plotLossReason(
            [f"{p.__class__.__name__} {p.id}" for p in self.players], self.getLossReasons())

    def plotWRandLR(self):
        # plot.plotWRandLR
        player_names = [f"{p.__class__.__name__} {p.id}" for p in self.players]
        plotWRandLR(player_names, self.getWinRates(), self.getLossReasons())

    def assignIds(self, players) -> None:
        for i, player in enumerate(players):
            player.id = i

