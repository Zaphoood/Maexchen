from enum import Enum

from throw import Throw


class EVENT_TYPES(Enum):
    THROW = 0
    DOUBT = 1
    KICK = 2
    ABORT = 3


class Event:
    """Basisklasse für ein Ereignis eines Spiels als Teil eines Mäxchenspiels dar."""
    eventType: EVENT_TYPES  # What kind of Event this represents
    playerId: int  # The player which caused the event

    def __init__(self, eventType: EVENT_TYPES, playerId: int):
        self.type = eventType
        self.playerId = playerId

    def __str__(self):
        return f"{self.__class__.__name__} by Player {self.playerId})>"

    def __repr__(self):
        return f"<{self.__class__.__name__} (type={self.eventType}, playerId={self.playerId})>"


class EventThrow(Event):
    """Spieler würfelt und gibt ein Würfelergebnis an."""
    throwActual: Throw  # The actual result of the players throw
    throwStated: Throw  # The result that the player stated they threw
    isTruthful: bool  # Whether the player stated their result truthfully

    def __init__(self, playerId: int, throwActual: Throw, throwStated: Throw):
        super().__init__(EVENT_TYPES.THROW, playerId)
        self.throwActual = throwActual
        self.throwStated = throwStated
        self.isTruthful = throwActual == throwStated

    def __str__(self):
        return f"Player {self.playerId} threw {self.throwActual}, said they threw {self.throwStated}"


class EventDoubt(Event):
    """Spieler zweifelt seinen Vorgänger an."""

    def __init__(self, playerId: int):
        super().__init__(EVENT_TYPES.DOUBT, playerId)

    def __str__(self):
        return f"Player {self.playerId} doubted their predecessor"


class EventKick(Event):
    """Spieler verlässt (unfreiwillig) das Spiel."""

    def __init__(self, playerId: int):
        super().__init__(EVENT_TYPES.KICK, playerId)

    def __str__(self):
        return f"Player {self.playerId} was kicked"


class EventAbort(Event):
    """Spiel wird vorzeitig beendet."""

    def __init__(self):
        super().__init__(EVENT_TYPES.ABORT, None)

    def __str__(self):
        return "Game was ended"
