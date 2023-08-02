import logging
import random

from model.solver import Solver, NoSolutionError
from model.utils import get_microservice


class PSOSolver(Solver):
    def solve(self):
        c_ran = range(sum(m.containers for m in self.scenario.micros))

        for i in range(self.iterations):
            for particle in self.particles:

                for dim in c_ran:
                    particle.velocity[dim] = self.__update_velocity(particle, dim)
                    particle.position[dim] = self.__update_position(particle, dim)

                particle.cost = objective(self.scenario, particle.position)

                if particle.cost < particle.best_cost:
                    particle.best_position = particle.position[:]
                    particle.best_cost = particle.cost

                    if particle.best_cost < self.cost:
                        logging.info(f'Swarm\'s best position updated at iteration {i}/{self.iterations}')
                        self.position = particle.best_position[:]
                        self.cost = particle.best_cost

    def __update_velocity(self, part, dim):
        n_len = len(self.scenario.nodes)

        r1 = random.random()
        r2 = random.random()

        dim_velocity = self.inertia * part.velocity[dim] + \
            self.cognitive * r1 * (part.best_position[dim] - part.position[dim]) + \
            self.social * r2 * (self.position[dim] - part.position[dim])
        return self.handle_velocity(dim_velocity, -(n_len - 1), n_len)

    def __update_position(self, part, dim):
        n_len = len(self.scenario.nodes)
        dim_position = int(part.position[dim] + part.velocity[dim])
        return self.handle_position(dim_position, 0, n_len)

    def print_solution(self, file):
        if self.cost == float('inf'):
            logging.error('Particle Swarm Optimization failed to find a solution')
            raise NoSolutionError(
                'Particle Swarm Optimization failed to find a solution.')

        i = 0
        for micro in self.scenario.micros:
            for container in range(micro.containers):
                self.mapping[self.scenario.nodes[self.position[i]]][micro] += 1
                i += 1

        super().print_solution(file)

    def __init__(
            self,
            scenario,
            particles,
            iterations,
            inertia,
            cognitive,
            social,
            random_init_position,
            zero_init_velocity,
            velocity_handling,
            position_handling):

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

        self.position = None
        self.particles = [Particle(scenario,
                                   random_init_position,
                                   zero_init_velocity) for _ in range(particles)]

        for particle in self.particles:
            if particle.best_cost < self.cost:
                self.position = particle.best_position[:]
                self.cost = particle.best_cost

        if self.position is None:
            logging.info('No viable solutions were generated on init')
            self.position = random.choice([particle.position
                                           for particle in self.particles])[:]

    @staticmethod
    def none_handle(value, min, max):
        return value

    @staticmethod
    def boundary_handle(value, min, max):
        if value < min:
            return min
        elif value >= max:
            return max - 1
        return value

    @staticmethod
    def periodic_handle(value, min, max):
        if value >= max:
            return value % max
        elif value < min:
            return value % max if min >= 0 else (value % max) - max
        return value

    @staticmethod
    def random_handle(value, min, max):
        return value if min <= value < max else random.randrange(min, max)


class Particle:
    def __init__(self, scenario, random_init_position, zero_init_velocity):
        n_len = len(scenario.nodes)
        c_len = sum(m.containers for m in scenario.micros)

        self.velocity = [0] * c_len if zero_init_velocity else \
                        random.choices(range(-n_len + 1, n_len), k=c_len)

        self.position = Particle.random_position(n_len, c_len) if random_init_position \
                        else Particle.viable_position(scenario)
        self.best_position = self.position

        self.cost = objective(scenario, self.position)
        self.best_cost = self.cost

    @staticmethod
    def random_position(n_len, c_len):
        return random.choices(range(n_len), k=c_len)

    @staticmethod
    def viable_position(scenario):
        n_len = len(scenario.nodes)
        c_len = sum(m.containers for m in scenario.micros)

        nodes = list(enumerate(scenario.nodes))
        random.shuffle(nodes)

        position = [-1] * c_len

        for c in range(c_len):
            micro = scenario.micros[get_microservice(scenario.micros, c)]
            for i, node in nodes:
                if node.fits(micro):
                    node.add(micro)
                    position[c] = i
                    break

        scenario.nodes = list(map(lambda n: n.reset(), scenario.nodes))

        if -1 in position:
            logging.debug('Failed to initialize particle with a viable position. Falling back to random.')
            return Particle.random_position(n_len, c_len)

        return position


def objective(scenario, position):
    mapping = {n: {m: 0 for m in scenario.micros} for n in scenario.nodes}

    c_ran = range(sum(m.containers for m in scenario.micros))

    for container in c_ran:
        node = scenario.nodes[position[container]]
        micro = scenario.micros[get_microservice(scenario.micros, container)]

        if not node.fits(micro):
            return float('inf')

        node.add(micro)

        mapping[node][micro] += 1

    scenario.nodes = list(map(lambda n: n.reset(), scenario.nodes))

    infra_cost = scenario.infra_cost(mapping)
    data_cost = scenario.data_cost(mapping)

    return infra_cost + data_cost
