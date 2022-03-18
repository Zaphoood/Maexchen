from __future__ import annotations  # Notwendig für type hints, die die eigene Klasse beinhalten

import contextlib
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
    """Basisklasse für ein Ereignis eines Spiels als Teil eines Mäxchenspiels dar."""
    eventType: EVENT_TYPES  # What kind of Event this represents
    playerId: int  # The player which caused the event

    def __init__(self, eventType: EVENT_TYPES, playerId: int) -> None:
        self.eventType = eventType
        self.playerId = playerId

    def __str__(self) -> str:
        return f"{self.__class__.__name__} by Player with id {self.playerId})>"

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} (type={self.eventType}, playerId={self.playerId})>"

    def __eq__(self, other: Event) -> bool:
        if not isinstance(other, self.__class__):
            raise NotImplementedError
        return self.eventType == other.eventType and self.playerId == other.playerId


class EventThrow(Event):
    """Spieler würfelt und gibt ein Würfelergebnis an."""
    throwActual: Throw  # The actual result of the players throw
    throwStated: Throw  # The result that the player stated they threw
    isTruthful: bool  # Whether the player stated their result truthfully

    def __init__(self, playerId: int, throwActual: Throw, throwStated: Throw) -> None:
        super().__init__(EVENT_TYPES.THROW, playerId)
        self.throwActual = throwActual
        self.throwStated = throwStated
        self.isTruthful = None if None in (throwActual, throwStated) else throwActual == throwStated

    def __str__(self) -> str:
        if self.throwActual:
            return f"Player with id {self.playerId} threw {self.throwActual}, states they threw {self.throwStated}"
        else:
            return f"Player with id {self.playerId} states they threw {self.throwStated}"

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} (playerId={self.playerId}, throwActual={self.throwActual}, throwStated={self.throwStated})>"

    def __eq__(self, other: Event) -> bool:
        return super().__eq__(other) and self.throwActual == other.throwActual and self.throwStated == other.throwStated


class EventDoubt(Event):
    """Spieler zweifelt seinen Vorgänger an."""

    def __init__(self, playerId: int) -> None:
        super().__init__(EVENT_TYPES.DOUBT, playerId)

    def __str__(self) -> str:
        return f"Player {self.playerId} chose to doubt their predecessor"


class EventKick(Event):
    """Spieler verlässt (unfreiwillig) das Spiel."""
    reason: KICK_REASON

    def __init__(self, playerId: int, reason: KICK_REASON) -> None:
        super().__init__(EVENT_TYPES.KICK, playerId)
        self.reason = reason

    def __str__(self) -> str:
        return f"Player {self.playerId} was removed. Reason: {self.reason.value}"

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} (playerId={self.playerId}, reason=\"{self.reason.value}\")>"

    def __eq__(self, other: Event) -> bool:
        return super().__eq__(other) and self.reason == other.reason


class EventFinish(Event):
    """Spiel wird ordnungsgemäß beendet."""
    winner_id: int  # ID des Siegers des Spiels

    def __init__(self, winner_id: int) -> None:
        super().__init__(EVENT_TYPES.FINISH, None)
        self.winner_id = winner_id

    def __str__(self) -> str:
        return f"Game finished regularly. Player with id={self.winner_id} won"

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} (winner={repr(self.winner)})"

    def __eq__(self, other: Event) -> bool:
        # Unterdrücken von AttributeError für den Fall, dass other keine EventAbort-Instanz ist
        # und deshalb nicht das Attribut .winner hat
        # super().__eq__(other) wird hier nicht verwendet, da diese funktion auch die Gleichheit
        # von .playerId überprüft, welche hier aber irrelevant ist
        with contextlib.suppress(AttributeError):
            return isinstance(other, EventFinish) and self.winner_id == other.winner_id


class EventAbort(Event):
    """Spiel wird vorzeitig beendet."""
    message: str  # Grund, warum das Spiel vorzeitig beendet wird

    def __init__(self, message="") -> None:
        super().__init__(EVENT_TYPES.ABORT, None)
        self.message = message

    def __str__(self) -> str:
        return "Game was aborted. " + (self.message if self.message else "(No message provided)")

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} (type={self.eventType}, playerId={self.playerId})>"

    def __eq__(self, other: Event) -> bool:
        # Unterdrücken von AttributeError für den Fall, dass other keine EventAbort-Instanz ist
        # und deshalb nicht das Attribut .message hat
        # super().__eq__(other) wird nicht verwendet, da diese Funktion auch die Gleichheit
        # von .playerId überprüft, welche hier aber irrelevant ist
        with contextlib.suppress(AttributeError):
            return isinstance(other, EventAbort) and self.message == other.message
