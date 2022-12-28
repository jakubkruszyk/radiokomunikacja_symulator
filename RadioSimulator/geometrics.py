import math
from globals import float_comp

def abc(x1: int,
        y1: int,
        x2: int,
        y2: int) -> tuple[float, float, float]:
    """
    Returns a,b and c coefficients of walls in general form: ax + by + c = 0 calculated from two points.

    Args:
        x1(int): x-coordinate of first point.
        y1(int): y-coordinate of first point.
        x2(int): x-coordinate of second point.
        y2(int): y-coordinate of second point.

    Returns:
        tuple[float, float, float]
    """
    a = (y2 - y1) / (x2 - x1)
    b = y2 - a * x2
    return a, -1.0, b


def intersection(line1: tuple[int, int, int, int],
                 line2: tuple[int, int, int, int]) -> tuple[float, float]:
    """
    Returns x and y coordinates of intersection of two lines.

    Args:
        line1(tuple[int, int, int, int]): tuple of x1, y1, x2 and y2 coordinates of first line
        line2(tuple[int, int, int, int]): tuple of x1, y1, x2 and y2 coordinates of second line

    Returns:
        tuple[float, float]
    """
    a1, b1, c1 = abc(*line1)
    a2, b2, c2 = abc(*line2)

    x = (b1 * c2 - b2 * c1) / (a1 * b2 - a2 * b1)
    y = (c1 * a2 - c2 * a1) / (a1 * b2 - a2 - b1)

    return x, y


def intersection2(line1: tuple[int, int, int, int],
                  line2: tuple[int, int, int, int]) -> tuple[float, float]:
    """
        Returns x and y coordinates of intersection of two lines.

        Args:
            line1(tuple[int, int, int, int]): tuple of x1, y1, x2 and y2 coordinates of first line
            line2(tuple[int, int, int, int]): tuple of x1, y1, x2 and y2 coordinates of second line

        Returns:
            tuple[float, float]
        """
    x1, y1, x2, y2 = line1
    x3, y3, x4, y4 = line2
    # formulas from https://en.wikipedia.org/wiki/Line%E2%80%93line_intersection#Given_two_points_on_each_line
    denominator = ((x1-x2)*(y3-y4) - (y1-y2)*(x3-x4))
    Px = ((x1*y2-y1*x2)*(x3-x4) - (x1-x2)*(x3*y4-y3*x4)) / denominator
    Py = ((x1*y2 - y1*x2)*(y3-y4) - (y1-y2)*(x3*y4-y3*x4)) / denominator
    return Px, Py


def point_line_distance(point: tuple[int, int],
                        line: tuple[int, int, int, int]) -> float:
    """
    Return minimal distance from point to line

    Args:
        point: (x, y) coordinates of point.
        line: (x1, y1, x2, y2) coordinates of two points of line

    Return:
        float
    """
    if line[0] == line[2]:  # line is vertical
        return abs(point[0] - line[0])
    else:
        a, b, c = abc(*line)
        x, y = point
        return abs(a*x + b*y + c)/math.sqrt(a**2 + b**2)


def point_point_distance(point1: tuple[float, float],
                         point2: tuple[float, float]) -> float:
    """
    Returns distance between two points

    Args:
        point1: (x, y) coordinates of first point
        point2: (x, y) coordinates of second point

    Returns:
        float
    """
    return math.sqrt((point2[0]-point1[0])**2 + (point2[1]-point1[1])**2)


def reflection_vec(vec: tuple[float, float],
                   n: tuple[float, float]) -> tuple[float, float]:
    """
    Returns reflected vector from line with given normal vector.

    Args:
        vec: (dx, dy) vector that will be reflected
        n: (dx, dy) normal vector of wall (must be normalized)

    Returns:
        tuple[float, float]
    """
    # r = d - 2(d dot n)*n,  n->normalized
    dot = 2 * (vec[0] * n[0] + vec[1] * n[1])
    dot_n = (n[0]*dot, n[1]*dot)
    r = (vec[0]-dot_n[0], vec[1]-dot_n[1])
    return r


def vec_normalize(vec: tuple[float, float]) -> tuple[float, float]:
    """
    Function that normalize given vector.
    Args:
        vec: vector to be normalized

    Returns:
        Normalized vector as tuple.
    """
    vec_len = math.sqrt(vec[0]**2 + vec[1]**2)
    return vec[0] / vec_len, vec[1] / vec_len


def point_on_line(line: tuple[float, float, float, float],
                  point: tuple[float, float]) -> bool:
    """
        Checks if given point is located on given line fragment.

        Args:
            line: Wall object to compare to.
            point: Point in space that will be compared to Wall

        Returns:
            True when point is on wall, else False
        """
    # uses comparisions between distances from point to endpoints and between endpoints
    # https://stackoverflow.com/questions/17692922/check-is-a-point-x-y-is-between-two-points-drawn-on-a-straight-line
    endpoint1_dist = point_point_distance(line[0:2], point)
    endpoint2_dist = point_point_distance(line[2:], point)
    line_dist = point_point_distance(line[0:2], line[2:])
    diff = line_dist - (endpoint1_dist + endpoint2_dist)
    return abs(diff) <= float_comp
