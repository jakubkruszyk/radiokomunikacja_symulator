from collections import namedtuple

Material = namedtuple("Material", ["name",
                                   "param1", "param2"])


class Wall:
    """
    Class representing simple 1 dimensional wall on 2D space. Thickness is not represented on screen but it can be
    simulated through properties of wall

    Args:
        point1(int, int): x and y coordinates of first point of wall.
        point2(int, int): x and y coordinates of second point of wall.
        line_id: id of line object in pysimplegui graph
        material(props.Material): Material object describing wall parameters
    """

    def __init__(self,
                 point1: tuple[int, int],
                 point2: tuple[int, int],
                 line_id,
                 material: Material,
                 width: float = 1):
        self.points = (*point1, *point2)
        self.material = material
        self.line_id = line_id
        self.width = width
