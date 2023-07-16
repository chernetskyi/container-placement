from model.solution import Solution


class Solver:
    def __init__(self, scenario):
        self.microservices = scenario.microservices
        self.nodes = scenario.nodes
        self.solution = Solution(scenario)

    def solve(self):
        raise NotImplementedError()

    def print_solution(self):
        print(self.solution)


class NoSolutionError(RuntimeError):
    pass
