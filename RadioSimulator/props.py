from collections import namedtuple
import math


Material = namedtuple("Material", ["name",
                                   "param1", "param2"])


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


class Transmitter:
    def __init__(self,
                 point: tuple[int, int],
                 graph_id: int,
                 power: float):
        self.point = point
        self.power = power
        self.graph_id = graph_id
