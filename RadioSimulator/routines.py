import PySimpleGUI as sg
import globals as gb
import math
from props import Wall, Transmitter
from geometrics import point_line_distance, point_point_distance
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


def draw_transmitter(event, values):
    values_s = (gb.SCENE_GRID[0] * math.floor(values[event][0] / gb.SCENE_GRID[0] + 0.5),
                gb.SCENE_GRID[1] * math.floor(values[event][1] / gb.SCENE_GRID[1] + 0.5))

    circle_id = gb.graph.draw_point(values_s, gb.TRANSMITTER_SIZE, color=gb.TRANSMITTER_COLOR)
    try:
        power = float(values["power"])
    except ValueError:
        power = 1
    gb.transmitters.append(Transmitter(values_s, circle_id, power))


def clear_displayed_points(app):
    app["x1"].update("")
    app["y1"].update("")
    app["x2"].update("")
    app["y2"].update("")


def show_line_layout(app):
    app["update"].update(visible=False)
    app["draw_line_layout"].update(visible=True)
    app["draw_transmitter_layout"].update(visible=False)
    clear_displayed_points(app)


def show_transmitter_layout(app):
    app["update"].update(visible=False)
    app["draw_line_layout"].update(visible=False)
    app["draw_transmitter_layout"].update(visible=True)
    clear_displayed_points(app)


def edit_wall(app, event, values):
    # calculate distance from last click to all walls
    distances = [(point_line_distance(values[event], wall.points), wall) for wall in gb.walls]
    # calculate distance from last click to all transmitters
    distances_t = [(point_point_distance(values[event], transmitter.point), transmitter) for transmitter in gb.transmitters]
    # filter results by size of wall/ transmitter
    snap_walls = [wall for wall in distances if wall[0] <= gb.WALL_WIDTH]
    snap_transmitters = [transmitter for transmitter in distances_t if transmitter[0] <= gb.TRANSMITTER_SIZE]
    snap_combined = snap_walls + snap_transmitters
    if snap_combined:
        # sort by distance
        snap_combined = sorted(snap_combined, key=lambda x: x[0])
        gb.edit_prop = snap_combined[0][1]
        if type(gb.edit_prop) == Wall:
            show_line_layout(app)
            app["update"].update(visible=True)
            app["width"].update(gb.edit_prop.width)
            app["x1"].update(gb.edit_prop.points[0])
            app["y1"].update(gb.edit_prop.points[1])
            app["x2"].update(gb.edit_prop.points[2])
            app["y2"].update(gb.edit_prop.points[3])
            app["material_list"].update(value=gb.edit_prop.material.name)
            for name, value in zip(gb.edit_prop.material._fields, gb.edit_prop.material):
                if name != "name":
                    app[f"property_{name}"].update(value)
        elif type(gb.edit_prop) == Transmitter:
            show_transmitter_layout(app)
            app["update"].update(visible=True)
            app["x1"].update(gb.edit_prop.point[0])
            app["y1"].update(gb.edit_prop.point[1])
            app["power"].update(gb.edit_prop.power)

    else:
        clear_displayed_points(app)


def draw_scene_routine(app, event, values):
    if event == "graph":
        if gb.current_sub_mode == "draw_l":
            draw_wall(app, event, values)
        elif gb.current_sub_mode == "draw_t":
            draw_transmitter(event, values)
        elif gb.current_sub_mode == "edit":
            edit_wall(app, event, values)

    elif event == "reset_scene":
        for line in gb.walls:
            gb.graph.delete_figure(line.line_id)
        gb.walls.clear()

    elif event == "draw":
        gb.current_sub_mode = "draw_l"
        app["draw"].update(button_color=gb.BUTTON_ACTIVE_COLOR)
        app["edit"].update(button_color=gb.BUTTON_INACTIVE_COLOR)
        app["transmitter"].update(button_color=gb.BUTTON_INACTIVE_COLOR)
        show_line_layout(app)
    elif event == "transmitter":
        gb.current_sub_mode = "draw_t"
        app["draw"].update(button_color=gb.BUTTON_INACTIVE_COLOR)
        app["edit"].update(button_color=gb.BUTTON_INACTIVE_COLOR)
        app["transmitter"].update(button_color=gb.BUTTON_ACTIVE_COLOR)
        show_transmitter_layout(app)

    elif event == "edit":
        gb.current_sub_mode = "edit"
        app["draw"].update(button_color=gb.BUTTON_INACTIVE_COLOR)
        app["edit"].update(button_color=gb.BUTTON_ACTIVE_COLOR)
        app["transmitter"].update(button_color=gb.BUTTON_INACTIVE_COLOR)
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
        gb.edit_prop.points = points
        material = [m for m in materials_list if m.name == values["material_list"]][0]
        gb.edit_prop.material = material
        gb.graph.delete_figure(gb.edit_prop.line_id)
        line_id = gb.graph.draw_line(points[0:2], points[2:], width=gb.WALL_WIDTH, color=gb.WALL_COLOR)
        gb.edit_prop.line_id = line_id

    elif event == "save":
        save_scene(gb.walls)

    elif event == "load":
        load_scene()
