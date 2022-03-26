import constants as c
from throw import Throw

# Probability for each Throw to occur
PROB_BY_NUM = [*[1/18]*14, *[1/36]*6, 1/18]
# Same as above but cumulative
PROB_BY_NUM_CUM = [sum(PROB_BY_NUM[:(i + 1)]) for i in range(21)]

def probEQ(throw: Throw) -> float:
    """Probability that a randomly chosen Throw is equal to `throw`"""
    return PROB_BY_NUM[throw.rank]

def probLT(throw: Throw) -> float:
    """Probability that a randomly chosen Throw is of a lower rank than `throw`"""
    return PROB_BY_NUM_CUM[throw.rank - 1]

def probGE(throw: Throw) -> float:
    """Probability that a randomly chosen Throw is of an equal or higher rank than `throw`"""
    return 1 - probLT(throw)
