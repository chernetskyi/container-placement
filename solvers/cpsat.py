import logging

from ortools.sat.python import cp_model

from model.solver import Solver, NoSolutionError


class CPSATSolver(Solver):
    def __init__(self, scenario):
        self.solver = cp_model.CpSolver()
        self.model = cp_model.CpModel()
        super().__init__(scenario)

    def solve(self):
        micros = self.scenario.micros
        nodes = self.scenario.nodes

        self.__m_range = range(len(micros))
        self.__n_range = range(len(nodes))

        node_costs = []
        data_costs = []

        # Variables
        self.used = {}  # does node have any containers scheduled
        self.sched = {}  # is container scheduled on a node
        for k in self.__n_range:
            self.used[k] = self.model.NewBoolVar('used')
            for i in self.__m_range:
                for j in range(micros[i].containers):
                    self.sched[i, j, k] = self.model.NewBoolVar('sched')
            self.model.AddMaxEquality(self.used[k],
                                      [self.sched[i, j, k] for i in self.__m_range
                                       for j in range(micros[i].containers)])

        self.schedx2 = {}
        for k1 in self.__n_range:
            for i1 in self.__m_range:
                for j1 in range(micros[i1].containers):
                    for k2 in self.__n_range:
                        for i2 in self.__m_range:
                            for j2 in range(micros[i2].containers):
                                self.schedx2[i1, j1, k1, i2, j2, k2] = self.model.NewBoolVar('schedx2')
                                self.model.AddMultiplicationEquality(self.schedx2[i1, j1, k1, i2, j2, k2], (self.sched[i1, j1, k1], self.sched[i2, j2, k2]))

        # Constraints
        # Every container is scheduled exactly once
        for i in self.__m_range:
            for j in range(micros[i].containers):
                self.model.AddExactlyOne(
                    self.sched[i, j, k] for k in self.__n_range)

        for k in self.__n_range:
            # Container limit
            self.model.Add(sum(self.sched[i, j, k]
                               for i in self.__m_range
                               for j in range(micros[i].containers)) <= nodes[k].contlim)

            # CPU limit
            self.model.Add(sum(self.sched[i, j, k] * micros[i].cpureq
                               for i in self.__m_range
                               for j in range(micros[i].containers)) <= nodes[k].cpulim)

            # Memory limit
            self.model.Add(sum(self.sched[i, j, k] * micros[i].memreq
                               for i in self.__m_range
                               for j in range(micros[i].containers)) <= nodes[k].memlim)

            # Objectives
            # Cost
            node_costs.append(
                cp_model.LinearExpr.Term(self.used[k], nodes[k].cost))

        for k1 in self.__n_range:
            for i1 in self.__m_range:
                for j1 in range(micros[i1].containers):
                    for k2 in self.__n_range:
                        for i2 in self.__m_range:
                            for j2 in range(micros[i2].containers):
                                ndc = self.scenario.node_data_cost(nodes[k1], nodes[k2])
                                data = self.scenario.datarate.get(micros[i1].name, {}).get(micros[i2].name, 0)
                                coef = ndc * data / micros[i1].containers / micros[i2].containers
                                data_costs.append(cp_model.LinearExpr.Term(self.schedx2[i1, j1, k1, i2, j2, k2], coef))

        nodecost = cp_model.LinearExpr.Sum(node_costs)
        datacost = cp_model.LinearExpr.Sum(data_costs)

        self.model.Minimize(nodecost + datacost)

        self.status = self.solver.Solve(self.model)

    def print_solution(self, file):
        if self.status != cp_model.OPTIMAL:
            logging.error('CP-SAT failed to find an optimal solution')
            raise NoSolutionError('CP-SAT failed to find an optimal solution.')

        self.cost = self.solver.ObjectiveValue()

        micros = self.scenario.micros
        nodes = self.scenario.nodes

        for k in self.__n_range:
            if self.solver.Value(self.used[k]):
                for i in self.__m_range:
                    for j in range(micros[i].containers):
                        scheduled = self.solver.Value(self.sched[i, j, k])
                        self.mapping[nodes[k]][micros[i]] += scheduled

        super().print_solution(file)
