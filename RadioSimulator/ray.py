from props import Wall


class Ray:

    def __init__(self,
                 x: int,
                 y: int,
                 a: float):
        self.lines = list()
        self.x = x
        self.y = y
        self.a = a

    def calculate_reflection(self, walls: list[Wall]):
        pass
