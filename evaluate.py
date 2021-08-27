"""Game Evaluation

Allows the evaluation of GameLog objects in order to determine, for example, who was the winner of a game."""

from gamelog import GameLog
from gameevent import EventKick
from player import Player


class IncompleteLogError(Exception):
    pass


def getWinner(log: GameLog) -> Player:
    if log.hasFinished():
        playersAlive = log.players
        print(f"Players in game are: ")
        print("\n".join([f" - {str(p)}" for p in log.players]))
        for kickEvent in [e for e in log.getEvents() if isinstance(e, EventKick)]:
            for i, player in enumerate(playersAlive):
                if player.id == kickEvent.playerId:
                    print(f"Removed player with id={kickEvent.playerId}")
                    playersAlive.pop(i)
        if len(playersAlive) == 1:
            return playersAlive[0]
        else:
            raise IncompleteLogError(f"Couldn't determine winner from GameLog. {len(playersAlive)} left at the end of evaluation.")
    else:
        return None
