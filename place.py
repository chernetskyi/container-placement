#!/usr/bin/env python3
import argparse
import pathlib
import random

from solvers import PSOSolver, CPSATSolver
from model import Scenario


def main():
    parser = argparse.ArgumentParser(description='Solve node-container placement.')
    parser.add_argument('--seed', type=int, help='value to initialize the random number generator')
    parser.add_argument('solver', choices=('cp-sat', 'pso'), help='name of the solver to use')
    parser.add_argument('filename', type=pathlib.Path, help='path to YAML file with the scenario')
    args = parser.parse_args()

    random.seed(args.seed)

    scenario = Scenario()
    scenario.read_from_yaml(args.filename)

    solvers = {
        'cp-sat': CPSATSolver,
        'pso': PSOSolver
    }
    Solver = solvers[args.solver]

    extra_args = {
        'cp-sat': {},
        'pso': {
            'particles': 20,
            'iterations': 100,
            'inertia':  0.75,
            'cognitive':  0.125,
            'social':  0.125,
            'velocity_bound_handling': None,
            'position_bound_handling': 'boundary'
        }
    }

    solver = Solver(scenario, **extra_args[args.solver])
    solver.solve()
    solver.print_solution()


if __name__ == '__main__':
    main()
