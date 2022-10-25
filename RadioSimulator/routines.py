import PySimpleGUI as sg
import globals as gb
import math
from props import Wall
from geometrics import point_line_distance
from files import save_scene, load_scene
from materials import materials_list


# ======================================================================================================================
# Draw scene mode
# ======================================================================================================================
def draw_wall(app, event, values):
    # coordinates after snapping - basic quantization based on SCENE_GRID size
    values_s = (gb.SCENE_GRID[0] * math.floor(values[event][0] / gb.SCENE_GRID[0] + 0.5),
                gb.SCENE_GRID[1] * math.floor(values[event][1] / gb.SCENE_GRID[1] + 0.5))

    if gb.last_click:
        # draw walls and add Wall objects to list
        line_id = gb.graph.draw_line(gb.last_click, values_s, width=gb.WALL_WIDTH, color=gb.WALL_COLOR)
        material = [m for m in materials_list if m.name == values["material_list"]][0]
        try:
            width = float(values["width"])
        except ValueError:
            sg.popup_error('Given width is not a number. Maybe you used "," instead of "."?  Used default value.')
            width = 1
        gb.walls.append(Wall(gb.last_click, values_s, line_id, material, width))
        gb.last_click = None
        app["x1"].update("")
        app["y1"].update("")
    else:
        gb.last_click = values_s
        app["x1"].update(values_s[0])
        app["y1"].update(values_s[1])


def edit_wall(app, event, values):
    # calculate distance from last click to all walls
    distances = [(point_line_distance(values[event], wall.points), wall) for wall in gb.walls]
    # filter results by size of wall + snapping offset
    snap_walls = [wall for wall in distances if wall[0] <= gb.WALL_WIDTH]
    if snap_walls:
        # sort by distance
        snap_walls = sorted(snap_walls, key=lambda x: x[0])
        gb.edit_wall = snap_walls[0][1]
        app["width"].update(gb.edit_wall.width)
        app["x1"].update(gb.edit_wall.points[0])
        app["y1"].update(gb.edit_wall.points[1])
        app["x2"].update(gb.edit_wall.points[2])
        app["y2"].update(gb.edit_wall.points[3])
        app["material_list"].update(value=gb.edit_wall.material.name)
        for name, value in zip(gb.edit_wall.material._fields, gb.edit_wall.material):
            if name != "name":
                app[f"property_{name}"].update(value)
    else:
        app["x1"].update("")
        app["y1"].update("")
        app["x2"].update("")
        app["y2"].update("")


def draw_scene_routine(app, event, values):
    if event == "graph":
        if gb.current_sub_mode == "draw":
            draw_wall(app, event, values)
        elif gb.current_sub_mode == "edit":
            edit_wall(app, event, values)

    elif event == "reset_scene":
        for line in gb.walls:
            gb.graph.delete_figure(line.line_id)
        gb.walls.clear()

    elif event == "draw":
        gb.current_sub_mode = "draw"
        app["draw"].update(button_color=gb.BUTTON_ACTIVE_COLOR)
        app["edit"].update(button_color=gb.BUTTON_INACTIVE_COLOR)
        app["update"].update(visible=False)
        app["x1"].update("")
        app["y1"].update("")
        app["x2"].update("")
        app["y2"].update("")

    elif event == "edit":
        gb.current_sub_mode = "edit"
        app["draw"].update(button_color=gb.BUTTON_INACTIVE_COLOR)
        app["edit"].update(button_color=gb.BUTTON_ACTIVE_COLOR)
        app["update"].update(visible=True)

    elif event == "material_list":
        material = [m for m in materials_list if m.name == values[event]][0]
        for name, value in zip(material._fields, material):
            if name != "name":
                app[f"property_{name}"].update(value)

    elif event == "update":
        points = (values["x1"], values["y1"], values["x2"], values["y2"])
        try:
            points = tuple(int(p) for p in points)
        except ValueError:
            sg.popup_error("Coordinates from inputs are not integers!")
            return
        gb.edit_wall.points = points
        material = [m for m in materials_list if m.name == values["material_list"]][0]
        gb.edit_wall.material = material
        gb.graph.delete_figure(gb.edit_wall.line_id)
        line_id = gb.graph.draw_line(points[0:2], points[2:], width=gb.WALL_WIDTH, color=gb.WALL_COLOR)
        gb.edit_wall.line_id = line_id

    elif event == "save":
        save_scene(gb.walls)

    elif event == "load":
        load_scene()
