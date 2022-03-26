import logging
from copy import copy
from random import Random, randrange
from sys import maxsize
from contextlib import suppress
from typing import List, Set, Optional

from gamelog import GameLog
import gameevent
from player import Player
from throw import Throw, NoneThrow

class TooFewPlayers(Exception):
    """Is raised when too few players have been provided to the Game class"""
    n_players: Optional[int]
    message: str

    def __init__(self, *args, message: str = "") -> None:
        if not args:
            self.n_players = None
            self.message = message or "Too few players for simulation"
        else:
            with suppress(ValueError):  # contextlib.suppress
                self.n_players = args[0]
            self.message = message or f"{self.n_players} player(s) is too few for a simulation."

class DuplicateId(Exception):
    pass

class Game:
    """Implement the rules of the game.  """ 

    players: List[Player]  # All players participating in the game
    alive_players: List[bool] # For each player, store if they are still in the game (i. e. if they're 'alive')
    current_player: int  # Index of the player who's turn it is currently
    last_throw_actual: Optional[Throw] # The result the last player actually threw
    last_throw_stated: Optional[Throw] # The result the last player said they threw
    moveCounter: int
    _initialized: bool
    _running: bool
    # Log for tracking everything that happens in a game
    log: GameLog
    # Pseudo-random number generator
    rng: Random # random.Random

    def __init__(self, players: List[Player], seed: int = None, shuffle_players: bool = True, disable_assign_ids: bool = False) -> None:
        self.players = players
        self.alive_players = [True for _ in self.players]
        if disable_assign_ids:
            # If assigning unique IDs was disabled, check if the ones the players have are unique
            # If they are not, exit
            if not self.checkUniqueIds():
                raise DuplicateId()
        else:
            # Assign a unique Id to each player
            self.assignIds()
        # Index of the current move
        self.move_index = -1 
        self.last_throw_stated = None
        self.last_throw_actual = None
        self._initialized = False
        self._running = False

        self.log = GameLog(self.players)

        # Initialize PRNG. Use seed if specified, otherwise generate a new seed.
        # The important part is not the randomness source but that the seed is known
        # so that the game can be reproduced later.
        self._seed = seed if seed else randrange(maxsize) # random.randrange, sys.maxsize
        self.rng = Random(self._seed)

        # Yes, the order of self.players changes, while self.alive_players stays the same.
        # This does not introduce any discrepancy because at this point all players are alive anyway.
        # Though, the order of neither of those lists must change throughout the game!
        if shuffle_players:
            self.rng.shuffle(self.players)

    @property
    def running(self) -> bool:
        return self._running

    @property
    def seed(self) -> int:
        return self._seed

    @property
    def initialized(self) -> int:
        return self._initialized
 
    def init(self) -> None:
        """Initialize the game.

        First, check if there are enough players, otherwise raise an Exception.
        Then, set some flags and select a random player to start the game.
        """
        if len(self.players) == self.countAlivePlayers() > 1:
            logging.info("=== Game initialized ===")
            self.current_player = self.rng.randrange(0, len(self.players))
            self._initialized = True
            self._running = True
        else:
            self.happen(gameevent.EventAbort(message="Too few players for game (at least 2 are required)"))
            raise TooFewPlayers(len(self.players))

    def run(self) -> None:
        """Perform moves until the game has finished"""
        if not self.initialized:
            logging.error("Game.run() was called even though the game is not yet initialized")
            return
        while self._running:
            self.move()

    def move(self) -> None:
        """Perform a move.

        Check if a move is possible, interact with the player, then check if the game is over.
        Otherwise increment the pointer (it's not actually a pointer but rather an index)
        to the current player.
        """

        if not self.initialized:
            logging.error("Game.move() was called even though the game is not yet initialized")
            return
        if not self._running:
            logging.warning("Game.move() was called even though the game is already over")
            return

        self.move_index += 1
        logging.info(f"Move {self.move_index} | {self.countAlivePlayers()} players left")
        self.log.newRound()
        self.handlePlayerMove()
        
        alive_players = self.countAlivePlayers()
        if alive_players == 0:
            # Dieser Zustand (kein Spieler mehr übrig) sollte nicht eintreten.
            # Das Spiel ist bereits vorbei, wenn nur ein Spieler übrig bleibt.
            logging.warning("Zero players left, game is over. (How did we get here?)")
            self.happen(gameevent.EventAbort(message="Zero players left, game is over. (How did we get here?)"))
            self._running = False
        elif alive_players == 1:
            # Spiel ist vorbei
            logging.info(f"One player left, game is over")
            logging.info(f"{repr(self.players[0])} won")
            assert isinstance(self.players[0].id, int)
            self.happen(gameevent.EventFinish(self.players[0].id))
            self._running = False

        self.current_player = self.nextAlivePlayer(self.current_player + 1)

    def handlePlayerMove(self) -> None:
        """Perform a move with the player who's turn it currently is.

        A move consists of the following steps:
        (1) Ask the player if they doubt their predecessor. If it's the first player of
          a round or the last player was kicked, this step is omitted.
          If the player doubted their predecessor, kick the player who's in the wrong
          and end the move.
        (2) Generate a new random dice throw, which represents the current player's throw result.
        (3) Ask the current player whether they want to tell the truth or lie, in which case they
          must also provide a different throw to tell to the other players.
        (4) Check if the players' throw (whether truthful or not) beats the previous
          player's throw. If it doesn't, kick the current player and end the move.
        (5) Store the current players throw as the last throw.
        """
        if self.last_throw_stated is None:
            # Default value, in cases there's no last throw
            doubt_predecessor = False
        else:
            # Ask the current player whether they accept or doubt their predecessor's throw result.
            doubt_predecessor = self.players[self.current_player].getDoubt(self.last_throw_stated, self.move_index, self.rng)

        if doubt_predecessor is None:
            # Player didn't answer
            logging.info(
                    f"{repr(self.players[self.current_player])} will be removed (got no response when asked for doubt)")
            self.kickPlayer(self.current_player, gameevent.KICK_REASON.NO_RESPONSE)
        elif doubt_predecessor:
            # Player doubts their predecessor
            logging.info(f"{repr(self.players[self.current_player])} chose to doubt their predecessor.")
            self.happen(gameevent.EventDoubt(self.players[self.current_player].id)) # type: ignore
            if self.last_throw_stated == self.last_throw_actual:
                # Previous player told the truth -> current player is in the wrong, kick them
                playerToKick = self.current_player
                self.kickPlayer(playerToKick, gameevent.KICK_REASON.FALSE_ACCUSATION)
                logging.info(f"Previous player was wrongfully doubted, {repr(self.players[playerToKick])} will be removed")
            else:
                # Previous player lied -> current player is right, kick previous player
                playerToKick = self.prevAlivePlayer(self.current_player - 1)
                self.kickPlayer(playerToKick, gameevent.KICK_REASON.LYING)
                logging.info(f"Previous player was rightfully doubted, {repr(self.players[playerToKick])} will be removed")

        else:
            # Player accepts their predecessors result
            # Now, it's their turn to throw dice
            if self.last_throw_stated is not None:
                logging.info(f"{repr(self.players[self.current_player])} chose not to doubt their predecessor.")
            # Generate a random dice throw
            currentThrow = self.randomThrow()
            # Ask the player what result they want to tell to the other players
            throwStated = self.players[self.current_player].getThrowStated(currentThrow, self.last_throw_stated,
                    self.move_index, self.rng)
            if throwStated is None:
                # Player didn't answer
                self.kickPlayer(self.current_player, gameevent.KICK_REASON.NO_RESPONSE)
                logging.info(f"{repr(self.players[self.current_player])} will be removed (got no response when asked for Throw)")
            else:
                # Player did answer
                logging.info(
                        f"{repr(self.players[self.current_player])} threw {str(currentThrow)}, states they threw {throwStated}")
                # This is the only way mypy will accept that self.players[self.current_player].id is not None....
                id_ = self.players[self.current_player].id
                assert isinstance(id_, int)
                self.happen(gameevent.EventThrow(id_, currentThrow, throwStated))
                # Check if the throw beats the one of the previous player
                if self.last_throw_stated is None:
                    # Their is no previous player or the player right before this one was kicked
                    self.last_throw_stated = throwStated
                    self.last_throw_actual = currentThrow
                else:
                    if throwStated > self.last_throw_stated:
                        # Beats predecessor
                        logging.info(
                                f"Stated current throw {throwStated} beats stated previous throw {self.last_throw_stated}")
                        self.last_throw_stated = throwStated
                        self.last_throw_actual = currentThrow
                    else:
                        # Does not beat predecessor
                        self.kickPlayer(self.current_player, gameevent.KICK_REASON.FAILED_TO_BEAT_PREDECESSOR)
                        logging.info(f"Stated current throw {throwStated} doesn't beat stated previous throw {self.last_throw_stated}")

    def kickPlayer(self, i: int, reason: gameevent.KICK_REASON) -> None:
        """Remove a player from the game.

        :param i: Index of the player to remove
        :param reason: Reason for the player to be kicked
        :param message: Message to print to the log
        """
        assert self.alive_players[i], f"Trying to kick already dead player {repr(self.players[i])}"
        # This is the only way to make mypy understand that id is, in fact, an int
        id_ = self.players[i].id
        assert isinstance(id_, int)
        self.alive_players[i] = False

        self.last_throw_stated = None
        self.last_throw_actual = None 

        self.happen(gameevent.EventKick(id_, reason))
        logging.info("Value to beat has been reset.")

    def happen(self, event: gameevent.Event) -> None:
        """Write an event to the log and alert other players.

        For each player, if they have the attribute listensToEvents set to True,
        their onEvent method will be called.

        :param event: Event that has occured"""
        self.log.happen(event)

        if isinstance(event, gameevent.EventThrow):
            # Delete the value of the actual throw, so that other players can't know what it was
            event.throw_actual = NoneThrow()
        for player in self.players:
            if player.listensToEvents:
                player.onEvent(event)

    def assignIds(self) -> None:
        """Assign a unique ID to each player"""
        used_ids: Set[int] = set()
        for p in self.players:
            if not isinstance(p.id, int) or (p.id in used_ids):
                p.id = max(used_ids) + 1 if used_ids else 0
            used_ids.add(p.id)

    def checkUniqueIds(self) -> bool:
        """Check if every player has a unique id"""
        used_ids: Set[int] = set()
        for p in self.players:
            assert isinstance(p.id, int)
            if p.id in used_ids:
                return False
            used_ids.add(p.id)
        return True

    def nextAlivePlayer(self, start):
        """Find the next player that is still in the game, starting from `start`.

        :param start: Index at which to start looking for an alive player.
          Can be a negative value."""
        assert any(self.alive_players), "Cannot find an alive player; none are left"
        start %= len(self.players)
        while not self.alive_players[start]:
            start = (start + 1) % len(self.players)
        return start
    
    def prevAlivePlayer(self, start):
        """Going backwards, find the next player that is still in the game, starting from `start`.

        :param start: Index at which to start looking for an alive player.
          Can be a negative value."""
        assert any(self.alive_players), "Cannot find an alive player; none are left"
        start %= len(self.players)
        while not self.alive_players[start]:
            start = (start - 1) % len(self.players)
        return start


    def countAlivePlayers(self):
        """Return the number of players still in the game"""
        return sum(self.alive_players)

    def randomThrow(self) -> Throw:
        """Generate a random Throw.

        This uses the instance's PRNG to ensure reproducibility."""
        return Throw(self.rng.randint(1, 6), self.rng.randint(1, 6))
