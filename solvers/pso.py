from random import choice, choices, random

from model.solver import Solver, NoSolutionError


class Particle:
    def __init__(self, microservices, nodes):
        nodel = len(nodes)
        contl = sum(m.num_containers for m in microservices)

        self.velocity = choices(list(range(-nodel+1, nodel)), k=contl)
        self.position = choices(list(range(nodel)), k=contl)
        self.best_position = self.position[:]
        self.cost = cost(microservices, nodes, self.position)
        self.best_cost = self.cost


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

        self.particles = [Particle(self.microservices, self.nodes) for _ in range(self.particlel)]
        self.swarm_best_position = None
        self.swarm_best_cost = float('inf')

        for particle in self.particles:
            if particle.cost < self.swarm_best_cost:
                self.swarm_best_position = particle.position[:]
                self.swarm_best_cost = particle.cost

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

                particle.cost = cost(self.microservices, self.nodes, particle.position)
                if particle.cost < particle.best_cost:
                    particle.best_position = particle.position[:]
                    particle.best_cost = particle.cost

                    if particle.cost < self.swarm_best_cost:
                        self.swarm_best_position = particle.position[:]
                        self.swarm_best_cost = particle.cost

    def print_solution(self):
        if self.swarm_best_cost == float('inf'):
            raise NoSolutionError('Particle Swarm Optimization algorithm failed to find a solution.')

        self.solution.cost = self.swarm_best_cost

        i = 0
        for microservice in self.microservices:
            for container in range(microservice.num_containers):
                self.solution.assign(self.nodes[self.swarm_best_position[i]], microservice, 1)
                i += 1

        super().print_solution()


def get_microservice(microservices, container):
    for m in range(len(microservices)):
        microservice_containers = microservices[m].num_containers
        if container < microservice_containers:
            return m
        container -= microservice_containers
    raise IndexError('Specified container does not belong to any microservice')


def cost(microservices, nodes, position):
    containers = sum(m.num_containers for m in microservices)

    for container in range(containers):
        node = nodes[position[container]]
        microservice = microservices[get_microservice(microservices, container)]
        if not node.fits(microservice):
            return float('inf')
        node.cont += 1
        node.cpu += microservice.cpureq
        node.mem += microservice.memreq

    value = sum(node.cost for node in nodes if node.cont)

    nodes = list(map(lambda n: n.reset(), nodes))

    return value
