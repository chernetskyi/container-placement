class Solver:
    def __init__(self, microservices, nodes):
        self.microservices = microservices
        self.nodes = nodes

    def solve(self):
        raise NotImplementedError()

    def solution(self):
        raise NotImplementedError()


class NoSolutionError(RuntimeError):
    pass
