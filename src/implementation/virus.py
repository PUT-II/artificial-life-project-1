import numpy as np


class DeadlyRabbitVirus:
    GENETIC_CODE_LENGTH = 32

    def __init__(
            self,
            death_chance: float,
            transmission_chance: float,
            transmission_distance: int,
            incubation_period: int,
            mutation_chance: float,
            transmit_to_offspring: bool
    ):
        self.death_chance = death_chance
        self.transmission_chance = transmission_chance
        self.transmission_distance = transmission_distance
        self.incubation_period = incubation_period
        self.mutation_chance = mutation_chance
        self.transmit_to_offspring = transmit_to_offspring

        self.age = 0

        self.genetic_code = np.random.randint(0, 1 + 1, self.GENETIC_CODE_LENGTH)

    def kill_host(self) -> bool:
        if self.age < self.incubation_period:
            return False

        return np.random.random() <= self.death_chance

    def try_to_mutate(self):
        if np.random.random() > self.mutation_chance:
            return

        mutation_size = np.random.randint(1, 3 + 1)
        mutation_start = np.random.randint(0, self.GENETIC_CODE_LENGTH)
        if mutation_start + mutation_size >= self.GENETIC_CODE_LENGTH:
            offset = mutation_start + mutation_size - self.GENETIC_CODE_LENGTH
            mutation_start -= offset

        for i in range(mutation_start, mutation_size):
            self.genetic_code[i] = np.bitwise_not(self.genetic_code[i])

    def clone(self):
        virus_clone = DeadlyRabbitVirus(self.death_chance, self.transmission_chance, self.transmission_distance,
                                        self.incubation_period, self.mutation_chance, self.transmit_to_offspring)
        virus_clone.genetic_code = self.genetic_code
        return virus_clone

    def __eq__(self, other):
        return np.alltrue(self.genetic_code == other.genetic_code)
