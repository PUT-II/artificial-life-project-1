from typing import Set

import numpy as np
from mesa.datacollection import DataCollector
from mesa.space import ContinuousSpace
from mesa.time import RandomActivation

from implementation.abstract_model import AbstractAustralianRabbits
from implementation.rabbit import Rabbit, RabbitSex
from implementation.virus import DeadlyRabbitVirus


class AustralianRabbits(AbstractAustralianRabbits):
    """
    Australian Rabbits model represents a scenario of eradicating rabbits with a weaponized virus.
    """

    POPULATION_LIMIT = 1000

    # noinspection PyMissingConstructor
    def __init__(
            self,
            starting_population: int,
            starting_diseased: int,
            reproduction_distance: int,
            reproduction_chance: float,
            transmit_to_offspring: bool,
            virus_death_chance: float,
            transmission_chance: float,
            transmission_distance: int,
            mutation_chance: float,
            immunity_chance: float,
            incubation_period: int,
            speed: int = 5
    ):
        self.male_count = 0
        self.female_count = 0
        self.population_size = 0
        self.diseased_count = 0
        self.immune_count = 0
        self.last_id: int = starting_population
        self.population: Set[Rabbit] = set()

        self.total_population = 0
        self.total_death_count = 0
        self.death_ratio = 0.0

        self.datacollector = DataCollector({
            "males": "male_count",
            "females": "female_count",
            "population": "population_size",
            "diseased": "diseased_count",
            "immune": "immune_count"
        })

        self.schedule = RandomActivation(self)
        self.space = ContinuousSpace(500, 500, True)

        virus_template = DeadlyRabbitVirus(virus_death_chance,
                                           transmission_chance,
                                           transmission_distance,
                                           incubation_period,
                                           mutation_chance,
                                           transmit_to_offspring)

        rabbit_template = Rabbit(
            unique_id=-1,
            model=self,
            pos=None,
            speed=speed,
            velocity=None,
            reproduction_distance=reproduction_distance,
            reproduction_chance=reproduction_chance,
            immunity_chance=immunity_chance
        )

        self.make_agents(starting_population, starting_diseased, rabbit_template, virus_template)

        self.running = True

    def make_agents(
            self,
            starting_population: int,
            diseased: int,
            rabbit_template: Rabbit,
            virus_template: DeadlyRabbitVirus
    ):
        for i in range(starting_population):
            x = self.random.random() * self.space.x_max
            y = self.random.random() * self.space.y_max
            pos = np.array((x, y))
            velocity = np.random.random(2) * 2 - 1

            rabbit = Rabbit(
                unique_id=i,
                model=rabbit_template.model,
                pos=pos,
                speed=rabbit_template.speed,
                velocity=velocity,
                reproduction_distance=rabbit_template.reproduction_distance,
                reproduction_chance=rabbit_template.reproduction_chance,
                immunity_chance=rabbit_template.immunity_chance
            )

            if diseased > 0:
                diseased -= 1
                rabbit.virus = virus_template.clone()

            self.add_agent(rabbit)

        self.__update_counters()
        self.datacollector.collect(self)

    def step(self):
        self.schedule.step()

        self.__update_counters()
        self.datacollector.collect(self)

        if self.population_size == 0 or self.female_count == 0 or self.male_count == 0:
            self.running = False
            return

        if self.diseased_count == 0:
            self.running = False
            return

        if all(a.is_immune() for a in self.population):
            self.running = False
            return

    def get_new_id(self) -> int:
        new_id = self.last_id
        self.last_id += 1
        return new_id

    def add_agent(self, agent: Rabbit):
        if len(self.population) >= self.POPULATION_LIMIT:
            return

        self.total_population += 1

        self.space.place_agent(agent, agent.pos)
        self.schedule.add(agent)
        self.population.add(agent)

    def remove_agent(self, agent: Rabbit, death_from_virus: bool = False) -> None:
        if death_from_virus:
            self.total_death_count += 1

        self.space.remove_agent(agent)
        self.schedule.remove(agent)
        self.population.remove(agent)

    def __update_counters(self):
        male_population = list(None for a in self.population if a.sex == RabbitSex.MALE)

        self.population_size = len(self.population)
        self.male_count = len(male_population)
        self.female_count = self.population_size - self.male_count
        self.diseased_count = len(list(None for agent in self.population if agent.virus))
        self.immune_count = len(list(None for agent in self.population if agent.is_immune()))
        self.death_ratio = self.total_death_count / self.total_population
