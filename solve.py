#!/usr/bin/env python3
import argparse
import pathlib
import sys

from solvers import PSOSolver, CPSATSolver, NoSolutionError

from model import read_scenario_from_yaml


def main():
    parser = argparse.ArgumentParser(description='Solve node-container placement.')
    parser.add_argument('solver', choices={'cp-sat', 'pso'}, help='name of the solver to use')
    parser.add_argument('filename', type=pathlib.Path, help='path to YAML file with the scenario')
    args = parser.parse_args()

    scenario = read_scenario_from_yaml(args.filename)

    solvers = {
        'cp-sat': CPSATSolver,
        'pso': PSOSolver
    }
    Solver = solvers[args.solver]

    extra_args = {
        'cp_sat': {},
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

    solver = Solver(**scenario, **extra_args[args.solver])
    solver.solve()

    try:
        print(solver.solution())
    except NoSolutionError as e:
        sys.exit(e)


if __name__ == '__main__':
    main()
