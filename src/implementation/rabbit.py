from enum import Enum
from typing import List

import numpy as np
from mesa import Agent

from implementation.abstract_model import AbstractAustralianRabbits
from implementation.virus import DeadlyRabbitVirus


class RabbitSex(Enum):
    MALE = 0,
    FEMALE = 1


class Rabbit(Agent):
    model: AbstractAustralianRabbits

    def __init__(
            self,
            unique_id: int,
            model: AbstractAustralianRabbits,
            pos: np.array,
            speed: int,
            velocity: np.array,
            reproduction_distance: int,
            reproduction_chance: float,
            immunity_chance: float
    ):
        super().__init__(unique_id, model)

        self.pos = np.array(pos)
        self.speed = speed
        self.velocity = velocity
        self.sex = np.random.choice((RabbitSex.MALE, RabbitSex.FEMALE))
        self.reproduction_distance = reproduction_distance
        self.reproduction_chance = reproduction_chance
        self.immunity_chance = immunity_chance

        self.is_fertile = False
        self.is_pregnant = 0
        self.age = 0
        self.energy = np.random.randint(60, 80 + 1)

        # noinspection PyTypeChecker
        self.virus: DeadlyRabbitVirus = None
        self.immunity_genetic_code = np.zeros(DeadlyRabbitVirus.GENETIC_CODE_LENGTH)

    def __hash__(self) -> int:
        return self.unique_id

    def step(self):
        self.age += 1
        self.energy -= 1

        if self.try_to_die():
            return

        if not self.is_fertile and self.age > 20:
            self.is_fertile = True

        if self.is_pregnant:
            self.is_pregnant -= 1
            self.give_birth()
        else:
            self.try_to_reproduce()

        if self.virus is not None:

            self.try_to_gain_immunity()
            self.virus.age += 1
            if self.is_immune():
                self.virus.try_to_mutate()
            self.transmit_virus()

        self.move()

    def move(self):
        if np.random.random() <= 0.05:
            self.velocity = np.random.uniform(-1, 1, 2)
            self.speed = np.random.randint(4, 6 + 1)

        new_pos = self.pos + self.velocity * self.speed
        self.model.space.move_agent(self, new_pos)

    def try_to_reproduce(self):
        if self.sex != RabbitSex.FEMALE or not self.is_fertile or self.is_pregnant:
            return

        if np.random.random() > self.reproduction_chance:
            return

        # noinspection PyTypeChecker
        reproduction_neighbors: List[Rabbit] = self.model.space.get_neighbors(self.pos, self.reproduction_distance,
                                                                              include_center=False)
        reproduction_neighbors = list(n for n in reproduction_neighbors if n.sex == RabbitSex.MALE and n.is_fertile)
        if not reproduction_neighbors:
            return

        first_male = reproduction_neighbors[0]
        first_male.energy -= 10

        self.is_pregnant = 10
        self.energy -= 10

    def give_birth(self):
        for _ in range(np.random.randint(2, 5 + 1)):
            offspring = Rabbit(
                unique_id=self.model.get_new_id(),
                model=self.model,
                pos=self.pos,
                speed=np.random.randint(4, 6 + 1),
                velocity=np.random.uniform(-1, 1, 2),
                reproduction_distance=self.reproduction_distance,
                reproduction_chance=self.reproduction_chance,
                immunity_chance=self.immunity_chance
            )
            offspring.immunity_genetic_code = self.immunity_genetic_code

            if self.virus is not None and self.virus.transmit_to_offspring:
                offspring.virus = self.virus.clone()

            self.model.add_agent(offspring)

    def transmit_virus(self):
        # noinspection PyTypeChecker
        transmission_neighbors: List[Rabbit] = self.model.space.get_neighbors(self.pos,
                                                                              self.virus.transmission_distance,
                                                                              include_center=False)

        transmission_neighbors = list(n for n in transmission_neighbors if n.virus is None or n.virus != self.virus)

        for neighbor in transmission_neighbors:
            if np.random.random() > self.virus.transmission_chance:
                continue

            neighbor.virus = self.virus.clone()

    def try_to_gain_immunity(self):
        if np.random.random() > self.immunity_chance:
            return

        self.immunity_genetic_code = self.virus.genetic_code

    def try_to_die(self) -> bool:
        can_die = self.energy <= 0 \
                  or (self.virus is not None and not self.is_immune() and self.virus.kill_host())

        if can_die:
            self.model.remove_agent(self)
            return True
        else:
            return False

    def is_immune(self):
        if self.virus is None:
            return None

        return np.alltrue(self.virus.genetic_code == self.immunity_genetic_code)

    def can_reproduce(self):
        return self.sex == RabbitSex.FEMALE and self.is_fertile and not self.is_pregnant
