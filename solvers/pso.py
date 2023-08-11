import logging
import random

from model.solver import Solver, NoSolutionError


class PSOSolver(Solver):
    def solve(self):
        for i in range(self.iterations):
            for particle in self.particles:
                for dim in range(self.scenario.conts):
                    particle.velocity[dim], particle.position[dim] = self.__update_particle(particle, dim)

                particle.cost = objective(self.scenario, particle.position)

                if particle.cost < particle.best_cost:
                    particle.best_position = particle.position[:]
                    particle.best_cost = particle.cost

                    if particle.best_cost < self.cost:
                        logging.debug(f"Swarm's best position updated at iteration {i}/{self.iterations}")
                        self.position = particle.best_position[:]
                        self.cost = particle.best_cost

        logging.debug('Finished solving')

    def __update_particle(self, part, dim):
        r1, r2 = random.random(), random.random()

        dim_velocity = self.inertia * part.velocity[dim] + \
            self.cognitive * r1 * (part.best_position[dim] - part.position[dim]) + \
            self.social * r2 * (self.position[dim] - part.position[dim])

        dim_position = round(part.position[dim] + dim_velocity)

        return self.handle_boundary(dim_velocity, dim_position, len(self.scenario.nodes) - 1)

    def solution(self):
        if self.cost == float('inf'):
            logging.error('Particle Swarm Optimization failed to find a solution')
            raise NoSolutionError(
                'Particle Swarm Optimization failed to find a solution.')

        c = 0
        for m, micro in self.scenario.micros.items():
            for _ in range(micro.containers):
                n = self.scenario.nodes_tpl[self.position[c]]
                self.mapping[n][m] += 1
                c += 1

        return super().solution()

    def __init__(self,
                 scenario,
                 particles,
                 iterations,
                 inertia,
                 cognitive,
                 social,
                 random_init_position,
                 zero_init_velocity,
                 boundary_handling):

        super().__init__(scenario)

        handling_methods = {
            'absorbing': PSOSolver.absorbing,
            'reflecting': PSOSolver.reflecting
        }

        self.iterations = iterations
        self.inertia = inertia
        self.cognitive = cognitive
        self.social = social
        self.handle_boundary = handling_methods[boundary_handling]

        self.position = None

        logging.debug('Starting solving')

        self.particles = [Particle(scenario,
                                   random_init_position,
                                   zero_init_velocity) for _ in range(particles)]

        best_particle = min(self.particles, key = lambda p: p.best_cost)

        if best_particle.best_cost < self.cost:
            self.position = best_particle.best_position[:]
            self.cost = best_particle.best_cost

        if self.position is None:
            logging.info('No viable solutions were generated on init')
            self.position = random.choice([particle.position
                                           for particle in self.particles])[:]

    @staticmethod
    def absorbing(vel, pos, max_pos):
        if pos < 0:
            return 0, 0
        elif pos > max_pos:
            return 0, max_pos
        return vel, pos

    @staticmethod
    def reflecting(vel, pos, max_pos):
        if pos < 0:
            return -vel, 0
        elif pos > max_pos:
            return -vel, max_pos
        return vel, pos


class Particle:
    def __init__(self, scenario, random_init_position, zero_init_velocity):
        n_len = len(scenario.nodes)
        c_len = scenario.conts

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
        c_len = scenario.conts

        i_n = list(enumerate(scenario.nodes_tpl))
        random.shuffle(i_n)

        position = [-1] * c_len

        c = 0
        for m in scenario.micros_tpl:
            micro = scenario.micros[m]
            for _ in range(micro.containers):
                for i, n in i_n:
                    node = scenario.nodes[n]
                    if node.fits(micro):
                        node.add(micro, 1)
                        position[c] = i
                        break
                c += 1

        scenario.reset_nodes()

        if -1 in position:
            logging.debug('Failed to initialize particle with a viable position. Falling back to random.')
            return Particle.random_position(n_len, c_len)

        return position


def objective(scenario, position):
    mapping = {n: {m: 0 for m in scenario.micros} for n in scenario.nodes}

    c = 0
    for m in scenario.micros_tpl:
        micro = scenario.micros[m]
        for _ in range(micro.containers):
            n = scenario.nodes_tpl[position[c]]
            node = scenario.nodes[n]

            if not node.fits(micro):
                scenario.reset_nodes()
                return float('inf')

            node.add(micro, 1)
            mapping[n][m] += 1
            c += 1

    scenario.reset_nodes()

    return scenario.cost(mapping)
