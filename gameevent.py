# Necessary for type hints of methods that include their own class
from __future__ import annotations
from typing import Optional
from enum import Enum, auto

from throw import Throw


class StrEnum(Enum):
    """Prettier string formatting for Enums"""
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}.{self._name_}"

    def __str__(self):
        return f"{self._name_}"


class EVENT_TYPES(StrEnum):
    THROW = auto()
    DOUBT = auto()
    KICK = auto()
    FINISH = auto()
    ABORT = auto()


class KICK_REASON(StrEnum):
    # Each item's value is a descriptive message
    LYING = "Lying"
    FALSE_ACCUSATION = "Making a false accusation"
    FAILED_TO_BEAT_PREDECESSOR = "Failing to beat their predecessor's result"
    NO_RESPONSE = "Player didn't respond"


class Event:
    """Base class for all Events"""
    # The type of Event
    event_type: EVENT_TYPES
    # The player which caused the event or which the event relates to
    player_id: Optional[int]

    def __init__(self, event_type: EVENT_TYPES, player_id: Optional[int]) -> None:
        self.event_type = event_type
        self.player_id = player_id

    def __str__(self) -> str:
        return f"{self.__class__.__name__} by Player with id {self.player_id})>"

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} (type={self.event_type}, player_id={self.player_id})>"


class EventThrow(Event):
    """Stores the result of a players dice throw and the result they told the other players"""
    throw_actual: Throw  # The actual result of the players throw
    throw_stated: Throw  # The result that the player stated they threw
    is_truthful: Optional[bool]  # Whether the player stated their result truthfully

    def __init__(self, player_id: int, throw_actual: Throw, throw_stated: Throw) -> None:
        super().__init__(EVENT_TYPES.THROW, player_id)
        self.throw_actual = throw_actual
        self.throw_stated = throw_stated
        self.is_truthful = None if None in (throw_actual, throw_stated) else throw_actual == throw_stated

    def __str__(self) -> str:
        if self.throw_actual:
            return f"Player with id {self.player_id} threw {self.throw_actual}, states they threw {self.throw_stated}"
        else:
            return f"Player with id {self.player_id} states they threw {self.throw_stated}"

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} (player_id={self.player_id}, throw_actual={self.throw_actual}, throw_stated={self.throw_stated})>"


class EventDoubt(Event):
    """Player doubts their predecessor"""

    def __init__(self, player_id: int) -> None:
        super().__init__(EVENT_TYPES.DOUBT, player_id)

    def __str__(self) -> str:
        return f"Player {self.player_id} chose to doubt their predecessor"


class EventKick(Event):
    """Player is kicked from the game"""
    player_id: int
    reason: KICK_REASON

    def __init__(self, player_id: int, reason: KICK_REASON) -> None:
        super().__init__(EVENT_TYPES.KICK, player_id)
        self.reason = reason

    def __str__(self) -> str:
        return f"Player {self.player_id} was removed. Reason: {self.reason.value}"

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} (player_id={self.player_id}, reason=\"{self.reason.value}\")>"


class EventFinish(Event):
    """Game ends regularly"""
    player_id: int

    def __init__(self, player_id: int) -> None:
        super().__init__(EVENT_TYPES.FINISH, None)
        self.player_id = player_id

    def __str__(self) -> str:
        return f"Game finished regularly. Player with id={self.player_id} won"

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} (player_id={(self.player_id)})"


class EventAbort(Event):
    """Game ends early/irregularly"""
    # Message / reason to end the Game early
    message: str

    def __init__(self, message="") -> None:
        super().__init__(EVENT_TYPES.ABORT, None)
        self.message = message

    def __str__(self) -> str:
        return "Game was aborted. " + (self.message if self.message else "(No message provided)")

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}>"
