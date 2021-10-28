def formatTable(table, space=2):
    """Eine zweidimensionale Tabelle formatieren und als String zurückgeben.

    :param table: Tabelle als nested list
    :param space: Anzahl Leerzeichen zwischen zwei Spalten
    :return: Tabelle als str"""
    # Sichergehen, dass alle Zeilen die gleiche Länge haben
    assert all([len(row) == len(table[0]) for row in table[1:]])
    # ... und vom Typ str sind
    assert all([all([isinstance(el, str) for el in row]) for row in table])

    delim = " " * space
    column_widths = [max([len(table[row][col] + delim) for row in range(len(table))]) for col in range(len(table[0]))]
    
    table_str = "\n".join(
        ["".join(
                [el + " " * (column_widths[col] - len(el)) for col, el in enumerate(row)]
        )
        for row in table]
    )
    return table_str

if __name__ == "__main__":
    t = [
        ["a", "000", "0"],
        ["asdfsadf", "", "001"],
        ["asdfd", "000", "1219412"],
    ]

    print(formatTable(t))
