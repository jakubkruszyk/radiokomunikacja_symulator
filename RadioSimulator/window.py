import PySimpleGUI as sg
import props
import globals as gb


def draw_scene_tab() -> list[list]:
    materials_names = [m.name for m in props.materials_list]
    properties_layout = [[sg.Text(name), sg.Text(value, key=f"property_{name}")]
                         for name, value in
                         zip(props.materials_list[0]._fields, props.materials_list[0])
                         if name != "name"]

    draw_scene_layout = [[sg.Button("Reset scene", key="reset_scene")],
                         [sg.Button("Draw", key="draw"), sg.Button("Edit", key="edit"),
                          sg.Button("Update", key="update", visible=False)],
                         [sg.Text("x1:"), sg.Input(key="x1", size=5), sg.Text("y1:"), sg.Input(key="y1", size=5)],
                         [sg.Text("x2:"), sg.Input(key="x2", size=5), sg.Text("y2:"), sg.Input(key="y2", size=5)],
                         [sg.Text("Width:"), sg.Input(key="width", size=5, default_text="1")],
                         [sg.Combo(materials_names, key="material_list", enable_events=True,
                                   default_value=materials_names[0])],
                         [sg.Column(properties_layout, scrollable=True, size=(150, 200))],
                         [sg.Button("Save", key="save")]]

    return draw_scene_layout


def layout() -> list[list]:
    """
     Returns layout of main window.
    """
    dummy_side_tab = [[sg.Button("Show", key="Show")],
                      [sg.Button("Hide", key="Hide")],
                      [sg.Button("Add", key="Add")]]

    side_menu = [[sg.Column(dummy_side_tab, key="dummy_tab"), sg.Column(draw_scene_tab(), visible=False,
                                                                        key="draw_scene_tab")]]

    top_menu = [sg.Button('Draw scene', key="draw_scene"), sg.Button("Option2", key="dummy")]

    main_layout = [[top_menu],
                   [sg.Column(side_menu), sg.Graph(gb.SCENE_SIZE, (0, 0), gb.SCENE_SIZE, background_color="black",
                                                   key="graph", enable_events=True)]]

    return main_layout


def add_grid(graph):
    for x in range(0, gb.SCENE_SIZE[0], gb.SCENE_GRID[0]):
        for y in range(0, gb.SCENE_SIZE[1], gb.SCENE_GRID[1]):
            graph.draw_point((x, y), gb.GRID_DOT_SIZE, color=gb.GRID_DOT_COLOR)
