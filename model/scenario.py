import yaml

from model.microservice import Microservice
from model.node import Node
from model.utils import clean_double_dict


class Scenario:
    def read_from_yaml(self, file):
        scenario = {}
        with file as f:
            scenario = yaml.safe_load(f)
        self.read_from_dict(scenario)

    def read_from_dict(self, scenario):
        self.micros = [
            Microservice(
                m,
                scenario['microservices'][m]['cpureq'],
                scenario['microservices'][m]['memreq'],
                scenario['microservices'][m]['containers']
            ) for m in scenario['microservices']]

        self.datarate = scenario['datarate']

        self.nodes = [
            Node(
                n,
                scenario['nodes'][n]['cost'],
                scenario['nodes'][n]['cpulim'],
                scenario['nodes'][n]['memlim'],
                scenario['nodes'][n]['contlim'],
                scenario['nodes'][n]['zone'],
            ) for n in scenario['nodes']]

        self.__intra = scenario['data_cost']['intrazone']
        self.__inter = scenario['data_cost']['interzone']

    def infra_cost(self, mapping):
        mp = clean_double_dict(mapping)
        return sum(node.cost for node in mp)

    def data_cost(self, mapping):
        mp = clean_double_dict(mapping)

        cost = 0

        for n1 in mp:
            for n2 in mp:
                if n1.name == n2.name:
                    continue

                data = 0
                for prod in mp[n1]:
                    for cons in mp[n2]:
                        data += self.datarate.get(prod.name, {}).get(cons.name, 0)

                cost += data * self.node_data_cost(n1, n2)

        return cost

    def node_data_cost(self, n1, n2):
        if n1.name == n2.name:
            return 0
        elif n1.zone == n2.zone:
            return self.__intra
        else:
            return self.__inter
