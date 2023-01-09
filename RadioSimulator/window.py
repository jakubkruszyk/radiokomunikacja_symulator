import PySimpleGUI as sg
import globals as gb
from materials import materials_list


def draw_scene_tab() -> list[list]:
    """
        Function that generates pysimplegui layout for draw-scene mode
    """
    materials_names = [m.name for m in materials_list]
    properties_layout = [[sg.Text(name), sg.Text(value, key=f"property_{name}")]
                         for name, value in
                         zip(materials_list[0]._fields, materials_list[0])
                         if name != "name"]

    draw_line_layout = [[sg.Text("Width:"), sg.Input(key="width", size=5, default_text="1")],
                        [sg.Combo(materials_names, key="material_list", enable_events=True,
                                  default_value=materials_names[0])],
                        [sg.Column(properties_layout, key="properties_layout", scrollable=True, size=(150, 200))]]

    draw_transmitter_layout = [[sg.Text("Transmitter power"), sg.Input(key="power", size=5, default_text="1")],
                               [sg.Text("Frequency [Hz]"), sg.Input(key="freq", size=12, default_text="1000000")]]

    draw_scene_layout = [[sg.Button("Reset scene", key="reset_scene")],
                         [sg.Button("Draw", key="draw"), sg.Button("Add T", key="transmitter"),
                          sg.Button("Add R", key="receiver")],
                         [sg.Button("Edit", key="edit"), sg.Button("Delete", key="delete"),
                          sg.Button("Update", key="update")],
                         [sg.Text("Scale"), sg.Input(key="scale", size=5, default_text=gb.SCALE)],
                         [sg.Text("x1:"), sg.Input(key="x1", size=5), sg.Text("y1:"), sg.Input(key="y1", size=5)],
                         [sg.Text("x2:"), sg.Input(key="x2", size=5), sg.Text("y2:"), sg.Input(key="y2", size=5)],
                         [sg.Column(draw_line_layout, key="draw_line_layout", visible=True),
                          sg.Column(draw_transmitter_layout, key="draw_transmitter_layout", visible=False)],
                         [sg.Button("Save", key="save"), sg.Button("Load", key="load")]]

    return draw_scene_layout


def single_ray_tab() -> list[list]:
    """
    Function that generates pysimplegui layout for single-ray mode
    """

    single_layout = [[sg.Text("AP"), sg.Input("3", key="AP", size=5)],
                     [sg.Text("Distance step"), sg.Input(f"{gb.SCENE_GRID[0]}", key="step", size=5)],
                     [sg.Button("Draw ray", key="draw_ray"), sg.Button("Calculate", key="calc")],
                     [sg.Radio("Linear", "single_radio", key="single_radio_lin", default=True)],
                     [sg.Radio("dBm", "single_radio", key="single_radio_dbm")],
                     [sg.Radio("dB", "single_radio", key="single_radio_db")]]

    return single_layout


def multi_ray_tab() -> list[list]:
    """
        Function that generates pysimplegui layout for multi-ray mode
    """
    multi_layout = [[sg.Button("Add ray", key="add_ray_multi"), sg.Button("Delete ray", key="delete_ray_multi")],
                    [sg.Button("Calculate", key="calc_multi")],
                    [sg.Radio("Linear", "multi_radio", key="multi_radio_lin", default=True)],
                    [sg.Radio("dBm", "multi_radio", key="multi_radio_dbm")],
                    [sg.Radio("dB", "multi_radio", key="multi_radio_db")]]

    return multi_layout


def diffraction_tab() -> list[list]:
    """
        Function that generates pysimplegui layout for diffraction mode
    """
    diff_layout = [[sg.Button("Add ray", key="add_ray_diff"), sg.Button("Delete ray", key="delete_ray_diff")],
                   [sg.Button("Calculate", key="calc_diff")],
                   [sg.Text("Mode:")],
                   [sg.Radio("Linear", "diff_radio", key="diff_radio_lin", default=True)],
                   [sg.Radio("dBm", "diff_radio", key="diff_radio_dbm")],
                   [sg.Radio("dB", "diff_radio", key="diff_radio_db")]]
    return diff_layout


def layout() -> list[list]:
    """
     Returns layout of main window.
    """
    side_menu = [[sg.Column(draw_scene_tab(), visible=True, key="draw_scene_tab"),
                  sg.Column(single_ray_tab(), visible=False, key="single_ray_tab"),
                  sg.Column(multi_ray_tab(), visible=False, key="multi_ray_tab"),
                  sg.Column(diffraction_tab(), visible=False, key="diffraction_tab")]]

    top_menu = [sg.Button('Draw scene', key="draw_scene"),
                sg.Button("Single ray", key="single_ray"),
                sg.Button("Multi ray", key="multi_ray"),
                sg.Button("Diffraction", key="diffraction")]

    scene = [[sg.Graph(gb.SCENE_SIZE, (0, 0), gb.SCENE_SIZE, background_color="black",
                       key="graph", enable_events=True)],
             [sg.Canvas(key='plot_canvas', size=(gb.SCENE_SIZE[1], 200))]]

    main_layout = [[top_menu],
                   [sg.HSeparator()],
                   [sg.Column(side_menu, vertical_alignment="top"), sg.Column(scene)]]

    return main_layout


def add_grid(graph):
    for x in range(0, gb.SCENE_SIZE[0], gb.SCENE_GRID[0]):
        for y in range(0, gb.SCENE_SIZE[1], gb.SCENE_GRID[1]):
            graph.draw_point((x, y), gb.GRID_DOT_SIZE, color=gb.GRID_DOT_COLOR)
