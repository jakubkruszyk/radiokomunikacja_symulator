import math
import numpy as np
from globals import FLOAT_COMP, FLOAT_ZERO


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
    a = (y2 - y1)
    b = -(x2 - x1)
    c = -a*x1 - b*y1
    return a, b, c


def abc_normalized(x1: int,
                   y1: int,
                   x2: int,
                   y2: int) -> tuple[float, float, float]:
    """
    Returns a,b and c coefficients of walls in general form: ax + by + c = 0 calculated from two points.
    Coefficients are normalized.

    Args:
        x1(int): x-coordinate of first point.
        y1(int): y-coordinate of first point.
        x2(int): x-coordinate of second point.
        y2(int): y-coordinate of second point.

    Returns:
        tuple[float, float, float]
    """
    a = (y2 - y1)
    b = -(x2 - x1)
    c = -a*x1 - b*y1
    m = math.sqrt(a*a + b*b)
    a = a / m
    b = b / m
    c = c / m
    return a, b, c


def intersection(line1: tuple[int, int, int, int],
                 line2: tuple[int, int, int, int]) -> tuple[float, float]:
    """
    Returns x and y coordinates of intersection of two lines.
    intersection2 is more efficient.

    Args:
        line1: tuple of x1, y1, x2 and y2 coordinates of first line
        line2: tuple of x1, y1, x2 and y2 coordinates of second line

    Returns:
        tuple[float, float]
    """
    a1, b1, c1 = abc(*line1)
    a2, b2, c2 = abc(*line2)

    x = (b1 * c2 - b2 * c1) / (a1 * b2 - a2 * b1)
    y = (c1 * a2 - c2 * a1) / (a1 * b2 - a2 - b1)

    return x, y


def intersection2(line1: tuple[float, float, float, float],
                  line2: tuple[float, float, float, float]) -> tuple[float, float] | None:
    """
        Returns x and y coordinates of intersection of two lines.

        Args:
            line1: tuple of x1, y1, x2 and y2 coordinates of first line
            line2: tuple of x1, y1, x2 and y2 coordinates of second line

        Returns:
            tuple[float, float] or None when lines are parallel
        """
    x1, y1, x2, y2 = line1
    x3, y3, x4, y4 = line2
    # formulas from https://en.wikipedia.org/wiki/Line%E2%80%93line_intersection#Given_two_points_on_each_line
    denominator = ((x1-x2)*(y3-y4) - (y1-y2)*(x3-x4))
    if abs(denominator) < FLOAT_ZERO:
        return None

    px = ((x1*y2-y1*x2)*(x3-x4) - (x1-x2)*(x3*y4-y3*x4)) / denominator
    py = ((x1*y2 - y1*x2)*(y3-y4) - (y1-y2)*(x3*y4-y3*x4)) / denominator
    return px, py


def point_line_distance(point: tuple[float, float],
                        line: tuple[float, float, float, float]) -> float:
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
            line: tuple containing two points that form a line (x1, y1, x2, y2) that point will be compared to.
            point: Point in space that will be compared to Wall

        Returns:
            True when point is on wall, else False
        """
    # uses comparisons between distances from point to endpoints and between endpoints
    # https://stackoverflow.com/questions/17692922/check-is-a-point-x-y-is-between-two-points-drawn-on-a-straight-line
    endpoint1_dist = point_point_distance(line[0:2], point)
    endpoint2_dist = point_point_distance(line[2:], point)
    line_dist = point_point_distance(line[0:2], line[2:])
    diff = line_dist - (endpoint1_dist + endpoint2_dist)
    return abs(diff) <= FLOAT_COMP


def point_mirror_line(line: tuple[float, float, float, float],
                      point: tuple[float, float]) -> tuple[float, float]:
    """
    Function that mirrors given point along given line.

    Args:
         line: tuple containing two points that form a line (x1, y1, x2, y2).
         point: tuple with coordinates of point to be mirrored.

    Returns:
        tuple with coordinates of mirrored point.
    """
    a, b, c = abc_normalized(*line)
    d = a*point[0] + b*point[1] + c
    px_mirror = point[0] - 2*a*d
    py_mirror = point[1] - 2*b*d
    return px_mirror, py_mirror


def distance_spaces(start: tuple[float, float],
                    end: tuple[float, float],
                    steps: int) -> (tuple[float], tuple[float], tuple[float]):
    """
    Function that returns evenly spaced arrays of x, y coordinates and total distance between start point and end point.

    Args:
        start: (x, y) coordinates of start-point
        end: (x, y) coordinates of end-point
        steps: number of desired segments

    Returns:
        x_axis, y_axis, distance arrays
    """
    xp = (start[0], end[0])
    fp = (start[1], end[1])
    dist_space = np.linspace(0, point_point_distance(start, end), steps)

    if abs(end[0] - start[0]) > abs(end[1] - start[1]):
        x_space = np.linspace(start[0], end[0], steps)
        y_space = np.interp(x_space, xp, fp)

    else:
        y_space = np.linspace(start[1], end[1], steps)
        x_space = np.interp(y_space, fp, xp)

    return x_space, y_space, dist_space
