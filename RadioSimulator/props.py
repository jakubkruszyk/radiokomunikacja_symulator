from collections import namedtuple
import math
from globals import USE_TM
from geometrics import vec_vec_angle

Material = namedtuple("Material", ["name",  # name of material
                                   "alpha",  # custom values of reflection coefficient
                                   "custom_alpha",  # flag if program should use alpha parameter (True, False)
                                   "eta"  # relative permitivity of material
                                   ])


class Wall:
    """
    Class representing simple 1 dimensional wall on 2D space. Thickness is not represented on screen, but it can be
    simulated through properties of wall

    Args:
        point1(int, int): x and y coordinates of first point of wall.
        point2(int, int): x and y coordinates of second point of wall.
        graph_id: id of line object in pysimplegui graph
        material(props.Material): Material object describing wall parameters
    """

    def __init__(self,
                 point1: tuple[int, int],
                 point2: tuple[int, int],
                 graph_id,
                 material: Material,
                 width: float = 1):
        self.points: tuple[int, int, int, int] = (*point1, *point2)
        self.material = material
        self.graph_id = graph_id
        self.width = width
        self.normal = self.calc_normal()

    def calc_normal(self) -> tuple[float, float]:
        """
        Method to calculate normal vector of wall. Since there are 2 of those vectors,
        one with negative value of dx is chosen.

        Return:
            Normal vector of given wall.
        """
        dx = self.points[0] - self.points[2]
        dy = self.points[1] - self.points[3]
        n = (-dy, dx)
        n_len = math.sqrt(n[0]**2 + n[1]**2)
        n = (n[0]/n_len, n[1]/n_len)  # normalize
        if n[0] > 0:
            n = (-n[0], -n[1])
        return n

    def reflection_coefficient(self,
                               vec: tuple[float, float]):
        """
        Calculates reflection coefficient for given vector of incidence

        """
        if self.material.custom_alpha:
            return self.material.alpha

        # because angle between vectors is angle when vectors are connected with tails and with ray reflection
        # ray vector is connected with normal vector head to tail we need to substract result from pi
        theta = math.pi - vec_vec_angle(vec, self.normal)

        if USE_TM:
            r = (self.material.eta * math.cos(theta) - math.sqrt(self.material.eta - math.sin(theta)**2)) \
                / (self.material.eta * math.cos(theta) + math.sqrt(self.material.eta - math.sin(theta)**2))

        else:
            r = (math.cos(theta) - math.sqrt(self.material.eta - math.sin(theta)**2)) \
                / (math.cos(theta) + math.sqrt(self.material.eta - math.sin(theta)**2))

        return r


class Transmitter:
    """
    Dataclass representing RF transmitter.
    Lambda is calculated based on given frequency.

    Args:
         point: (x, y) coordinates of transmitter(represented as point)
         graph_id: id of PySimpleGUI point on graph
         power: power value of transmitter in Watts
         freq: frequency of generated wave in Hertz
    """
    def __init__(self,
                 point: tuple[float, float],
                 graph_id: int,
                 power: float,
                 freq: float):
        self.point = point
        self.power = power
        self.graph_id = graph_id
        self.freq = freq
        self.lam = 3e8/freq


class Receiver:
    """
        Dataclass representing RF receiver.

        Args:
             point: (x, y) coordinates of receiver(represented as point)
             graph_id: id of PySimpleGUI point on graph
    """
    def __init__(self,
                 point: tuple[float, float],
                 graph_id: int):
        self.point = point
        self.graph_id = graph_id
