import window
from routines import single_ray_routine, draw_scene_routine, multi_ray_routine
import globals as gb
import PySimpleGUI as sg

lines = []

app = sg.Window("test", window.layout(), finalize=True)
gb.graph = app["graph"]

window.add_grid(gb.graph)

while True:
    event, values = app.read(timeout=50)
    if event == sg.WIN_CLOSED:
        break

    # mode routines
    if gb.current_mode == "draw_scene":
        draw_scene_routine(app, event, values)

    elif gb.current_mode == "single_ray":
        single_ray_routine(app, event, values)

    elif gb.current_mode == "multi_ray":
        multi_ray_routine(app, event, values)

    # ==================================================================================================================
    # common routines
    # ==================================================================================================================
    # change mode
    if event in ("draw_scene", "single_ray", "multi_ray"):
        app[f"{event}_tab"].update(visible=True)
        app[f"{gb.current_mode}_tab"].update(visible=False)
        gb.current_mode = event
        gb.current_sub_mode = None
        gb.last_click = None
