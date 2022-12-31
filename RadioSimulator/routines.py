import PySimpleGUI as sg
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import globals as gb
import math

from RadioSimulator.props import Material
from props import Wall, Transmitter
from ray import Ray
from files import save_scene, load_scene
from materials import materials_list


# ======================================================================================================================
# Draw scene mode
# ======================================================================================================================
def point_quantization(point: tuple[int, int]):
    return (gb.SCENE_GRID[0] * math.floor(point[0] / gb.SCENE_GRID[0] + 0.5),
            gb.SCENE_GRID[1] * math.floor(point[1] / gb.SCENE_GRID[1] + 0.5))


def draw_wall(app, event, values):
    # coordinates after snapping - basic quantization based on SCENE_GRID size
    values_s = point_quantization(values[event])

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
    values_s = point_quantization(values[event])

    circle_id = gb.graph.draw_point(values_s, gb.TRANSMITTER_SIZE, color=gb.TRANSMITTER_COLOR)
    try:
        power = float(values["power"])
    except ValueError:
        power = 1

    try:
        freq = float(values["freq"])
    except ValueError:
        freq = 1e6
    gb.transmitters.append(Transmitter(values_s, circle_id, power, freq))


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
    # get ids of objects that user clicked on
    objects = gb.graph.get_figures_at_location(values[event])
    # check walls, transmitter lists for matching ids
    filtered = [o for o in (*gb.walls, *gb.transmitters) if o.graph_id in objects]
    if filtered:
        gb.edit_prop = filtered[0]
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
            app["freq"].update(gb.edit_prop.freq)

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
            gb.graph.delete_figure(line.graph_id)
        gb.walls.clear()
        for transmitter in gb.transmitters:
            gb.graph.delete_figure(transmitter.graph_id)
        gb.transmitters.clear()

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
        material: Material = [m for m in materials_list if m.name == values[event]][0]
        for name, value in zip(material._fields, material):
            if name != "name":
                app[f"property_{name}"].update(value)

    elif event == "update":
        if type(gb.edit_prop) == Wall:
            points = (values["x1"], values["y1"], values["x2"], values["y2"])
            try:
                points = tuple(int(p) for p in points)
            except ValueError:
                sg.popup_error("Coordinates from inputs are not integers!")
                return
            gb.edit_prop.points = points
            material = [m for m in materials_list if m.name == values["material_list"]][0]
            try:
                width = float(values["width"])
            except ValueError:
                width = 1
            gb.graph.delete_figure(gb.edit_prop.graph_id)
            line_id = gb.graph.draw_line(points[0:2], points[2:], width=gb.WALL_WIDTH, color=gb.WALL_COLOR)
            gb.edit_prop.graph_id = line_id
            gb.edit_prop.material = material
            gb.edit_prop.width = width
            gb.edit_prop = None

        elif type(gb.edit_prop) == Transmitter:
            points = (values["x1"], values["y1"])
            try:
                points = tuple(int(p) for p in points if p != "")
            except ValueError:
                sg.popup_error("Coordinates from inputs are not integers!")
                return
            gb.edit_prop.point = points
            try:
                power = float(values["power"])
            except ValueError:
                power = 1

            try:
                freq = float(values["freq"])
            except ValueError:
                freq = 1e6
            gb.graph.delete_figure(gb.edit_prop.graph_id)
            transmitter_id = gb.graph.draw_point(points, gb.TRANSMITTER_SIZE, color=gb.TRANSMITTER_COLOR)
            gb.edit_prop.power = power
            gb.edit_prop.freq = freq
            gb.edit_prop.graph_id = transmitter_id
            gb.edit_prop = None

    elif event == "save":
        save_scene(gb.walls, gb.transmitters)

    elif event == "load":
        load_scene()


# ======================================================================================================================
# Single ray simulation
# ======================================================================================================================
def single_ray_routine(app, event, values):
    if event == "draw_ray":
        # clear previous ray and enable drawing new one
        clear_rays()
        gb.current_sub_mode = "draw_ray"
        app["draw_ray"].update(button_color=gb.BUTTON_ACTIVE_COLOR)

    elif event == "calc":
        try:
            step = float(values["step"])
        except ValueError:
            step = gb.SCENE_GRID[0]

        if not gb.rays:
            sg.popup_error("Draw ray first")
            return
        coefs = gb.rays[-1].get_dist_coef_array(step)
        if not coefs:
            return

        power_ref = gb.rays[-1].get_power_ref()
        power_values = [power_ref * abs(c)**2 for c in coefs[1:]]

        # plot results
        x_space = [i*step for i in range(len(power_values))]
        draw_plot(power_values, x_space, app["plot_canvas"].TKCanvas)

    elif event == "graph" and gb.current_sub_mode == "draw_ray":
        if gb.last_click:
            try:
                ap = int(values["AP"])
            except ValueError:
                ap = 0
            # create ray and propagate it
            vec = (values[event][0] - gb.last_click.point[0],
                   values[event][1] - gb.last_click.point[1])
            gb.rays.append(Ray(gb.last_click, vec, ap))
            gb.rays[-1].propagate(gb.walls)
            draw_ray(gb.rays[-1])
            # exit drawing sub_mode
            gb.current_sub_mode = None
            app["draw_ray"].update(button_color=gb.BUTTON_INACTIVE_COLOR)
            gb.last_click = None
        else:
            figures = gb.graph.get_figures_at_location(values[event])
            transmitter_list = [t for t in gb.transmitters if t.graph_id in figures]
            if transmitter_list:
                gb.last_click = transmitter_list[0]


def draw_ray(ray: Ray):
    sources = [ray.transmitter.point] + [line[0] for line in ray.reflections_list]
    destinations = [line[0] for line in ray.reflections_list]
    graph_ids = list()
    for src, dst in zip(sources, destinations):
        graph_ids.append(gb.graph.draw_line(src, dst, width=gb.RAY_SIZE, color=gb.RAY_COLOR))
    ray.graph_ids = graph_ids


def clear_rays():
    if gb.rays:
        for ray in gb.rays:
            for graph_id in ray.graph_ids:
                gb.graph.delete_figure(graph_id)
        gb.rays.clear()


def draw_figure(canvas, figure):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    return figure_canvas_agg


def draw_plot(y: list, x: list, canvas):
    fig = plt.figure(figsize=(5, 2))
    plt.plot(y, x)
    plt.grid()
    draw_figure(canvas, fig)


# ======================================================================================================================
# Multi ray simulation
# ======================================================================================================================
def multi_ray_routine(app, event, values):
    if event == "add_ray_multi":
        gb.current_sub_mode = event
        app[event].update(button_color=gb.BUTTON_ACTIVE_COLOR)
        app["delete_ray_multi"].update(button_color=gb.BUTTON_ACTIVE_COLOR)

    elif event == "delete_ray_multi":
        gb.current_sub_mode = event
        app[event].update(button_color=gb.BUTTON_ACTIVE_COLOR)
        app["add_ray_multi"].update(button_color=gb.BUTTON_ACTIVE_COLOR)

    elif event == "calc_multi":
        pass

    elif event == "graph" and gb.current_sub_mode in ("add_ray_multi", "delete_ray_multi"):
        pass
