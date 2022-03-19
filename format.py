def formatTable(table, space=2):
    """Eine zweidimensionale Tabelle formatieren und als String zurückgeben.

    :param table: Tabelle als nested list
    :param space: Anzahl Leerzeichen zwischen zwei Spalten
    :return: Tabelle als str"""

    assert all([len(row) == len(table[0]) for row in table[1:]]), "All rows must be of the same width"
    assert all([isinstance(el, str) for row in table for el in row]), "All elements must be strings"

    delim = " " * space
    column_widths = [max([len(table[row][col] + delim) for row in range(len(table))]) for col in range(len(table[0]))]
    
    table_str = "\n".join(
        ["".join(
                [el + " " * (column_widths[col] - len(el)) for col, el in enumerate(row)]
        )
        for row in table]
    )
    return table_str

