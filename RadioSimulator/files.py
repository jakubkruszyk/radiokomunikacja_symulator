import json
import PySimpleGUI as sg
import globals as gb
from props import Material, Wall, Transmitter, Receiver


def save_scene():
    """
    Function that stores parameters of scene from globals.py in json file. File location is chosen by popup.
    """
    walls_list = list()
    materials_list = list()
    transmitters_list = list()
    receivers_list = list()
    for wall in gb.walls:
        wall_dict = {
            "points": wall.points,
            "width": wall.width,
            "material": wall.material.name
        }
        if wall.material not in materials_list:
            materials_list.append(wall.material)

        walls_list.append(wall_dict)

    for transmitter in gb.transmitters:
        transmitter_dict = {
            "point": transmitter.point,
            "power": transmitter.power,
            "freq": transmitter.freq
        }
        transmitters_list.append(transmitter_dict)

    for receiver in gb.receivers:
        receiver_dict = {
            "point": receiver.point,
        }
        receivers_list.append(receiver_dict)

    combined_list = {
        "Scale": gb.SCALE,
        "Materials": materials_list,
        "Walls": walls_list,
        "Transmitters": transmitters_list,
        "Receivers": receivers_list
    }

    path = sg.popup_get_file("Choose file:", save_as=True, default_extension=".json")
    if path:
        with open(path, "w") as file:
            file.write(json.dumps(combined_list, indent=2))


def load_scene():
    """
        Function that loads parameters of Walls and Transmitters from json file and creates respective objects.
        File location is chosen by popup.
    """
    path = sg.popup_get_file("Choose file:")
    if not path:
        return

    with open(path) as file:
        file_content = json.load(file)
        # read scene SCALE
        new_scale = int(file_content["Scale"])
        sf = gb.SCALE/new_scale  # scaling factor for conversion from file scale to scene scale

        # read materials
        materials = tuple(Material(*m) for m in file_content["Materials"])

        # read walls
        walls = list()
        for wall in file_content['Walls']:
            point1 = (wall["points"][0]*sf, wall["points"][1]*sf)
            point2 = (wall["points"][2]*sf, wall["points"][3]*sf)
            line_id = gb.graph.draw_line(point1, point2, width=gb.WALL_WIDTH, color=gb.WALL_COLOR)
            material = [m for m in materials if m.name == wall["material"]][0]
            walls.append(Wall(point1, point2, line_id, material, wall["width"]))

        transmitters = list()
        for transmitter in file_content["Transmitters"]:
            point = (transmitter["point"][0]*sf, transmitter["point"][1]*sf)
            power = transmitter["power"]
            freq = transmitter["freq"]
            graph_id = gb.graph.draw_point(point, gb.TRANSMITTER_SIZE, color=gb.TRANSMITTER_COLOR)
            transmitters.append(Transmitter(point, graph_id, power, freq))

        receivers = list()
        for receiver in file_content["Receivers"]:
            point = (receiver["point"][0]*sf, receiver["point"][1]*sf)
            graph_id = gb.graph.draw_point(point, gb.RECEIVER_SIZE, color=gb.RECEIVER_COLOR)
            receivers.append(Receiver(point, graph_id))

        # update globals
        gb.walls = walls
        gb.transmitters = transmitters
        gb.receivers = receivers
