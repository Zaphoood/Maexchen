# Maexchen

A simulator for the dice game "Mäxchen" (also known as "Mäxle" or "Meier").
Various player types, each with a different strategy, compete against each other.
The results can then be stored and/or visualized.

This program was written as part of my term paper in 12th grade.
Tag `v0.1` marks the state of the project at the time of submission.

## Installation
This project uses Python 3.9 and the matplotlib library. It is optional but recommended to use a virtual environment.

Create and activate virtualenv
```
virtualenv --python=<path-to-python3.9> venv
source venv/bin/activate
```

Install matplotlib
```
python3.9 -m pip install matplotlib
```

## Usage
Run a simulation with:
```
python3.9 main.py NUM_REPS [OPTIONS]
```
The number of time the simulation will be repeated is specified by `NUM_REPS`.
The players simulated can be specified with `OPTIONS`.  The following player types are available:

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

The number of player instances of each class can be specified as well.
For example, in order to start a simulation with two players of type `DummyPlayer`, and three of type `CounterDummyPlayer`, run
```
python3.9 main.py n_reps --dummy 2 --c-dummy 3
```

Other options are:

 * `-q, --quiet`: Disable progress bar
 * `-v, --verbose`: Enable verbose output
 * `-x, --no-write`: Disable writing results to log file
 * `-u, --no-sort`: Disable sorting of results by win rate
 * `-p, --plot-all`: Graph simulation results for both win rate and loss causes
 * `--plot-win-rate`: Same as above but only win rate
 * `--plot-loss-reason`: Same as above but only loss causes

The results of a simulation will be written to `results.log`.