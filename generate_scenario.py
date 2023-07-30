#!/usr/bin/env python3
import argparse
import petname
import random
import yaml


zones = ('alpha', 'beta', 'gamma', 'delta', 'epsilon', 'zeta', 'eta', 'theta', 'iota',
         'kappa', 'lambda', 'mu', 'nu', 'xi', 'omicron', 'pi', 'rho', 'sigma', 'tau',
         'upsilon', 'phi', 'chi', 'psi', 'omega')


def microservice(min, max):
    cpureq = 250 * random.randint(1, 16)
    memreq = 128 * random.randint(1, 64)
    containers = random.randint(min, max)

    return {'cpureq': cpureq,
            'memreq': memreq,
            'containers': containers}


def datarate(microservice_list, no_data, min, max):
    if no_data:
        return {}

    length = int(len(microservice_list) * random.uniform(0.6, 0.8))
    micros = random.sample(microservice_list, length)
    tree = Tree(micros)

    return tree.dict(min, max)


def node(zone_num):
    r1, r2 = random.randint(1, 128), random.randint(1, 128)
    cpulim = 1000 * r1
    memlim = 512 * r2
    cost = round((r1 + r2) * random.uniform(1, 2), 2)
    contlim = int(max(r1, r2) * random.uniform(0.5, 1.5))
    zone = random.choice(zones[:zone_num])

    return {'cost': cost,
            'cpulim': cpulim,
            'memlim': memlim,
            'contlim': contlim,
            'zone': zone}


def main():
    parser = argparse.ArgumentParser(
        description='Generate scenario for node-container placement.')
    parser.add_argument('-m', '--micros',
                        type=int, default=random.randint(20, 40),
                        help='number of microservices to generate')
    parser.add_argument('--minc', '--min-containers',
                        type=int, default=1,
                        help='minimum number of containers in microservice')
    parser.add_argument('--maxc', '--max-containers',
                        type=int, default=10,
                        help='maximum number of containers in microservice')
    parser.add_argument('--no-data',
                        action='store_true',
                        help='no communication between microservices')
    parser.add_argument('--mind', '--min-datarate',
                        type=int, default=1,
                        help='minimum amount of data moved between two microservices')
    parser.add_argument('--maxd', '--max-datarate',
                        type=int, default=10,
                        help='maximum amount of data moved between two microservices')
    parser.add_argument('-n', '--nodes',
                        type=int, default=random.randint(50, 150),
                        help='number of nodes to generate')
    parser.add_argument('-z',  '--zones',
                        type=int, default=3,
                        help = 'maximum number of zones to use')
    args = parser.parse_args()

    m_names = [petname.Generate(2) for _ in range(args.micros)]
    n_names = [petname.Generate(1) for _ in range(args.nodes)]

    microservices = {'microservices': {m: microservice(args.minc, args.maxc)
                                       for m in m_names}}
    nodes = {'nodes': {n: node(args.zones) for n in n_names}}
    data = {'datarate': datarate(m_names, args.no_data, args.mind, args.maxd)}
    data_cost = {'data_cost': {'intrazone': 0.01, 'interzone': 0.02}}

    scenario = microservices | data | nodes | data_cost

    print(yaml.dump(scenario))


class Tree:
    class Node:
        def __init__(self, name):
            self.name = name
            self.children = []

    def __init__(self, nodes):
        self.nodes = [Tree.Node(nodes[0])]
        for node in nodes[1:]:
            parent = random.choice(self.nodes)
            new_node = Tree.Node(node)
            parent.children.append(new_node)
            self.nodes.append(new_node)

    def dict(self, min, max):
        return {n.name: {c.name: round(random.uniform(min, max), 2) for c in n.children}
                for n in self.nodes if n.children}


if __name__ == '__main__':
    main()
