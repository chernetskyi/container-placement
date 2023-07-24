import random

from model.solver import Solver, NoSolutionError
from model.utils import clean_double_dict, get_microservice


class Particle:
    def __init__(self, scenario):
        n_len = len(scenario.nodes)
        c_len = sum(m.containers for m in scenario.micros)

        self.velocity = random.choices(list(range(-n_len+1, n_len)), k=c_len)
        self.position = random.choices(list(range(n_len)), k=c_len)
        self.best_position = self.position[:]

        obj = objective(scenario, self.position)
        self.cost = obj['cost']
        self.dataloss = obj['dataloss']

        self.best_cost = self.cost
        self.best_dataloss = self.dataloss


class PSOSolver(Solver):
    def __init__(self, scenario, particles, iterations, inertia, cognitive, social, velocity_handling, position_handling):
        super().__init__(scenario)

        handling_methods = {
            'none': PSOSolver.none_handle,
            'boundary': PSOSolver.boundary_handle,
            'periodic': PSOSolver.periodic_handle,
            'random': PSOSolver.random_handle
        }

        self.iterations = iterations
        self.inertia = inertia
        self.cognitive = cognitive
        self.social = social
        self.handle_velocity = handling_methods[velocity_handling]
        self.handle_position = handling_methods[position_handling]

        self.best_position = None
        self.particles = [Particle(scenario) for _ in range(particles)]

        for particle in self.particles:
            if (particle.cost <= self.cost) and (particle.dataloss <= self.dataloss):
                self.best_position = particle.position[:]
                self.cost = particle.cost
                self.dataloss = particle.dataloss

        if self.best_position is None:
            self.best_position = random.choice([particle.position for particle in self.particles])[:]

    def __particle_update_velocity(self, particle, dim):
        n_len = len(self.scenario.nodes)

        r1 = random.random()
        r2 = random.random()

        dim_velocity = self.inertia * particle.velocity[dim] + \
            self.cognitive * r1 * (particle.best_position[dim] - particle.position[dim]) + \
            self.social * r2 * (self.best_position[dim] - particle.position[dim])
        return self.handle_velocity(dim_velocity, -(n_len - 1), n_len)

    def __particle_update_position(self, particle, dim):
        n_len = len(self.scenario.nodes)
        dim_position = particle.position[dim] + int(particle.velocity[dim])
        return self.handle_position(dim_position, 0, n_len)

    def solve(self):
        for _ in range(self.iterations):
            for particle in self.particles:
                c_len = sum(m.containers for m in self.scenario.micros)

                for dim in range(c_len):
                    particle.velocity[dim] = self.__particle_update_velocity(particle, dim)
                    particle.position[dim] = self.__particle_update_position(particle, dim)

                obj = objective(self.scenario, particle.position)
                particle.cost = obj['cost']
                particle.dataloss = obj['dataloss']

                if (particle.cost <= particle.best_cost) and (particle.dataloss <= particle.best_dataloss):
                    particle.best_position = particle.position[:]
                    particle.best_cost = particle.cost
                    particle.best_dataloss = particle.dataloss

                    if (particle.cost <= self.cost) and (particle.dataloss <= self.dataloss):
                        self.best_position = particle.position[:]
                        self.cost = particle.cost
                        self.dataloss = particle.dataloss

    def print_solution(self):
        if self.cost == float('inf'):
            raise NoSolutionError('Particle Swarm Optimization algorithm failed to find a solution.')

        i = 0
        for micro in self.scenario.micros:
            for container in range(micro.containers):
                self.mapping[self.scenario.nodes[self.best_position[i]]][micro] += 1
                i += 1

        super().print_solution()

    def none_handle(value, min, max):
        return value

    def boundary_handle(value, min, max):
        if value < min:
            return min
        elif value >= max:
            return max - 1
        return value

    def periodic_handle(value, min, max):
        if value >= max:
            return value % max
        elif value < min:
            return value % max if min >= 0 else (value % max) - max
        return value

    def random_handle(value, min, max):
        return value if min <= value < max else random.choice(list(range(min, max)))


def objective(scenario, position):
    mapping = {n: {m: 0 for m in scenario.micros} for n in scenario.nodes}

    nodes = scenario.nodes[:]
    c_len = sum(m.containers for m in scenario.micros)

    for container in range(c_len):
        node = nodes[position[container]]
        micro = scenario.micros[get_microservice(scenario.micros, container)]

        if not node.fits(micro):
            return {'cost': float('inf'), 'dataloss': float('inf')}

        node.cont += 1
        node.cpu += micro.cpureq
        node.mem += micro.memreq

        mapping[node][micro] += 1

    mapping = clean_double_dict(mapping)

    cost = sum(node.cost for node in mapping)

    dataloss = 0

    for node1 in mapping:
        for node2 in mapping:
            dataloss += max(0, scenario.band(mapping, node1, node2) - scenario.bandlim(node1, node2))

    return {'cost': cost, 'dataloss': dataloss}
