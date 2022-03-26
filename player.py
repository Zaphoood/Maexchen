# Necessary for type hints of methods that include their own class
from __future__ import annotations
from typing import List, Optional
import random

import constants as c
import gameevent
from throw import Throw
from utils import probLT, probGE


class PlayerNotInitialized(Exception):
    pass


class Player:
    """Base class for all players"""

    # A player's id is necessary to identify it, since players don't have a fixed position in the
    # array that Game stores them in. It must be unique among all players of a game, and is assigned
    # by the Game this Player corresponds to.
    # TODO: This might not be necessary anymore since the order of players during a game
    # doesn't change
    id: Optional[int]

    def __init__(self, player_id: int = None, listens_to_events: bool = False):
        self.id = player_id
        # Whether this instances onEvent() should be called by Game
        self.listens_to_events = listens_to_events
        # Whether the instances onInit() method has been called
        self._initialized: bool = False

    def __str__(self):
        return f"{self.__class__.__name__} with id {self.id}"

    def __repr__(self):
        return f"<{self.__class__.__name__} (id={self.id})>"

    def getDoubt(self, lastThrow: Throw, iMove: int, rng: random.Random) -> Optional[bool]:
        """Ask the player whether they doubt the previous player

        :param lastThrow: The previous player's throw
        :param iMove: The index of the move of the game
        """
        raise NotImplementedError

    def getThrowStated(self, myThrow: Throw, lastThrow: Optional[Throw], iMove: int, rng: random.Random) -> Optional[Throw]:
        """Return the throw to tell to the other players (this might not be the actual throw -- players are allowed to lie)

        :param myThrow: This instances throw
        :param lastThrow: The previous Player's throw
        :param iMove: The index of the move of the game
        """
        raise NotImplementedError

    def onInit(self, players: list[Player]) -> None:
        """Is called at the start of an Evaluation.

        :param players: List of all players in the Evaluation
        """
        self._initialized = True

    def onEvent(self, event: gameevent.Event) -> None:
        """Is called by Game on every event that occurs.

        :param event: The event that has occurred
        """
        pass

    @property
    def initialized(self) -> bool:
        return self._initialized

    def _assertInitialized(self) -> None:
        """Raise an Exception if the instance has not been initialized.

        Player instances can be initialized by calling the onInit() method."""
        if not self._initialized:
            raise PlayerNotInitialized()


class DummyPlayer(Player):
    """Very basic player model.

    Trusts all results except Mäxchen.
    Only lies if necessary, that is, if DummyPlayer's throw doesn't beat the previous one.
    Otherwise just tells the truth.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def getDoubt(self, lastThrow: Throw, iMove: int, rng: random.Random) -> Optional[bool]:
        if lastThrow.isMaexchen:
            return True
        else:
            return False

    def getThrowStated(self, myThrow: Throw, lastThrow: Optional[Throw], iMove: int, rng: random.Random) -> Optional[Throw]:
        if lastThrow is None:
            # No need to beat the last throw
            return myThrow
        else:
            if myThrow > lastThrow:
                # Our throw beats previous one
                return myThrow
            else:
                # Doesn't beet previous throw
                # Just state we threw the next highest Throw
                return lastThrow + 1

class AdvancedDummyPlayer(Player):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def getDoubt(self, lastThrow: Throw, iMove: int, rng: random.Random) -> Optional[bool]:
        if lastThrow.isMaexchen or lastThrow == Throw(66):
            return True
        else:
            return False

    def getThrowStated(self, myThrow: Throw, lastThrow: Optional[Throw], iMove: int, rng: random.Random) -> Optional[Throw]:
        if lastThrow is None or myThrow > lastThrow:
            return myThrow
        else:
            if lastThrow == Throw(66):
                return Throw(21)
            else:
                return Throw(rng.choice(c.THROW_VALUES[lastThrow.rank + 1:-1]))

class CounterDummyPlayer(Player):
    """Designed to exploit the flaws in DummyPlayer's strategy"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, listens_to_events=True, **kwargs)

        # Store last and second to last Throw so that
        # we can deduce the previous players strategy
        self.lastThrow = None
        self.secondLastThrow = None

    def onEvent(self, event: gameevent.Event) -> None:
        if isinstance(event, gameevent.EventThrow):
            self.secondLastThrow = self.lastThrow
            self.lastThrow = event.throw_stated
        elif isinstance(event, gameevent.EventKick):
            self.lastThrow = self.secondLastThrow = None

    def getDoubt(self, lastThrow: Throw, iMove: int, rng: random.Random) -> Optional[bool]:
        if lastThrow.isMaexchen:
            return True
        elif self.secondLastThrow is not None and lastThrow == self.secondLastThrow + 1:
            # Last Throw is exactly one above the one before that, which means that the last player
            # is likely to be a DummyPlayer
            return True
        else:
            return False

    def getThrowStated(self, myThrow: Throw, lastThrow: Optional[Throw], iMove: int, rng: random.Random) -> Optional[Throw]:
        if lastThrow is None or myThrow > lastThrow:
            return myThrow
        else:
            # If forced to lie, announced 66 as the Throw value. The next player must then announce 21 (Mäxchen),
            # so that the one after that will most like doubt them, since Mäxchen can't be beaten
            return Throw(66)

class ShowOffPlayer(Player):
    """A real show-off.

    Always announces that they threw a double or Mäxchen, except if the predecessor happened
    to throw Mäxchen.
    """

    def __init__(self, player_id=None) -> None:
        super().__init__(player_id)

    def getDoubt(self, lastThrow: Throw, iMove:int, rng: random.Random) -> Optional[bool]:
        if lastThrow.isMaexchen:
            return True
        else:
            return False

    def getThrowStated(self, myThrow: Throw, lastThrow: Optional[Throw], iMove: int, rng: random.Random) -> Optional[Throw]:
        #Randomly choose a double or Mäxchen in order to beat the previous player
        rank_11 = c.THROW_RANK_BY_VALUE[11]
        if lastThrow is None:
            return Throw(random.choice(c.THROW_VALUES[rank_11:]))
        else:
            return Throw(random.choice(c.THROW_VALUES[max(lastThrow.rank + 1, rank_11):]))


class RandomPlayer(Player):
    """Acts completely randomly"""

    def __init__(self, *args, doubtChance: float = 0.5, **kwargs):
        super().__init__(*args, **kwargs)
        self.doubtChance = doubtChance

    def getDoubt(self, lastThrow: Throw, iMove: int, rng: random.Random) -> Optional[bool]:
        return rng.random() < self.doubtChance

    def getThrowStated(self, myThrow: Throw, lastThrow: Optional[Throw], iMove: int, rng: random.Random) -> Optional[Throw]:
        return Throw(rng.choice(c.THROW_VALUES))


class ThresholdPlayer(Player):
    """Doubts or trusts depending on certain constant thresholds.

    If the last players throw is greater than or equal to `doubtThreshold`, they are doubted.
    If our own throw is higher than the last throw but lower than `lieThreshold`, we lie and
    announce we threw `lieThreshold`. Therefore, we never state anything than that threshold
    as our throw.
    """
    
    def __init__(self, player_id: int = None, doubtThreshold: int = 61, lieThreshold: int = 61):
        super().__init__(player_id)
        if isinstance(doubtThreshold, int):
            self.doubtThreshold = Throw(doubtThreshold)
        elif isinstance(doubtThreshold, Throw):
            self.doubtThreshold = doubtThreshold
        else:
            raise TypeError(f"doubtThreshold must be of type int or Throw (got {type(doubtThreshold)})")
        if isinstance(lieThreshold, int):
            self.lieThreshold = Throw(lieThreshold)
        elif isinstance(lieThreshold, Throw):
            self.lieThreshold = lieThreshold
        else:
            raise TypeError(f"lieThreshold must be of type int or Throw (got {type(lieThreshold)})")

    def getDoubt(self, lastThrow: Throw, iMove: int, rng: random.Random) -> Optional[bool]:
        if self.doubtThreshold:
            return lastThrow >= self.doubtThreshold
        else:
            return lastThrow.isMaexchen

    def getThrowStated(self, myThrow: Throw, lastThrow: Optional[Throw], iMove: int, rng: random.Random) -> Optional[Throw]:
        if lastThrow is None or myThrow > lastThrow:
            if myThrow <= self.lieThreshold:
                return self.lieThreshold
            else:
                return myThrow
        else:
            # Anderer Zug
            return lastThrow + 1

class CounterThresPlayer(Player):
    """Designed to exploit the flaws in ThresholdPlayer's strategy

    Stores the results other players announce, in order to detect a pattern.
    If a player is suspected to be a ThresPlayer, then any throw they announce
    which corresponds to their supposed threshold is doubted.
    """

    def __init__(self, *args, minDataPoints=5, freqThres=0.5, **kwargs):
        super().__init__(*args, listens_to_events=True, **kwargs)

        # Statistic about the frequency of other players throws
        # { player0Id: [0, 0, 0, 0, ..., 0],
        #   player1Id: [0, 0, 0, 0, ..., 0],
        #              ^--- 21 entries --^
        # ... }
        self.throwStats: Dict[int, List[int]] = {}
        # The last player to state a throw
        self.lastPlayerId = None

        # Minimum amount of data points to collect before we make an assumption about
        # another player
        self.minDataPoints = minDataPoints
        # Minimum frequency at which a player must announce a certain Throw so that we assume
        # they are a ThresPlayer
        self.freqThres = freqThres

    def onInit(self, players: list[Player]) -> None:
        super().onInit(players)
        # Create empty table for each player
        self.throwStats = {player.id: [0 for _ in range(c.N_THROW_VALUES)] for player in players if player is not self}

    def onEvent(self, event: gameevent.Event) -> None:
        if isinstance(event, gameevent.EventThrow):
            if event.player_id != self.id:
                self.throwStats[event.player_id][event.throw_stated.rank] += 1
                self.lastPlayerId = event.player_id
        elif event.event_type == gameevent.EVENT_TYPES.KICK:
            self.lastPlayerId = None

    def getDoubt(self, lastThrow: Throw, iMove: int, rng: random.Random) -> Optional[bool]:
        if lastThrow.isMaexchen:
            return True
        elif self.existsAssumption(self.lastPlayerId):
            # Decide based on data that was collected about the last player
            if self.mostFreqThrow(self.lastPlayerId)[0] == lastThrow:
                # Last player acted according to assumption 
                return True
        # No assumption exists or it couldn't be confirmed
        return False


    def getThrowStated(self, myThrow: Throw, lastThrow: Optional[Throw], iMove: int, rng: random.Random) -> Optional[Throw]:
        # Same behavior as DummyPlayer
        if lastThrow is None:
            return myThrow
        else:
            if myThrow > lastThrow:
                return myThrow
            else:
                return lastThrow + 1

    def existsAssumption(self, player_id: int):
        """Assess whether the data collected about a player is meaningful enough to make an assumption.

        Requirements are:
         * Enough data points have been collected
         * The frequency of the most frequent throw is above a certain threshold
         * The player has a max frequency for just one Throw

        :param player_id: The ID of the player to assess
        """
        return self.totalThrowsTracked(player_id) > self.minDataPoints\
                and self.mostFreqThrowFreq(player_id) > self.freqThres\
                and len(self.mostFreqThrowIndices(player_id)) == 1

    def mostFreqThrowIndices(self, player_id: int) -> List[int]:
        """Return the indices of the most frequent throw(s) of a player.
        
        The index of a throw in table which holds the statistics about a player
        corresponds to the rank of that throw."""
        p_stats = self.throwStats[player_id]
        max_freq = max(p_stats)
        return [i for i, freq in enumerate(p_stats) if freq == max_freq]

    def mostFreqThrow(self, player_id: int) -> List[int]:
        """Return the values of the most frequent throw(s) of a player"""
        return [c.THROW_VALUES[index] for index in self.mostFreqThrowIndices(player_id)]

    def mostFreqThrowFreq(self, player_id: int) -> float:
        """Calculate the frequency of a players most frequent throw"""
        # Avoid ZeroDivision by checking total number of tracked throws first
        if (total_throws := self.totalThrowsTracked(player_id)):
            return max(self.throwStats[player_id]) / total_throws
        else:
            # No data collected for this specific player
            return 0.0

    def totalThrowsTracked(self, player_id: int) -> int:
        """Count the number of data points collected about a player"""
        return sum(self.throwStats[player_id])

class TrackingPlayer(Player):
    """Tracks other players tendency to tell the truth or lie"""

    def __init__(self, *args, credLevel=0.5, **kwargs):
        super().__init__(*args, listens_to_events=True, **kwargs)

        # Statistic about other player's truthfulness
        # {player0Id: [count_truths, count_lies],
        # {player1Id: [count_truths, count_lies],
        #  ...}
        self.playerStats: Dict[int, List[int]] = {}
        # Store last and second to last Throw so that
        # we can deduce the previous players strategy
        self.lastThrow: Optional[Throw] = None
        self.secondLastThrow: Optional[Throw] = None
        # The last player to state a throw
        self.lastPlayerId: Optional[int] = None
        # Level of credibility which another player must at least have so that we trust them
        # if there are no other data points (this is the case if the last player had no value to beat)
        self.credLevel = credLevel

    def getDoubt(self, lastThrow: Throw, iMove: int, rng: random.Random) -> Optional[bool]:
        if lastThrow.isMaexchen:
            return True
        else:
            return self.shouldDoubt(lastThrow)

    def getThrowStated(self, myThrow: Throw, lastThrow: Optional[Throw], iMove: int, rng: random.Random) -> Optional[Throw]:
        if lastThrow is None or myThrow > lastThrow:
            return myThrow
        else:
            return lastThrow + 1

    def onInit(self, players: list[Player]) -> None:
        super().onInit(players)
        # Create empty table for each player
        self.playerStats = {player.id: [0, 0] for player in players if player is not self}

    def onEvent(self, event: gameevent.Event) -> None:
        if isinstance(event, gameevent.EventThrow):
            self.secondLastThrow = self.lastThrow
            self.lastThrow = event.throw_stated
            self.lastPlayerId = event.player_id
        if isinstance(event, gameevent.EventKick):
            if event.reason == gameevent.KICK_REASON.LYING:
                if event.player_id != self.id:
                    self.trackPlayerLie(event.player_id)
            elif event.reason == gameevent.KICK_REASON.FALSE_ACCUSATION:
                if self.lastPlayerId != self.id:
                    self.trackPlayerTruth(self.lastPlayerId)
            self.lastThrow = self.secondLastThrow = self.lastPlayerId = None

    def trackPlayerLie(self, player_id: int) -> None:
        """Track that the last player lied"""
        self._savePlayerStat(player_id, 1)

    def trackPlayerTruth(self, player_id: int) -> None:
        """Track that the last player told the truth"""
        self._savePlayerStat(player_id, 0)

    def _savePlayerStat(self, player_id: int, event: int) -> None:
        """Store an event regarding a player.

        An event can be either that player lying or telling the truth.

        :param player_id: The ID of the player
        :param event: What the player did: 0 = telling the truth, 1 = lying
        """
        self._assertInitialized()
        self.playerStats[player_id][event] += 1

    def getPlayerCredibility(self, player_id: int) -> float:
        """Calculate a players credibility.

        It is calculated with
            credibility = count_truths / (count_truths + count_lies)

        :param player_id: The ID of the player
        """
        truths, lies = self.playerStats[player_id]
        return truths / (truths + lies) if self.existPlayerStats(player_id) else None 

    def existPlayerStats(self, player_id: int) -> bool:
        """Check if there has been any data collected at all about a player

        :param player_id: The ID of the player
        """
        if player_id in self.playerStats:
            return any(self.playerStats[player_id])
        else:
            # TODO: This should be unreachable, maybe throw an Exception instead
            # If this block is reached, that must be a bug
            return False

    def shouldDoubt(self, playerThrow: Throw) -> bool:
        # TODO: Translate this docstring into english
        """Assess whether the last player should be mistrusted.

        Das geschieht auf folgende Weise: Zuerst wird die Wahrscheinlichkeit, dass der Spieler lügt,
        eingeschätzt. Diese errechnet sich aus der Wahrscheinlichkeit, den vorletzten Wurf mit einem zufälligen
        Wurf zu übertreffen, mal der Tendenz des Spielers, zu lügen (1 - Glaubwürdigkeit), plus die Wahrscheinlichkeit,
        den vorletzten Wurf mit einem zufälligen Wurf nicht zu übertreffen.
            P_Lüge = P_zufällig_erreichen(Vorletzter Wurf) * P_Lüge + P_nicht_zufällig_erreichen
        Anschließend wird die Wahrscheinlichkeit, dass der Spieler die Wahrheit sagt, eingeschätzt:
        Wahrscheinlichkeit, den vorletyten Wurf mit einem zufällgien Wurf zu übertreffen mal der Wahrscheinlichkeit,
        dass der Spieler die Wahrheit sagt.
            P_Wahrheit = P_zufällig_erreichen(Vorletzter Wurf) * P_Wahrheit

        :param playerThrow: Wurf des vorherigen Spielers"""
        if self.secondLastThrow is None:
            # Second move after resetting of value to beat
            if self.existPlayerStats(self.lastPlayerId):
                return self.getPlayerCredibility(self.lastPlayerId) > self.credLevel
            else:
                return False

        else:
            # Any other move
            if self.existPlayerStats(self.lastPlayerId):
                p_lie = probGE(self.secondLastThrow) * (1 - self.getPlayerCredibility(self.lastPlayerId)) + probLT(self.secondLastThrow) 
                p_truth = probGE(self.secondLastThrow) * self.getPlayerCredibility(self.lastPlayerId)
            else:
                p_lie = probGE(self.secondLastThrow)
                p_truth = probLT(self.secondLastThrow)

            return p_lie > p_truth


# Map command line flags to Player classes
FLAGS_TO_PLAYERS = {
    "dummy": DummyPlayer,
    "c-dummy": CounterDummyPlayer,
    "show-off": ShowOffPlayer,
    "random": RandomPlayer,
    "thres": ThresholdPlayer,
    "threshold": ThresholdPlayer,
    "c-thres": CounterThresPlayer,
    "tracking": TrackingPlayer,
    "adv-dummy": AdvancedDummyPlayer
}
