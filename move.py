import constants as c
from throw import Throw

class Move:
    def __init__(self, move, value: Throw =None):
        assert move in c.MOVES # Sichergehen, dass move ein erlaubter Zug ist
        self.move = move
        self.value = value # Wird nur für Züge verwendet, bei denen der Spieler würfelt. Beinhaltet
        # die Angabe des Spielers über das Würfelergebnis
