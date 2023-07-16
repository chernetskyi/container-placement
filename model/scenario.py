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
        self.microservices = [
            Microservice(
                m,
                scenario['microservices'][m]['cpureq'],
                scenario['microservices'][m]['memreq'],
                scenario['microservices'][m]['num_containers']
            ) for m in scenario['microservices']]
        self.nodes = [
            Node(
                n,
                scenario['nodes'][n]['cost'],
                scenario['nodes'][n]['cpulim'],
                scenario['nodes'][n]['memlim'],
                scenario['nodes'][n]['contlim'],
                scenario['nodes'][n]['zone'],
            ) for n in scenario['nodes']]
