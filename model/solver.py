from model.utils import clean_double_dict


class Solver:
    def __init__(self, scenario):
        self.scenario = scenario
        self.mapping = {n: {m: 0 for m in scenario.micros} for n in scenario.nodes}
        self.cost = float('inf')

    def solve(self):
        raise NotImplementedError()

    def solution(self):
        mapping = clean_double_dict(self.mapping)

        res = f'Total cost: {self.cost:.2f}\n'

        for n in mapping:
            node = self.scenario.nodes[n]

            res += f'\nNode "{n}":'

            for m in mapping[n]:
                num = mapping[n][m]
                node.add(self.scenario.micros[m], num)
                res += f'\n  - {num} containers of microservice "{m}"'

            res += f'\n{node.info()}\n'

        return res


class NoSolutionError(RuntimeError):
    pass
