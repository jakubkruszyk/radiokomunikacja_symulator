import json
import globals as gb
from props import Material, Wall
# TODO popup with file path


def save_scene(walls):
    walls_list = list()
    materials_list = list()
    for wall in walls:
        wall_dict = {
            "points": wall.points,
            "width": wall.width,
            "material": wall.material.name
        }
        if wall.material not in materials_list:
            materials_list.append(wall.material)

        walls_list.append(wall_dict)

    combined_list = {
        "Scale": gb.scale,
        "Materials": materials_list,
        "Walls": walls_list
    }

    with open("scena.json", "w") as file:
        file.write(json.dumps(combined_list, indent=4))


def load_scene():
    with open("scena.json") as file:
        file_content = json.load(file)
        # read scene scale
        gb.scale = int(file_content["Scale"])

        # read materials
        materials = tuple(Material(*m) for m in file_content["Materials"])

        # read walls
        walls = []
        for wall in file_content['Walls']:
            point1 = wall["points"][0:2]
            point2 = wall["points"][2:]
            line_id = gb.graph.draw_line(point1, point2, width=gb.WALL_WIDTH, color=gb.WALL_COLOR)
            material = [m for m in materials if m.name == wall["material"]][0]
            walls.append(Wall(point1, point2, line_id, material, wall["width"]))

        # update globals
        gb.walls = walls
