class Solver:
    def __init__(self, scenario):
        self.scenario = scenario
        self.mapping = {n: {m: 0 for m in scenario.micros}
                        for n in scenario.nodes}
        self.cost = float('inf')
        self.dataloss = float('inf')

    def solve(self):
        raise NotImplementedError()

    def print_solution(self):
        mapping = {n: {m: self.mapping[n][m] for m in self.mapping[n]
                       if self.mapping[n][m]} for n in self.mapping}
        mapping = {n: mapping[n] for n in mapping if mapping[n]}

        s = f'Total cost: {self.cost:.2f}\nData throttled: {self.dataloss}\n'

        for node in mapping:
            s += f'\nNode "{node.name}":'

            cpu = 0
            mem = 0
            cont = 0

            for micro in mapping[node]:
                s += f'\n  - {mapping[node][micro]} containers of microservice "{micro.name}"'

                num = mapping[node][micro]
                cpu += num * micro.cpureq
                mem += num * micro.memreq
                cont += num

            s += f'\n{cpu}/{node.cpulim} vCPU, {mem}/{node.memlim} MiB RAM, {cont}/{node.contlim} containers\n'

        print(s)


class NoSolutionError(RuntimeError):
    pass
