from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import UserSettableParameter
from mesa.visualization.modules import ChartModule, TextElement

from implementation.SimpleContinuousModule import SimpleCanvas
from implementation.model import AustralianRabbits
from implementation.rabbit import Rabbit, RabbitSex


def rabbit_draw(agent: Rabbit):
    if agent.sex == RabbitSex.MALE:
        portrayal = {"Shape": "rect", "w": 0.02, "h": 0.02, "Filled": "true", "Color": "Blue"}

        if not agent.is_fertile:
            portrayal["Color"] = "SteelBlue"
            portrayal["w"] = 0.01
            portrayal["h"] = 0.01

    elif agent.sex == RabbitSex.MALE.FEMALE:
        portrayal = {"Shape": "circle", "r": 3, "Filled": "true", "Color": "Red"}

        if not agent.is_fertile:
            portrayal["Color"] = "Orange"
            portrayal["r"] = 2

    else:
        raise RuntimeError(f"{agent.sex} rabbit sex not supported")

    if agent.virus is not None and not agent.is_immune():
        portrayal["Color"] = "Black"

    return portrayal


class PopulationElement(TextElement):
    def render(self, model: AustralianRabbits):
        return "Population: " + str(model.population_size)


class DiseasedElement(TextElement):
    def render(self, model: AustralianRabbits):
        return "Diseased: " + str(model.diseased_count)


population_chart = ChartModule([
    {"Label": "males", "Color": "blue"},
    {"Label": "females", "Color": "red"}
])

diseased_chart = ChartModule([
    {"Label": "population", "Color": "green"},
    {"Label": "diseased", "Color": "black"},
    {"Label": "immune", "Color": "gray"}
])

rabbits_canvas = SimpleCanvas(rabbit_draw, 500, 500)
model_params = {
    "starting_population": UserSettableParameter("slider", "Population", 100, 10, 100),
    "starting_diseased": UserSettableParameter("slider", "Diseased", 20, 1, 100),
    "reproduction_distance": 10,
    "reproduction_chance": UserSettableParameter("slider", "Reproduction chance", 0.25, 0.0, 1.0, 0.05),
    "transmit_to_offspring": UserSettableParameter("checkbox", "Transmit to offspring", True),
    "virus_death_chance": UserSettableParameter("slider", "Virus death chance", 0.5, 0.0, 1.0, 0.05),
    "transmission_chance": UserSettableParameter("slider", "Transmission chance", 1.0, 0.0, 1.0, 0.05),
    "transmission_distance": UserSettableParameter("slider", "Transmission distance", 10, 5, 30),
    "mutation_chance": UserSettableParameter("slider", "Mutation chance", 0.1, 0.0, 0.5, 0.05),
    "immunity_chance": UserSettableParameter("slider", "Immunity chance", 0.01, 0.0, 0.2, 0.001),
    "incubation_period": UserSettableParameter("slider", "Incubation period", 20, 2, 50),
}

elements = [rabbits_canvas, PopulationElement(), DiseasedElement(), population_chart, diseased_chart]
server = ModularServer(AustralianRabbits, elements, "Australian Rabbits", model_params)
