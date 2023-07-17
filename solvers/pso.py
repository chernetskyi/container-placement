from random import choice, choices, random

from model.solver import Solver, NoSolutionError


class Particle:
    def __init__(self, microservices, datarate, nodes, bandlim):
        nodel = len(nodes)
        contl = sum(m.num_containers for m in microservices)

        self.velocity = choices(list(range(-nodel+1, nodel)), k=contl)
        self.position = choices(list(range(nodel)), k=contl)
        self.best_position = self.position[:]

        obj = objective(microservices, datarate, nodes, bandlim, self.position)
        self.cost = obj['cost']
        self.dataloss = obj['dataloss']

        self.best_cost = self.cost
        self.best_dataloss = self.dataloss


class PSOSolver(Solver):
    velocity_bound_handling_methods = {None, 'boundary', 'periodic', 'random'}
    position_bound_handling_methods = {'boundary', 'periodic', 'random'}

    def __init__(self, scenario, iterations, particles, inertia, cognitive, social, velocity_bound_handling, position_bound_handling):
        super().__init__(scenario)

        self.iterations = iterations
        self.particlel = particles
        self.inertia = inertia
        self.cognitive = cognitive
        self.social = social

        if velocity_bound_handling in PSOSolver.velocity_bound_handling_methods:
            self.velocity_bound_handling = velocity_bound_handling
        else:
            raise ValueError(f'Unknown velocity_bound_handling value {velocity_bound_handling}.')

        if position_bound_handling in PSOSolver.position_bound_handling_methods:
            self.position_bound_handling = position_bound_handling
        else:
            raise ValueError(f'Unknown position_bound_handling value {position_bound_handling}.')

    def solve(self):
        nodel = len(self.nodes)
        contl = sum(m.num_containers for m in self.microservices)

        self.particles = [Particle(self.microservices, self.datarate, self.nodes, self.bandlim) for _ in range(self.particlel)]
        self.swarm_best_position = None

        for particle in self.particles:
            if (particle.cost < self.cost) and (particle.dataloss < self.dataloss):
                self.swarm_best_position = particle.position[:]
                self.cost = particle.cost
                self.dataloss = particle.dataloss

        if self.swarm_best_position is None:
            self.swarm_best_position = choice([particle.position for particle in self.particles])[:]

        for _ in range(self.iterations):
            for particle in self.particles:
                for dim in range(contl):
                    r1 = random()
                    r2 = random()
                    dim_velocity = self.inertia * particle.velocity[dim] + \
                        self.cognitive * r1 * (particle.best_position[dim] - particle.position[dim]) + \
                        self.social * r2 * (self.swarm_best_position[dim] - particle.position[dim])

                    if self.velocity_bound_handling == 'boundary':
                        if dim_velocity < -nodel + 1:
                            dim_velocity = -nodel + 1
                        elif dim_velocity > nodel - 1:
                            dim_velocity = nodel - 1
                    elif self.velocity_bound_handling == 'periodic':
                        if dim_velocity < -nodel + 1:
                            dim_velocity = (dim_velocity % nodel) - nodel
                        elif dim_velocity > nodel - 1:
                            dim_velocity %= nodel
                    elif self.velocity_bound_handling == 'random':
                        if not -nodel + 1 <= dim_velocity <= nodel - 1:
                            dim_velocity = choice(list(range(-nodel + 1, nodel)))

                    particle.velocity[dim] = dim_velocity

                    dim_position = particle.position[dim] + int(particle.velocity[dim])

                    if self.position_bound_handling == 'boundary':
                        if dim_position < 0:
                            dim_position = 0
                        elif dim_position > nodel - 1:
                            dim_position = nodel - 1
                    elif self.position_bound_handling == 'periodic':
                        if dim_position < 0:
                            dim_position = (dim_position % nodel) - nodel
                        elif dim_position > nodel - 1:
                            dim_position %= nodel
                    elif self.position_bound_handling == 'random':
                        if not 0 <= dim_position <= nodel - 1:
                            dim_position = choice(list(range(nodel)))

                    particle.position[dim] = dim_position

                obj = objective(self.microservices, self.datarate, self.nodes, self.bandlim, particle.position)
                particle.cost = obj['cost']
                particle.dataloss = obj['dataloss']

                if (particle.cost < particle.best_cost) and (particle.dataloss < particle.best_dataloss):
                    particle.best_position = particle.position[:]
                    particle.best_cost = particle.cost
                    particle.best_dataloss = particle.dataloss

                    if (particle.cost < self.cost) and (particle.dataloss < self.dataloss):
                        self.swarm_best_position = particle.position[:]
                        self.cost = particle.cost
                        self.dataloss = particle.dataloss

    def print_solution(self):
        if self.cost == float('inf'):
            raise NoSolutionError('Particle Swarm Optimization algorithm failed to find a solution.')

        i = 0
        for microservice in self.microservices:
            for container in range(microservice.num_containers):
                self.mapping[self.nodes[self.swarm_best_position[i]]][microservice] += 1
                i += 1

        super().print_solution()


def get_microservice(microservices, container):
    for m in range(len(microservices)):
        microservice_containers = microservices[m].num_containers
        if container < microservice_containers:
            return m
        container -= microservice_containers
    raise IndexError('Specified container does not belong to any microservice')


def objective(microservices, datarate, nodes, bandlim, position):
    mapping = {node: {microservice: 0 for microservice in microservices} for node in nodes}

    nods = nodes[:]
    containers = sum(m.num_containers for m in microservices)

    for container in range(containers):
        node = nods[position[container]]
        microservice = microservices[get_microservice(microservices, container)]

        if not node.fits(microservice):
            return {'cost': float('inf'), 'dataloss': float('inf')}

        node.cont += 1
        node.cpu += microservice.cpureq
        node.mem += microservice.memreq

        mapping[node][microservice] += 1

    mapping = {n: {m: mapping[n][m] for m in mapping[n] if mapping[n][m]} for n in mapping}
    mapping = {n: mapping[n] for n in mapping if mapping[n]}

    cost = sum(node.cost for node in mapping)

    dataloss = 0

    for node1 in mapping:
        for node2 in mapping:
            dataloss += max(0, band(mapping, datarate, node1, node2) - bandlimf(bandlim, node1, node2))

    return {'cost': cost, 'dataloss': dataloss}


def band(mapping, datarate, node1, node2):
    band = 0
    for m1 in mapping[node1]:
        for m2 in mapping[node2]:
            band += datarate[m1][m2] / m1.num_containers * mapping[node1][m1]
    return band


def bandlimf(bandlim, node1, node2):
    if node1.name == node2.name:
        return float('inf')
    elif node1.zone == node2.zone:
        return bandlim['same_zone']
    else:
        return bandlim['different_zones']
