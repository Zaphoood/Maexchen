# Maexchen

Simulate Mäxchen games between pre-defined player types.

## Installation
This project uses Python 3.9.x and the matplotlib library. It is optional but recommended to use a virtual environment for installing matplotlib.

Create and activate virtualenv
```
virtualenv --python=<path-to-python3.9> venv
source venv/bin/activate
```

Install matplotlib with:
```
python3.9 -m pip install matplotlib
```

## Usage
Run a simulation with:
```
python3.9 main.py [NUM_REPS] [OPTIONS]
```
The number of time the simulation will be repeated is specified by `NUM_REPS`.
`OPTIONS` lets you specify the players to be simulated. The following player types are available:

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

The number of players can be specified as well.
For example, in order to start a simulation with two players of type `DummyPlayer`, and three of type `CounterDummyPlayer`, run
```
python3.9 main.py n_reps --dummy 2 --c-dummy 3
```

Other options are:

 * `-q, --quiet`: Disable progress bar
 * `-v, --verbose`: Enable verbose output
 * `-x, --no-write`: Don't write results to log file
 * `-u, --no-sort`: Don't sort results by win rate
 * `-p, --plot-all`: Show visual plots of a simulations statistics for both win rate and reaons why players lost
 * `--plot-win-rate`: Same as above but only win rate
 * `--plot-loss-reason`: Same as above but only reasons for players to lose

The results of a simulation will be written to a file named 'results.log'.