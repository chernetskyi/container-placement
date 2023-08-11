from itertools import product
from yaml import safe_load

from model.microservice import Microservice
from model.node import Node
from model.utils import clean_double_dict


class Scenario:
    def __init__(self, file):
        scenario = {}
        with file as f:
            scenario = safe_load(f)

        self.micros = {
            m: Microservice(
                m,
                scenario['microservices'][m]['cpureq'],
                scenario['microservices'][m]['memreq'],
                scenario['microservices'][m]['containers']
            ) for m in scenario['microservices']}

        self.nodes = {
            n: Node(
                n,
                scenario['nodes'][n]['cost'],
                scenario['nodes'][n]['cpulim'],
                scenario['nodes'][n]['memlim'],
                scenario['nodes'][n]['contlim'],
                scenario['nodes'][n]['zone'],
            ) for n in scenario['nodes']}

        self.__datarate = scenario['datarate']
        self.__intra = scenario['data_cost']['intrazone']
        self.__inter = scenario['data_cost']['interzone']

        self.micros_tpl = tuple(self.micros.keys())
        self.nodes_tpl = tuple(self.nodes.keys())

        self.conts = sum(map(lambda m: m.containers, self.micros.values()))

    def cost(self, mapping):
        mp = clean_double_dict(mapping)

        infra_cost = sum(self.nodes[node].cost for node in mp)
        data_cost = sum(sum(self.data_rate(prod, cons) for prod, cons in product(mp[n1], mp[n2])) *\
                        self.data_cost(n1, n2) for n1, n2 in product(mp, mp))

        return infra_cost + data_cost

    def data_rate(self, prod, cons):
        return self.__datarate.get(prod, {}).get(cons, 0)

    def data_cost(self, n1, n2):
        if n1 == n2:
            return 0
        elif self.nodes[n1].zone == self.nodes[n2].zone:
            return self.__intra
        else:
            return self.__inter

    def reset_nodes(self):
        for n in self.nodes.values():
            n.cpu, n.mem, n.cont = 0, 0, 0
