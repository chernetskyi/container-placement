from model.utils import clean_double_dict, to_cpu


class Solver:
    def __init__(self, scenario):
        self.scenario = scenario
        self.mapping = {n: {m: 0 for m in scenario.micros}
                        for n in scenario.nodes}
        self.cost = float('inf')

    def solve(self):
        raise NotImplementedError()

    def print_solution(self, file):
        mapping = clean_double_dict(self.mapping)

        s = f'Total cost: {self.cost:.2f}\n'

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

            s += f'\n{to_cpu(cpu)}/{to_cpu(node.cpulim)} CPU, {mem}/{node.memlim} MiB RAM, {cont}/{node.contlim} containers\n'

        print(s, file=file)


class NoSolutionError(RuntimeError):
    pass
