from abc import ABC
from abc import abstractmethod

from mesa import Model
from mesa.space import ContinuousSpace


class AbstractAustralianRabbits(ABC, Model):
    space: ContinuousSpace

    @abstractmethod
    def get_new_id(self) -> int:
        pass

    @abstractmethod
    def add_agent(self, agent) -> None:
        pass

    @abstractmethod
    def remove_agent(self, agent) -> None:
        pass
