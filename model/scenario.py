import yaml

from model.microservice import Microservice
from model.node import Node


class Scenario:
    def read_from_yaml(self, filename):
        scenario = {}
        with open(filename, 'r') as f:
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

        self.__same_zone = scenario['bandlim']['same_zone']
        self.__different_zones = scenario['bandlim']['different_zones']

    def band(self, mapping, node1, node2):
        band = 0
        for producer in mapping[node1]:
            for consumer in mapping[node2]:
                datarate = self.datarate.get(producer, {}).get(consumer, 0)
                band += datarate / producer.containers * mapping[node1][producer]
        return band

    def bandlim(self, node1, node2):
        if node1.name == node2.name:
            return float('inf')
        elif node1.zone == node2.zone:
            return self.__same_zone
        else:
            return self.__different_zones
