#!/usr/bin/env python3
import argparse
import logging
import os
import random
import sys

from solvers import PSOSolver, CPSATSolver
from model import Scenario, NoSolutionError


def main():
    parser = argparse.ArgumentParser(description='Solve node-container placement.')
    parser.add_argument('--log-file',
                        type=argparse.FileType('a'),
                        default=sys.stdout,
                        help='log file')
    parser.add_argument('--log-level',
                        choices=('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'),
                        help='logging level')
    parser.add_argument('-o', '--output',
                        type=argparse.FileType('w'),
                        default=sys.stdout,
                        help='output file')
    parser.add_argument('--seed',
                        type=int,
                        help='random number generator seed')
    parser.add_argument('solver',
                        choices=('cp-sat', 'pso'),
                        help='name of the solver')
    parser.add_argument('scenario',
                        type=argparse.FileType('r'),
                        help='scenario YAML file')
    args = parser.parse_args()

    random.seed(args.seed)

    scenario = Scenario()
    scenario.read_from_yaml(args.scenario)

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
            'inertia': 0.75,
            'cognitive': 0.125,
            'social': 0.125,
            'zero_init_velocity': False,
            'velocity_handling': 'none',
            'position_handling': 'boundary'
        }
    }

    log_lvl = args.log_level if args.log_level else os.environ.get('LOG_LEVEL',
                                                                   'WARN').upper()
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                        level=log_lvl,
                        stream=args.log_file)

    solver = Solver(scenario, **extra_args[args.solver])
    solver.solve()

    try:
        solver.print_solution(args.output)
    except NoSolutionError:
        pass


if __name__ == '__main__':
    main()
