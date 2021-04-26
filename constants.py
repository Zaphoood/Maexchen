MAEXCHEN = 21

# Alle möglichen Ergebnisse für einen Wurf (mit der höheren Zahl als erste Stelle),
# geordnet nach ihrem Rang ([31, 32, ..., 65, 11, 22, ..., 66, 21])
THROW_VALUES = [
    *[i*10 + j for i in range(3, 7) for j in range(1, i)], # "Normale" Würfe
    *[i*10 + i for i in range(1, 7)], # Päsche
    21 # Mäxchen
]
# Weist jedem Wurfergebniss einen Rang zu
THROW_RANK_BY_VALUE = {val: rank for rank, val in enumerate(THROW_VALUES)}