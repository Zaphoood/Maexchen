# Maexchen

Simulate Mäxchen games between pre-defined player types.

## Installation
This project uses Python 3.9.x and the matplotlib module. It is optional but recommended to use a virtual environment for installing matplotlib.

Install matplotlib using pip:
```
python3.9 -m pip install matplotlib
```

## Usage
Start a simulation with
```
python3.9 main.py n_reps [OPTIONS]
```
`n_reps` specifies the number of times a simulation will be run. Options let you specify the players to be simulated. These are

Command line argument | Class name | Description
----------------------|------------|------------
`--dummmy` | `DummyPlayer` |  Very basic player class
`--c-dummy` | `CounterDummyPlayer` | Effective against `DummyPlayer`
`--adv-dummy` | `AdvancedDummyPlayer` | Effective against `CounterDummyPlayer` and pretty much all other player types
`--show-off` | `ShowOffPlayer` | Always lies about scoring high results
`--random` | `RandomPlayer` | Acts completely randomly
`--thres` | `ThresholdPlayer` | Has two thresholds that determine its behavior
`--c-thres` | `CounterThresholdPlayer` | Effective against `CounterThresholdPlayer`
`--tracking` | `TrackingPlayer` | Tracks other players' behavior

The number of players can be specified as well, for example
```
python3.9 main.py n_reps --dummy 2
```
would start a simulation with 2 players of type `DummyPlayer`.


Other options are:

 * `-q, --quiet`: Disable progress bar
 * `-v, --verbose`: Enable verbose output
 * `-x, --no-write`: Don't write results to log file
 * `-u, --no-sort`: Don't sort results by win rate
 * `-p, --plot-all`: Show visual plots of a simulations statistics for both win rate and reaons why players lost
 * `--plot-win-rate`: Same as above but only win rate
 * `--plot-loss-reason`: Same as above but only reasons for players to lose

The results of a simulation will be written to a file named 'results.log'.