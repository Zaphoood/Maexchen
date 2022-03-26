from typing import List

def formatTable(table: List[List[str]], spaces: int = 2) -> str:
    """Format a two-dimensional table into a string.

    :param table: Two-dimensional list
    :param spaces: Amount of spaces between columns
    :return: str containing the formatted table
    """

    assert all([len(row) == len(table[0]) for row in table[1:]]), "All rows must be of the same width"
    assert all([isinstance(el, str) for row in table for el in row]), "All elements must be strings"

    delim = " " * spaces
    # The width of each column, which is determined by the length of its widest element
    # plus the number of delimiting spaces between columns
    column_widths: List[int] = [max([len(el) for el in col]) + spaces for col in zip(*table)]
    
    output = ""
    for row in table:
        for col, el in enumerate(row):
            # Left-align text with additional spaces to the left, so that its
            # total length is equal to column_widths[col]
            output += ("{: <" + str(column_widths[col]) + "}").format(el)
        output += "\n"

    return output


def printProgress(prg: int, total: int, end: str = "\n"):
    """Simple progress bar.

    :param total: Inner width of the progress bar
    :param prg: Progress
    :param end: Optional. str to print after the progress bar
    """
    output = "[" + "#" * prg + "." * (total - prg) + "]"
    print(output, end=end)
