import yaml


class Microservice:
    def __init__(self, name, cpureq, memreq, num_containers):
        self.name = name
        self.cpureq = cpureq
        self.memreq = memreq
        self.num_containers = num_containers

    def __str__(self):
        return f'Microservice "{self.name}" ({self.cpureq} vCPU, {self.memreq} MiB RAM)'


class Node:
    def __init__(self, name, cost, cpulim, memlim, contlim):
        self.name = name
        self.cost = cost
        self.cpulim = cpulim
        self.memlim = memlim
        self.contlim = contlim
        self.reset()

    def __str__(self):
        return f'Node "{self.name}" ${self.cost}: {self.cpulim} vCPU, {self.memlim} MiB RAM, {self.contlim} containers'

    def reset(self):
        self.cpu = 0
        self.mem = 0
        self.cont = 0

    def fits(self, container):
        return (self.cpu + container.cpureq) <= self.cpulim and \
                (self.mem + container.memreq) <= self.memlim and \
                (self.cont + 1) <= self.contlim


def read_scenario_from_yaml(filename):
    scenario = []
    with open(filename, 'r') as f:
        scenario = yaml.safe_load(f)

    return {'microservices': [Microservice(m, **scenario['microservices'][m]) for m in scenario['microservices']],
            'nodes': [Node(n, **scenario['nodes'][n]) for n in scenario['nodes']]}
