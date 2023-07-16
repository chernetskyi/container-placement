class Solver:
    def __init__(self, scenario):
        self.microservices = scenario.microservices
        self.nodes = scenario.nodes
        self.datarate = scenario.datarate
        self.bandlim = scenario.bandlim
        self.mapping = {node: {microservice: 0 for microservice in self.microservices} for node in self.nodes}
        self.cost = float('inf')
        self.dataloss = float('inf')

    def solve(self):
        raise NotImplementedError()

    def print_solution(self):
        mapping = {n: {m: self.mapping[n][m] for m in self.mapping[n] if self.mapping[n][m]} for n in self.mapping}
        mapping = {n: mapping[n] for n in mapping if mapping[n]}

        s = f'Total cost: {self.cost:.2f}\nData throttled: {self.dataloss}\n'

        for node in mapping:
            s += f'\nNode "{node.name}":'

            cpu = 0
            mem = 0
            cont = 0

            for microservice in mapping[node]:
                s += f'\n  - {mapping[node][microservice]} containers of microservice "{microservice.name}"'

                num = mapping[node][microservice]
                cpu += num * microservice.cpureq
                mem += num * microservice.memreq
                cont += num

            s += f'\n{cpu}/{node.cpulim} vCPU, {mem}/{node.memlim} MiB RAM, {cont}/{node.contlim} containers\n'

        print(s)


class NoSolutionError(RuntimeError):
    pass
