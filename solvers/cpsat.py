import logging

from itertools import product
from ortools.sat.python import cp_model

from model.solver import Solver, NoSolutionError


class CPSATSolver(Solver):
    def __init__(self, scenario):
        self.solver = cp_model.CpSolver()
        self.model = cp_model.CpModel()
        super().__init__(scenario)
        self.__m_range = range(len(self.scenario.micros))
        self.__n_range = range(len(self.scenario.nodes))

    def __variables(self):
        self.used = {}  # does node have any containers scheduled
        self.sched = {}  # is container scheduled on a node
        for k in self.__n_range:
            for i in self.__m_range:
                for j in range(self.micro(i).containers):
                    self.sched[i, j, k] = self.model.NewBoolVar('sched')

            self.used[k] = self.model.NewBoolVar('used')
            self.model.AddMaxEquality(self.used[k],
                                      [self.sched[i, j, k] for i in self.__m_range
                                       for j in range(self.micro(i).containers)])

        self.schedx2 = {}  # product of two sched variables
        for k1, k2 in product(self.__n_range, self.__n_range):
            for i1, i2 in product(self.__m_range, self.__m_range):
                prod = product(range(self.micro(i1).containers), range(self.micro(i2).containers))
                for j1, j2 in prod:
                    self.schedx2[i1, j1, k1, i2, j2, k2] = self.model.NewBoolVar('schedx2')
                    self.model.AddMultiplicationEquality(self.schedx2[i1, j1, k1, i2, j2, k2], (self.sched[i1, j1, k1], self.sched[i2, j2, k2]))

        logging.debug('Variables are successfuly defined')

    def __constraints(self):
        # Every container is scheduled exactly once
        for i in self.__m_range:
            for j in range(self.micro(i).containers):
                self.model.AddExactlyOne(self.sched[i, j, k] for k in self.__n_range)

        for k in self.__n_range:
            # Container limit
            self.model.Add(sum(self.sched[i, j, k] for i in self.__m_range
                               for j in range(self.micro(i).containers)) <= self.node(k).contlim)

            # CPU limit
            self.model.Add(sum(self.sched[i, j, k] * self.micro(i).cpureq for i in self.__m_range
                               for j in range(self.micro(i).containers)) <= self.node(k).cpulim)

            # Memory limit
            self.model.Add(sum(self.sched[i, j, k] * self.micro(i).memreq for i in self.__m_range
                               for j in range(self.micro(i).containers)) <= self.node(k).memlim)

        logging.debug('Constraints are successfuly defined')

    def __objectives(self):
        node_costs, data_costs = [], []

        for k in self.__n_range:
            node_costs.append(
                cp_model.LinearExpr.Term(self.used[k], self.node(k).cost))

        for k1, k2 in product(self.__n_range, self.__n_range):
            for i1, i2 in product(self.__m_range, self.__m_range):
                prod = product(range(self.micro(i1).containers), range(self.micro(i2).containers))
                for j1, j2 in prod:
                    ndc = self.scenario.data_cost(self.node(k1).name, self.node(k2).name)
                    data = self.scenario.data_rate(self.micro(i1).name, self.micro(i2).name)
                    coef = ndc * data / self.micro(i1).containers / self.micro(i2).containers
                    data_costs.append(cp_model.LinearExpr.Term(self.schedx2[i1, j1, k1, i2, j2, k2], coef))

        nodecost = cp_model.LinearExpr.Sum(node_costs)
        datacost = cp_model.LinearExpr.Sum(data_costs)

        self.model.Minimize(nodecost + datacost)

        logging.debug('Objective is successfuly defined')

    def solution(self):
        if self.status != cp_model.OPTIMAL:
            logging.error('CP-SAT failed to find an optimal solution')
            raise NoSolutionError('CP-SAT failed to find an optimal solution.')

        self.cost = self.solver.ObjectiveValue()

        for k in self.__n_range:
            if self.solver.Value(self.used[k]):
                for i in self.__m_range:
                    for j in range(self.micro(i).containers):
                        scheduled = self.solver.Value(self.sched[i, j, k])
                        self.mapping[self.node(k).name][self.micro(i).name] += scheduled

        return super().solution()

    def solve(self):
        self.__variables()
        self.__constraints()
        self.__objectives()

        logging.debug('Starting solving')
        self.status = self.solver.Solve(self.model)
        logging.debug('Finished solving')

    def micro(self, i):
        return self.scenario.micros[self.scenario.micros_tpl[i]]

    def node(self, i):
        return self.scenario.nodes[self.scenario.nodes_tpl[i]]
