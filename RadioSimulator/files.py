import json


def save_scene(walls):
    walls_list = list()
    materials_list = dict()
    for wall in walls:
        wall_dict = {
            "points": wall.points,
            "width": wall.width,
            "material": wall.material.name
        }
        if not materials_list.get(wall.material.name):
            materials_list[wall.material.name] = wall.material

        walls_list.append(wall_dict)

    combined_list = {
        "Materials": materials_list,
        "Walls": walls_list
    }
    print(json.dumps(combined_list, indent=4))
