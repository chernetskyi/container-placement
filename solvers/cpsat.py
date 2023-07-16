from ortools.sat.python import cp_model

from model.solver import Solver, NoSolutionError


class CPSATSolver(Solver):
    def __init__(self, scenario):
        self.solver = cp_model.CpSolver()
        self.model = cp_model.CpModel()
        super().__init__(scenario)

    def solve(self):
        self.micros = range(len(self.microservices))
        self.conts = range(sum(m.num_containers for m in self.microservices))
        self.nods = range(len(self.nodes))

        objective = []

        # Variables
        self.used = {}  # does node have any containers scheduled
        self.sched = {}  # is container scheduled on a node
        for k in self.nods:
            self.used[k] = self.model.NewBoolVar('used')
            for i in self.micros:
                for j in range(self.microservices[i].num_containers):
                    self.sched[i, j, k] = self.model.NewBoolVar('sched')
            self.model.AddMaxEquality(self.used[k], [self.sched[i, j, k] for i in self.micros for j in range(self.microservices[i].num_containers)])

        # Constraints
        # Every container is scheduled exactly once
        for i in self.micros:
            for j in range(self.microservices[i].num_containers):
                self.model.AddExactlyOne(self.sched[i, j, k] for k in self.nods)

        for k in self.nods:
            # Container limit
            self.model.Add(sum(self.sched[i, j, k] for i in self.micros for j in range(self.microservices[i].num_containers)) <= self.nodes[k].contlim)

            # CPU limit
            self.model.Add(sum(self.sched[i, j, k] * self.microservices[i].cpureq for i in self.micros for j in range(self.microservices[i].num_containers)) <= self.nodes[k].cpulim)

            # Memory limit
            self.model.Add(sum(self.sched[i, j, k] * self.microservices[i].memreq for i in self.micros for j in range(self.microservices[i].num_containers)) <= self.nodes[k].memlim)

            # Objectives
            # Cost
            objective.append(cp_model.LinearExpr.Term(self.used[k], self.nodes[k].cost))

        self.model.Minimize(cp_model.LinearExpr.Sum(objective))

        self.status = self.solver.Solve(self.model)

    def print_solution(self):
        if self.status != cp_model.OPTIMAL:
            raise NoSolutionError('CP-SAT failed to find an optimal solution.')

        self.solution.cost = self.solver.ObjectiveValue()

        for k in self.nods:
            if self.solver.Value(self.used[k]):
                for i in self.micros:
                    for j in range(self.microservices[i].num_containers):
                        self.solution.assign(self.nodes[k], self.microservices[i], self.solver.Value(self.sched[i, j, k]))

        super().print_solution()
