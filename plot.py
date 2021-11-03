import matplotlib.pyplot as plt
import numpy as np

loss_categories = ["Lügen", "Falsch beschuldigt", "Vorgänger nicht überboten"]

border_0 = 0.08
border_1 = border_0 * 1.5
axis_rect = [border_0, border_0, 1 - border_1, 1 - border_1]

def plotWinRate(player_names: list[str], values: list[float], y_range=None) -> None:
    fig = plt.figure()
    ax = fig.add_axes(axis_rect)
    x_positions = np.arange(0, len(player_names)*1.25, 1.25)
    plt.xticks(x_positions, player_names)
    plt.yticks(np.arange(0, 1.0, 0.1))
    if y_range:
        plt.ylim(y_range)
    ax.bar(x_positions, values)
    plt.show()

def plotLossReason(player_names: list[str], values: list[float], y_range=[0, 1]) -> None:
    # Allow only for three values per player
    values = [player_stats[:3] for player_stats in values]
    # Flip table so bars are grouped by player and not by category
    values = [row for row in zip(*values)]

    fig = plt.figure()
    ax = fig.add_axes(axis_rect)
    positions = np.arange(0, len(player_names)*4, 4)
    plt.yticks(np.arange(0, 1.1, 0.1))
    plt.ylim(y_range)
    plt.xticks(positions, player_names)
    ax.bar(positions - 1, values[0], width=1)
    ax.bar(positions,     values[1], width=1)
    ax.bar(positions + 1, values[2], width=1)
    ax.legend(labels = loss_categories)
    plt.show()

