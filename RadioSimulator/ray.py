from props import Transmitter, Wall
from geometrics import intersection2, reflection_vec, point_point_distance, vec_normalize, point_on_line
from globals import SCENE_SIZE


class Ray:
    """
    Class that represents single RF ray. It contains reference to its transmitter and vector of initial direction
    of propagation from transmitter.
    """
    def __init__(self,
                 transmitter: Transmitter,
                 vec: tuple[float, float],
                 ap: int = 1):
        self.transmitter = transmitter
        self.vec = vec_normalize(vec)
        self.ap = ap
        self.reflections_list = list()

    def propagate(self, walls: list[Wall]):
        """
        Calculates path that ray will take with given AP value. Saves all reflection points in reflections_list.
        No power values are calculated.

        Args:
            walls: list of walls on which ray can be reflected.
        """
        point1 = self.transmitter.point
        point2 = (point1[0]+self.vec[0], point1[1]+self.vec[1])
        # copy for restoration after calculations
        initial_ap = self.ap
        initial_vec = self.vec

        while self.ap > 0:
            intersections = list()
            for wall in walls:
                wall_dx = wall.points[0] - wall.points[2]
                wall_dy = wall.points[1] - wall.points[3]
                # check for parallel lines
                if wall_dx == self.vec[0] and wall_dy == self.vec[1]:
                    continue
                # calculate intersection and check if result is placed on wall
                intersection = intersection2((*point1, *point2), wall.points)
                if check_on_wall(wall, intersection):
                    intersections.append((intersection, wall))

            # check if points are in desired direction
            intersections = [i for i in intersections if check_direction(self.vec, point1, i[0])]

            if intersections:
                self.ap -= 1
                # sort results and add closest from last reflection point to reflections_list
                if len(intersections) > 1:
                    # avoid unnecesary sorting
                    sorted(intersections, key=lambda i: point_point_distance(point1, i[0]))
                self.reflections_list.append(intersections[0])

                # calculate new ray vector and update point1 & point2
                self.vec = reflection_vec(self.vec, intersections[0][1].normal)
                point1 = intersections[0][0]
                point2 = (point1[0] + self.vec[0], point1[1] + self.vec[1])

            # no wall found for reflection. End ray on scene boundary.
            else:
                boundaries = [(0, 0, SCENE_SIZE[0], 0),
                              (0, 0, 0, SCENE_SIZE[1]),
                              (SCENE_SIZE[0], 0, SCENE_SIZE[0], SCENE_SIZE[1]),
                              (0, SCENE_SIZE[1], SCENE_SIZE[0], SCENE_SIZE[1])]
                for edge in boundaries:
                    wall_dx = edge[0] - edge[2]
                    wall_dy = edge[1] - edge[3]
                    # check for parallel lines
                    if wall_dx == self.vec[0] and wall_dy == self.vec[1]:
                        continue
                    # calculate intersection and check if result is placed on wall
                    intersection = intersection2((*point1, *point2), edge)
                    if point_on_line(edge, intersection):
                        intersections.append((intersection, None))
                # there should be only one result
                intersections = [i for i in intersections if check_direction(self.vec, point1, i[0])]
                self.reflections_list.append(intersections[0])
                break

        # restore initial parameters
        self.ap = initial_ap
        self.vec = initial_vec


# ======================================================================================================================
# Helper functions
# ======================================================================================================================
def check_on_wall(wall: Wall,
                  point: tuple[float, float]) -> bool:
    """
    Checks if given point is located on given wall. It's just a wrapper for point_on_line function.

    Args:
        wall: Wall object to compare to.
        point: Point in space that will be compared to Wall

    Returns:
        True when point is on wall, else False
    """

    return point_on_line(wall.points, point)


def check_direction(vec: tuple[float, float],
                    last_point: tuple[float, float],
                    new_point: tuple[float, float]) -> bool:
    """
    Simple function that checks if new point lies in correct direction based on given vector.

    Args:
        vec: vector that specifies direction where new point should be.
        last_point: previous point used to form line with new_point
        new_point: point to be checked

    Returns:
        True if new point is placed in correct direction else False
    """
    return ((vec[0] > 0 and new_point[0] > last_point[0] or
             vec[0] < 0 and new_point[0] < last_point[0] or
             vec[0] == 0 and new_point[0] == last_point[0]) and
            (vec[1] > 0 and new_point[1] > last_point[1] or
             vec[1] < 0 and new_point[1] < last_point[1] or
             vec[1] == 0 and new_point[1] == last_point[1]))
