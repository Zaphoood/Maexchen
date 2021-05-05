from throw import Throw


class EVENT_TYPES():
    THROW = 0
    DOUBT = 1
    LEAVE = 2


class Event:
    """Basisklasse für ein Ereignis eines Spiels als Teil eines Mäxchenspiels dar."""
    eventType: EVENT_TYPES  # What kind of Event this represents
    playerId: int  # The player which caused the event

    def __init__(self, eventType: EVENT_TYPES, playerId: int):
        self.type = eventType
        self.playerId = playerId


class EventThrow(Event):
    """Spieler würfelt und gibt ein Würfelergebnis an."""
    throwActual: Throw  # The actual result of the players throw
    throwStated: Throw  # The result that the player stated they threw
    isTruthful: bool  # Whether the player stated their result truthfully

    def __init__(self, playerId: int, throwActual: Throw, throwStated: Throw):
        super(EventThrow, self).__init__(EVENT_TYPES.THROW, playerId)
        self.throwActual = throwActual
        self.throwStated = throwStated
        self.isTruthful = throwActual == throwStated


class EventDoubt(Event):
    """Spieler zweifelt seinen Vorgänger an."""

    def __init__(self, playerId: int):
        super(EventDoubt, self).__init__(EVENT_TYPES.DOUBT, playerId)


class EventLeave(Event):
    """Spieler verlässt (unfreiwillig) das Spiel."""

    def __init__(self, playerId: int):
        super(EventLeave, self).__init__(EVENT_TYPES.LEAVE, playerId)