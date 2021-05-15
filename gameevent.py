from __future__ import annotations  # Notwendig für type hints die die eigene Klasse beinhalten

import contextlib
from enum import Enum

from throw import Throw
from player import Player


class EVENT_TYPES(Enum):
    THROW = 0
    DOUBT = 1
    KICK = 2
    FINISH = 3
    ABORT = 4


class KICK_REASON(Enum):
    LYING = 0
    FALSE_ACCUSATION = 1
    FAILED_TO_BEAT_PREDECESSOR = 2


KICK_REASON_TO_STR = {
    KICK_REASON.LYING: "Lying",
    KICK_REASON.FALSE_ACCUSATION: "Making a false accusation",
    KICK_REASON.FAILED_TO_BEAT_PREDECESSOR: "Failing to beat their predecessor's result"
}


class Event:
    """Basisklasse für ein Ereignis eines Spiels als Teil eines Mäxchenspiels dar."""
    eventType: EVENT_TYPES  # What kind of Event this represents
    playerId: int  # The player which caused the event

    def __init__(self, eventType: EVENT_TYPES, playerId: int):
        self.eventType = eventType
        self.playerId = playerId

    def __str__(self):
        return f"{self.__class__.__name__} by Player {self.playerId})>"

    def __repr__(self):
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
        self.isTruthful = throwActual == throwStated

    def __str__(self) -> str:
        return f"Player {self.playerId} threw {self.throwActual}, said they threw {self.throwStated}"

    def __eq__(self, other: Event) -> bool:
        return super().__eq__(other) and self.throwActual == other.throwActual and self.throwStated == other.throwStated


class EventDoubt(Event):
    """Spieler zweifelt seinen Vorgänger an."""

    def __init__(self, playerId: int) -> None:
        super().__init__(EVENT_TYPES.DOUBT, playerId)

    def __str__(self) -> str:
        return f"Player {self.playerId} doubted their predecessor"


class EventKick(Event):
    """Spieler verlässt (unfreiwillig) das Spiel."""
    reason: KICK_REASON
    reasonToStr: dict[KICK_REASON, str]

    def __init__(self, playerId: int, reason: KICK_REASON) -> None:
        super().__init__(EVENT_TYPES.KICK, playerId)
        self.reason = reason

    def __str__(self) -> str:
        return f"Player {self.playerId} was kicked. Reason: {KICK_REASON_TO_STR[self.reason]}"

    def __eq__(self, other: Event) -> bool:
        return super().__eq__(other) and self.reason == other.reason


class EventFinish(Event):
    """Spiel wird ordnungsgemäß beendet."""
    winner: Player

    def __init__(self, winner: Player) -> None:
        super().__init__(EVENT_TYPES.FINISH, None)
        self.winner = winner

    def __str__(self) -> str:
        return f"Game finished regularly. {str(self.winner)} won"

    def __eq__(self, other: Event) -> bool:
        # Unterdrücken von AttributeError für den Fall, dass other keine EventAbort-Instanz ist
        # und deshalb nicht das Attribut .winner hat
        # super().__eq__(other) wird hier nicht verwendet, da diese funktion auch die Gleichheit
        # von .playerId überprüft, welche hier aber irrelevant ist
        with contextlib.suppress(AttributeError):
            return isinstance(other, EventFinish) and self.winner == other.winner


class EventAbort(Event):
    """Spiel wird vorzeitig beendet."""
    message: str  # Grund, warum das Spiel vorzeitig beendet wurde

    def __init__(self, message=""):
        super().__init__(EVENT_TYPES.ABORT, None)
        self.message = message

    def __str__(self):
        return "Game was aborted" + (f". {self.message}" if self.message else ". <No message provided>")

    def __eq__(self, other: Event) -> bool:
        # Unterdrücken von AttributeError für den Fall, dass other keine EventAbort-Instanz ist
        # und deshalb nicht das Attribut .message hat
        # super().__eq__(other) wird hier nicht verwendet, da diese funktion auch die Gleichheit
        # von .playerId überprüft, welche hier aber irrelevant ist
        with contextlib.suppress(AttributeError):
            return isinstance(other, EventAbort) and self.message == other.message
