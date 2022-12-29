import json
import PySimpleGUI as sg
import globals as gb
from props import Material, Wall, Transmitter


def save_scene(walls: list[Wall],
               transmitters: list[Transmitter]):
    """
    Function that stores parameters of given Walls and Transmitters in json file. File location is chosen by popup.

    Args:
        walls: list of walls objects to be saved.
        transmitters: list of transmitters objects to be saved.
    """
    walls_list = list()
    materials_list = list()
    transmitters_list = list()
    for wall in walls:
        wall_dict = {
            "points": wall.points,
            "width": wall.width,
            "material": wall.material.name
        }
        if wall.material not in materials_list:
            materials_list.append(wall.material)

        walls_list.append(wall_dict)

    for transmitter in transmitters:
        transmitter_dict = {
            "point": transmitter.point,
            "power": transmitter.power
        }
        transmitters_list.append(transmitter_dict)

    combined_list = {
        "Scale": gb.SCALE,
        "Materials": materials_list,
        "Walls": walls_list,
        "Transmitters": transmitters_list
    }

    path = sg.popup_get_file("Choose file:", save_as=True)
    with open(path, "w") as file:
        file.write(json.dumps(combined_list, indent=2))


def load_scene():
    """
        Function that loads parameters of Walls and Transmitters from json file and creates respective objects.
        File location is chosen by popup.
    """
    path = sg.popup_get_file("Choose file:")
    with open(path) as file:
        file_content = json.load(file)
        # read scene SCALE
        gb.SCALE = int(file_content["Scale"])

        # read materials
        materials = tuple(Material(*m) for m in file_content["Materials"])

        # read walls
        walls = list()
        for wall in file_content['Walls']:
            point1 = wall["points"][0:2]
            point2 = wall["points"][2:]
            line_id = gb.graph.draw_line(point1, point2, width=gb.WALL_WIDTH, color=gb.WALL_COLOR)
            material = [m for m in materials if m.name == wall["material"]][0]
            walls.append(Wall(point1, point2, line_id, material, wall["width"]))

        transmitters = list()
        for transmitter in file_content["Transmitters"]:
            point = transmitter["point"]
            power = transmitter["power"]
            graph_id = gb.graph.draw_point(point, gb.TRANSMITTER_SIZE, color=gb.TRANSMITTER_COLOR)
            transmitters.append(Transmitter(point, graph_id, power))

        # update globals
        gb.walls = walls
        gb.transmitters = transmitters
