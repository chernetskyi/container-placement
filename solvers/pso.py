import logging
import random

from model.solver import Solver, NoSolutionError


class PSOSolver(Solver):
    def solve(self):
        for i in range(self.iterations):
            for particle in self.particles:
                for dim in range(self.scenario.conts):
                    particle.velocity[dim] = self.__update_velocity(particle, dim)
                    particle.position[dim] = self.__update_position(particle, dim)

                particle.cost = objective(self.scenario, particle.position)

                if particle.cost < particle.best_cost:
                    particle.best_position = particle.position[:]
                    particle.best_cost = particle.cost

                    if particle.best_cost < self.cost:
                        logging.info(f"Swarm's best position updated at iteration {i}/{self.iterations}")
                        self.position = particle.best_position[:]
                        self.cost = particle.best_cost

    def __update_velocity(self, part, dim):
        n_len = len(self.scenario.nodes)
        r1, r2 = random.random(), random.random()

        dim_velocity = self.inertia * part.velocity[dim] + \
            self.cognitive * r1 * (part.best_position[dim] - part.position[dim]) + \
            self.social * r2 * (self.position[dim] - part.position[dim])

        return self.handle_velocity(dim_velocity, -(n_len - 1), n_len)

    def __update_position(self, part, dim):
        dim_position = int(part.position[dim] + part.velocity[dim])

        return self.handle_position(dim_position, 0, len(self.scenario.nodes))

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

        best_particle = min(self.particles, key = lambda p: p.best_cost)

        if best_particle.best_cost < self.cost:
            self.position = best_particle.best_position[:]
            self.cost = best_particle.best_cost

        if self.position is None:
            logging.info('No viable solutions were generated on init')
            self.position = random.choice(particle.position
                                          for particle in self.particles)[:]

    @staticmethod
    def none_handle(value, mn, mx):
        return value

    @staticmethod
    def boundary_handle(value, mn, mx):
        if value < mn:
            return mn
        elif value >= mx:
            return mx - 1
        return value

    @staticmethod
    def periodic_handle(value, mn, mx):
        if value >= mx:
            return value % mx
        elif value < mn:
            return value % mx if mn >= 0 else (value % mx) - mx
        return value

    @staticmethod
    def random_handle(value, mn, mx):
        return value if mn <= value < mx else random.randrange(mn, mx)


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
