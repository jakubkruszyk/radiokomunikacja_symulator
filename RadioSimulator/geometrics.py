import math


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
    Returns x and y coordinates of intersection of two walls and angle between them.

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


def point_point_distance(point1: tuple[int, int],
                         point2: tuple[int, int]) -> float:
    """
    Returns distance between two points

    Args:
        point1: (x, y) coordinates of first point
        point2: (x, y) coordinates of second point

    Returns:
        float
    """
    return math.sqrt((point2[0]-point1[0])**2 + (point2[1]-point1[1])**2)
