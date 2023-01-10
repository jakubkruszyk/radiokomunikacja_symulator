import PySimpleGUI as sg
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from numpy import ndarray
import globals as gb
import math

from props import Wall, Transmitter, Receiver, Material
from ray import Ray, get_diffraction_power
from files import save_scene, load_scene
from materials import materials_list
from geometrics import point_point_distance, distance_spaces


# ======================================================================================================================
# Helper functions
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
        if values["draw_t_radio_dbm"]:
            dbm = float(values["power"])
            power = 10**(dbm/10) / 1000
        else:
            power = float(values["power"])
    except ValueError:
        power = 1

    try:
        freq = float(values["freq"])
    except ValueError:
        freq = 1e6
    gb.transmitters.append(Transmitter(values_s, circle_id, power, freq))


def draw_receiver(app, event, values):
    values_s = point_quantization(values[event])
    circle_id = gb.graph.draw_point(values_s, gb.RECEIVER_SIZE, color=gb.RECEIVER_COLOR)
    gb.receivers.append(Receiver(values_s, circle_id))


def clear_displayed_points(app):
    app["x1"].update("")
    app["y1"].update("")
    app["x2"].update("")
    app["y2"].update("")


def show_line_layout(app):
    app["draw_line_layout"].update(visible=True)
    app["draw_transmitter_layout"].update(visible=False)
    clear_displayed_points(app)


def show_transmitter_layout(app):
    app["draw_line_layout"].update(visible=False)
    app["draw_transmitter_layout"].update(visible=True)
    clear_displayed_points(app)


def show_receiver_layout(app):
    app["draw_line_layout"].update(visible=False)
    app["draw_transmitter_layout"].update(visible=False)
    clear_displayed_points(app)


def edit_wall(app, event, values):
    # get ids of objects that user clicked on
    objects = gb.graph.get_figures_at_location(values[event])
    # check walls, transmitter lists for matching ids
    filtered = [o for o in (*gb.walls, *gb.transmitters, *gb.receivers) if o.graph_id in objects]
    if filtered:
        gb.edit_prop = filtered[0]
        if type(gb.edit_prop) == Wall:
            show_line_layout(app)
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
            app["x1"].update(gb.edit_prop.point[0])
            app["y1"].update(gb.edit_prop.point[1])
            app["power"].update(gb.edit_prop.power)
            app["freq"].update(gb.edit_prop.freq)

        elif type(gb.edit_prop) == Receiver:
            show_receiver_layout(app)
            app["x1"].update(gb.edit_prop.point[0])
            app["y1"].update(gb.edit_prop.point[1])

    else:
        clear_displayed_points(app)


def draw_scene_button_update(app, active):
    app["draw"].update(button_color=gb.BUTTON_INACTIVE_COLOR)
    app["edit"].update(button_color=gb.BUTTON_INACTIVE_COLOR)
    app["transmitter"].update(button_color=gb.BUTTON_INACTIVE_COLOR)
    app["receiver"].update(button_color=gb.BUTTON_INACTIVE_COLOR)
    app["delete"].update(button_color=gb.BUTTON_INACTIVE_COLOR)
    app["delete_ray_multi"].update(button_color=gb.BUTTON_INACTIVE_COLOR)
    app["add_ray_multi"].update(button_color=gb.BUTTON_INACTIVE_COLOR)
    app["calc_multi"].update(button_color=gb.BUTTON_INACTIVE_COLOR)
    app["delete_ray_diff"].update(button_color=gb.BUTTON_INACTIVE_COLOR)
    app["add_ray_diff"].update(button_color=gb.BUTTON_INACTIVE_COLOR)
    app["calc_diff"].update(button_color=gb.BUTTON_INACTIVE_COLOR)
    app[active].update(button_color=gb.BUTTON_ACTIVE_COLOR)


def delete_element(app, event, values):
    figures = gb.graph.get_figures_at_location(values[event])
    walls = [wall for wall in gb.walls if wall.graph_id in figures]
    transmitters = [transmitter for transmitter in gb.transmitters if transmitter.graph_id in figures]
    receivers = [receiver for receiver in gb.receivers if receiver.graph_id in figures]
    if transmitters:
        gb.graph.delete_figure(transmitters[0].graph_id)
        gb.transmitters.remove(transmitters[0])
    elif receivers:
        gb.graph.delete_figure(receivers[0].graph_id)
        gb.receivers.remove(receivers[0])
    elif walls:
        gb.graph.delete_figure(walls[0].graph_id)
        gb.walls.remove(walls[0])


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


def draw_plot(y: list | ndarray, x: list | ndarray, canvas):
    fig = plt.figure(figsize=(5, 2))
    fig.add_subplot(111).plot(x, y)
    plt.grid()
    draw_figure(canvas, fig)


def multi_ray_power(steps: int):
    x_space, y_space, dist_space = distance_spaces(gb.selected_r1.point, gb.selected_r2.point, steps)
    power_list = list()
    for x, y in zip(x_space, y_space):
        for ray in gb.rays:
            ray.propagate_to_point((x, y), ray.forced_reflection_walls)
        coefficients = [ray.get_coef_at_end() for ray in gb.rays]
        power_ref = gb.rays[0].get_power_ref()
        coefs_sum = sum(coefficients)
        power = power_ref * abs(coefs_sum)**2
        power_list.append(power)

    return power_list, dist_space


# ======================================================================================================================
# Draw scene mode
# ======================================================================================================================
def draw_scene_routine(app, event, values):
    """
    Draw scene mode event-loop routine
    """

    if event == "graph":
        if gb.current_sub_mode == "draw_l":
            draw_wall(app, event, values)
        elif gb.current_sub_mode == "draw_t":
            draw_transmitter(event, values)
        elif gb.current_sub_mode == "draw_r":
            draw_receiver(app, event, values)
        elif gb.current_sub_mode == "edit":
            edit_wall(app, event, values)
        elif gb.current_sub_mode == "delete":
            delete_element(app, event, values)

    elif event == "reset_scene":
        for line in gb.walls:
            gb.graph.delete_figure(line.graph_id)
        gb.walls.clear()
        for transmitter in gb.transmitters:
            gb.graph.delete_figure(transmitter.graph_id)
        gb.transmitters.clear()

    elif event == "draw":
        gb.current_sub_mode = "draw_l"
        draw_scene_button_update(app, "draw")
        show_line_layout(app)

    elif event == "transmitter":
        gb.current_sub_mode = "draw_t"
        draw_scene_button_update(app, "transmitter")
        show_transmitter_layout(app)

    elif event == "receiver":
        gb.current_sub_mode = "draw_r"
        draw_scene_button_update(app, "receiver")
        show_receiver_layout(app)

    elif event == "edit":
        gb.current_sub_mode = "edit"
        draw_scene_button_update(app, "edit")

    elif event == "delete":
        gb.current_sub_mode = "delete"
        draw_scene_button_update(app, "delete")

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
        save_scene()

    elif event == "load":
        load_scene()


# ======================================================================================================================
# Single ray simulation
# ======================================================================================================================
def single_ray_routine(app, event, values):
    """
        Single ray mode event-loop routine
    """

    if event == "draw_ray":
        # clear previous ray and enable drawing new one
        clear_rays()
        gb.current_sub_mode = "draw_ray"
        app["draw_ray"].update(button_color=gb.BUTTON_ACTIVE_COLOR)

    elif event == "calc":
        try:
            step = float(values["step"])
        except ValueError:
            step = 1

        if not gb.rays:
            sg.popup_error("Draw ray first")
            return
        coefs = gb.rays[-1].get_dist_coef_array(step)
        if not coefs:
            return

        # calculate power array
        power_ref = gb.rays[-1].get_power_ref()
        power_values = [power_ref * abs(c)**2 for c in coefs[1:]]

        # convert if selected so
        if values["single_radio_dbm"]:
            power_values = [10*math.log10(p/0.001) for p in power_values]

        elif values["single_radio_db"]:
            initial_power = gb.rays[-1].transmitter.power
            power_values = [10*math.log10(p/initial_power) for p in power_values]

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


# ======================================================================================================================
# Multi ray simulation
# ======================================================================================================================
def multi_ray_routine(app, event, values):
    """
        Multi ray mode event-loop routine
    """

    if event in ("add_ray_multi", "delete_ray_multi", "calc_multi"):
        gb.current_sub_mode = event
        gb.last_click = None
        draw_scene_button_update(app, event)

    elif event == "graph" and gb.current_sub_mode == "add_ray_multi":
        if gb.selected_t:
            figures = gb.graph.get_figures_at_location(values[event])
            receivers_list = [r for r in gb.receivers if r.graph_id in figures]
            wall_list = [wall for wall in gb.walls if wall.graph_id in figures]
            if wall_list:
                gb.reflection_wall.append(wall_list[0])
            elif receivers_list:
                gb.selected_r1 = receivers_list[0]
                gb.rays.append(Ray(gb.selected_t, (1, 1), 1))  # ap and vec doesn't matter here
                gb.rays[-1].forced_reflection_walls = gb.reflection_wall.copy()
                gb.rays[-1].propagate_to_point(receivers_list[0].point, gb.reflection_wall)
                draw_ray(gb.rays[-1])
                gb.last_click = None
                gb.reflection_wall.clear()

        else:
            figures = gb.graph.get_figures_at_location(values[event])
            transmitter_list = [t for t in gb.transmitters if t.graph_id in figures]
            if transmitter_list:
                gb.selected_t = transmitter_list[0]

    elif event == "graph" and gb.current_sub_mode == "delete_ray_multi":
        figures = gb.graph.get_figures_at_location(values[event])
        for ray in gb.rays:
            test = [line for line in ray.graph_ids if line in figures]
            if any(test):
                for graph_id in ray.graph_ids:
                    gb.graph.delete_figure(graph_id)
                gb.rays.remove(ray)

    elif event == "graph" and gb.current_sub_mode == "calc_multi":
        figures = gb.graph.get_figures_at_location(values[event])
        receivers_list = [r for r in gb.receivers if r.graph_id in figures]
        if not receivers_list:
            return
        gb.selected_r2 = receivers_list[0]
        try:
            step = int(values["diff_step"])
        except ValueError:
            step = gb.MULTI_RAY_STEP
        p_values, space = multi_ray_power(step)
        # convert if selected so
        if values["multi_radio_db"]:
            initial_power = gb.rays[-1].transmitter.power
            p_values = [10*math.log10(p/initial_power) for p in p_values]

        elif values["multi_radio_dbm"]:
            p_values = [10*math.log10(p/0.001) for p in p_values]

        draw_plot(p_values, space, app["plot_canvas"].TKCanvas)


# ======================================================================================================================
# Diffraction simulation
# ======================================================================================================================
def diffraction_routine(app, event, values):
    """
        Diffraction mode event-loop routine
    """

    if event in ("add_ray_diff", "delete_ray_diff", "calc_diff"):
        draw_scene_button_update(app, event)
        gb.current_sub_mode = event
        gb.last_click = None

    elif event == "graph" and gb.current_sub_mode == "add_ray_diff" and not gb.rays:
        figures = gb.graph.get_figures_at_location(values[event])
        receivers_list = [r for r in gb.receivers if r.graph_id in figures]
        wall_list = [wall for wall in gb.walls if wall.graph_id in figures]
        transmitter_list = [t for t in gb.transmitters if t.graph_id in figures]

        if not gb.selected_t:
            if transmitter_list:
                gb.selected_t = transmitter_list[0]

        elif not gb.diff_point:
            if wall_list:
                point = values[event]
                points_list = []
                for wall in wall_list:
                    if point_point_distance(point, wall.points[0:2]) < gb.DIFFRACTION_POINT_MARGIN:
                        points_list.append(wall.points[0:2])
                    elif point_point_distance(point, wall.points[2:]) < gb.DIFFRACTION_POINT_MARGIN:
                        points_list.append(wall.points[2:])

                gb.diff_point = points_list[0] if points_list else None

        elif not gb.selected_r1:
            if receivers_list:
                gb.selected_r1 = receivers_list[0]
                lines = [gb.graph.draw_line(gb.selected_t.point, gb.diff_point,
                                            width=gb.RAY_SIZE, color=gb.RAY_COLOR),
                         gb.graph.draw_line(gb.diff_point, gb.selected_r1.point,
                                            width=gb.RAY_SIZE, color=gb.RAY_COLOR),
                         gb.graph.draw_line(gb.selected_t.point, gb.selected_r1.point,
                                            width=gb.RAY_SIZE, color=gb.RAY_COLOR)]
                gb.rays.append(Ray(gb.selected_t, (1, 1)))
                gb.rays[-1].graph_ids = lines

    elif event == "graph" and gb.current_sub_mode == "delete_ray_diff":
        figures = gb.graph.get_figures_at_location(values[event])
        for ray in gb.rays:
            test = [line for line in ray.graph_ids if line in figures]
            if any(test):
                for graph_id in ray.graph_ids:
                    gb.graph.delete_figure(graph_id)
                gb.rays.remove(ray)

    elif event == "graph" and gb.current_sub_mode == "calc_diff":
        figures = gb.graph.get_figures_at_location(values[event])
        receivers_list = [r for r in gb.receivers if r.graph_id in figures]
        if not receivers_list:
            return

        gb.selected_r2 = receivers_list[0]
        try:
            step = int(values["diff_step"])
        except ValueError:
            step = gb.MULTI_RAY_STEP

        x_space, y_space, dist_space = distance_spaces(gb.selected_r1.point, gb.selected_r2.point, step)

        if values["diff_radio_db"]:
            attenuation = [get_diffraction_power(gb.rays[-1], gb.diff_point, (x, y), gb.walls, mode=True)
                           for x, y in zip(x_space, y_space)]
            draw_plot(attenuation, dist_space, app["plot_canvas"].TKCanvas)

        elif values["diff_radio_lin"]:
            coefs = [get_diffraction_power(gb.rays[-1], gb.diff_point, (x, y), gb.walls)
                     for x, y in zip(x_space, y_space)]
            power_ref = gb.rays[-1].get_power_ref()
            power = [power_ref * abs(coef)**2 for coef in coefs]
            draw_plot(power, dist_space, app["plot_canvas"].TKCanvas)
