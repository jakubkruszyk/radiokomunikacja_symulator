import math
import cmath

from props import Transmitter, Wall
from geometrics import intersection2, reflection_vec, point_point_distance, vec_normalize, point_on_line, \
                       point_mirror_line
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
        self.forced_reflection_walls = list()
        self.graph_ids = list()

    def propagate(self, walls: list[Wall]):
        """
        Calculates path that ray will take with given AP value. Saves all reflection points in reflections_list.
        No power values are calculated.

        Args:
            walls: list of walls on which ray can be reflected.
        """
        # points that defines ray's line
        point1 = self.transmitter.point
        point2 = (point1[0]+self.vec[0], point1[1]+self.vec[1])
        # copy for restoration after calculations
        initial_ap = self.ap
        initial_vec = self.vec

        while self.ap > 0:
            intersections = list()
            for wall in walls:
                # wall's line direction vector
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
                    intersections = sorted(intersections, key=lambda i: point_point_distance(point1, i[0]))
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

    def propagate_to_point(self, endpoint: tuple[float, float],
                           walls: list[Wall] = ()):
        """
        Method that will try to propagate ray from its transmitter to endpoint. If walls parameter is provided ray will
        be forced to reflect of each of wall in list in order.

        Args:
            endpoint: point to where ray should get
            walls: list of Wall objects

        """
        if not walls:
            self.reflections_list = [(endpoint, None)]
            return

        points = [endpoint]
        # create list of mirrored point starting from endpoint towards transmitter
        for wall in walls[::-1]:
            points.append(point_mirror_line(wall.points, points[-1]))

        # calculate first reflection point from transmitter
        points = points[::-1]
        reflections = [self.transmitter.point]
        for point, wall in zip(points, walls):
            new_point = intersection2(wall.points, (*point, *reflections[-1]))
            if not check_on_wall(wall, new_point):
                return
            reflections.append(new_point)

        self.reflections_list = [(p, w) for p, w in zip(reflections[1:], walls)]
        self.reflections_list.append((endpoint, None))

    def get_dist_coef(self, dist: float) -> tuple[complex, bool]:
        """
        Method that returns distance coefficient of ray. Propagate method must be called beforehand.
        Multiply module squared of this coefficient times reference power gives actual power value.

        Args:
            dist: distance from transmitter where power will be calculated.

        Returns:
            Distance coefficient as complex number in and status flag. If given distance is larger than calculated path
            of ray, flag will be False.
        """
        # check if ray has propagation list filled
        if not self.reflections_list:
            return 0, False

        # check where on propagation path given distance is
        alpha = 1
        dist_sum = point_point_distance(self.transmitter.point, self.reflections_list[0][0])
        ref_idx = 0
        while dist > dist_sum:
            ref_idx += 1
            if ref_idx > len(self.reflections_list)-1:
                # given distance is outside calculated path
                return 0, False

            dist_sum += point_point_distance(self.reflections_list[ref_idx-1][0], self.reflections_list[ref_idx][0])
            alpha *= self.reflections_list[ref_idx-1][1].material.alpha

        path = alpha/dist * cmath.exp(-2j*math.pi*self.transmitter.freq*dist/3e8)
        return path, True

    def get_dist_coef_array(self, step: float) -> list[complex]:
        """
            Method that returns array of distance coefficients of ray. Array covers distance from start
            to end of the ray with 'step' change in distance. Propagate method must be called beforehand else empty list
            will be returned.
            Multiply module squared of this coefficient times reference power gives actual power value.

           Args:
               step: distance from transmitter where power will be calculated.

           Returns:
               Array of distance coefficients as complex numbers.
       """
        # check if ray has propagation list filled
        if not self.reflections_list:
            return list()

        alpha = 1
        dist_sum = step
        dist_threshold = point_point_distance(self.transmitter.point, self.reflections_list[0][0])
        ref_idx = 0
        dist_coefs = [1]
        while True:
            if dist_sum > dist_threshold:
                ref_idx += 1
                if ref_idx >= len(self.reflections_list):
                    break
                else:
                    dist_threshold += point_point_distance(self.reflections_list[ref_idx - 1][0],
                                                           self.reflections_list[ref_idx][0])
                    alpha *= self.reflections_list[ref_idx - 1][1].material.alpha

            # calculate coefficient
            coef = alpha / dist_sum * cmath.exp(-2j * math.pi * self.transmitter.freq * dist_sum / 3e8)
            dist_coefs.append(coef)
            dist_sum += step

        return dist_coefs

    def get_power_ref(self):
        """
        Method that calculates reference power level of ray's transmitter.
        It's basically Friis formula without distance. To get actual power level you need to divide by distance squared.
        For now antennas are treated as isotropic.

        Returns:
             Reference power level of ray's transmitter.
        """
        return self.transmitter.power * (self.transmitter.lam / (4 * math.pi)) ** 2

    def get_coef_at_end(self) -> complex | None:
        """
                Method that returns distance coefficient at the end of ray. Propagate method must be called beforehand.
                Multiply module squared of this coefficient times reference power gives actual power value.

                Returns:
                    Distance coefficient as complex number.
        """
        if not self.reflections_list:
            return None

        dist_sum = point_point_distance(self.transmitter.point, self.reflections_list[0][0])
        alpha = 1
        for i in range(1, len(self.reflections_list)):
            alpha *= self.reflections_list[i-1][1].material.alpha
            dist_sum += point_point_distance(self.reflections_list[i][0], self.reflections_list[i-1][0])

        return alpha/dist_sum * cmath.exp(-2j*math.pi*self.transmitter.freq*dist_sum/3e8)


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
