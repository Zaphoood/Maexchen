import constants as c
from throw import Throw

# Wahrscheinlichkeit für das Eintreten eines Würfelergebnisses z_i
PROB_BY_NUM = [*[1/18]*14, *[1/36]*6, 1/18]
# Kumulative Wahrscheinlichkeit, d. h. Wahrscheinlichkeit, dass ein zufällig gewähltes Ergebnis
# kleiner oder gleich einem Ergebnis z_i ist
PROB_BY_NUM_CUM = [sum(PROB_BY_NUM[:(i + 1)]) for i in range(21)]

def probBelow(throw: Throw) -> bool:
    """Wahrscheinlichkeit, dass ein zufällig gewählter Wurf niedriger als throw ist."""
    return PROB_BY_NUM_CUM[throw.rank - 1]

def probAbove(throw: Throw) -> bool:
    """Wahrscheinlichkeit, dass ein zufällig gewählter Wurf höher als throw ist."""
    return 1 - probAbove(throw)
