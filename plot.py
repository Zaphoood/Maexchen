import matplotlib.pyplot as plt
import pylab
import numpy as np

loss_categories = ["Lügen", "Falsch beschuldigt", "Vorgänger nicht überboten"]

border_0 = 0.08
border_1 = border_0 * 1.5
axis_rect = [border_0, border_0, 1 - border_1, 1 - border_1]

def plotWinRate(*args, **kwargs):
    figure = _winRateFig(*args, **kwargs) 
    plt.show()

def plotLossReason(*args, **kwargs):
    figure = _lossReasonFig(*args, **kwargs) 
    plt.show()
 
def plotWRandLR(player_names: list[str], win_rates: list[float], loss_reasons: list[float], win_y_range=None, loss_y_range=[0., 1.]):
    win_rate_figure = _winRateFig(player_names, win_rates, win_y_range, fig_index=0)
    loss_reason_figure = _lossReasonFig(player_names, loss_reasons, loss_y_range, fig_index=1)
    plt.show()
    
def _winRateFig(player_names: list[str], values: list[float], y_range=None, fig_index=None) -> None:
    fig = plt.figure(fig_index)
    window = pylab.gcf()
    window.canvas.manager.set_window_title('Gewinnrate je Spieler')
    ax = fig.add_axes(axis_rect)
    x_positions = np.arange(0, len(player_names)*1.25, 1.25)
    plt.xticks(x_positions, player_names)
    plt.yticks(np.arange(0, 1.0, 0.1))
    if y_range:
        plt.ylim(y_range)
    ax.bar(x_positions, values)

    return fig

def _lossReasonFig(player_names: list[str], values: list[float], y_range=[0, 1], fig_index=None) -> None:
    # Allow only for three values per player
    values = [player_stats[:3] for player_stats in values]
    # Flip table so bars are grouped by player and not by category
    values = [row for row in zip(*values)]

    fig = plt.figure(fig_index)
    window = pylab.gcf()
    window.canvas.manager.set_window_title('Gründe fürs Ausscheiden je Spieler')
    ax = fig.add_axes(axis_rect)
    positions = np.arange(0, len(player_names)*4, 4)
    plt.yticks(np.arange(0, 1.1, 0.1))
    plt.ylim(y_range)
    plt.xticks(positions, player_names)
    ax.bar(positions - 1, values[0], width=1)
    ax.bar(positions,     values[1], width=1)
    ax.bar(positions + 1, values[2], width=1)
    ax.legend(labels = loss_categories)

    return fig
