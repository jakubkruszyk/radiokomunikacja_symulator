import window
from routines import single_ray_routine, draw_scene_routine, multi_ray_routine, clear_rays, diffraction_routine
import globals as gb
import PySimpleGUI as sg

lines = []

app = sg.Window("test", window.layout(), finalize=True)
gb.graph = app["graph"]

window.add_grid(gb.graph)

while True:
    # window event read
    event, values = app.read(timeout=50)
    # close event must be checked before anything else
    if event == sg.WIN_CLOSED:
        break

    # graph coordinates scaling
    if event == "graph":
        print(values[event])

    # mode routines
    if gb.current_mode == "draw_scene":
        draw_scene_routine(app, event, values)

    elif gb.current_mode == "single_ray":
        single_ray_routine(app, event, values)

    elif gb.current_mode == "multi_ray":
        multi_ray_routine(app, event, values)

    elif gb.current_mode == "diffraction":
        diffraction_routine(app, event, values)

    # ==================================================================================================================
    # common routines
    # ==================================================================================================================
    # change mode
    if event in ("draw_scene", "single_ray", "multi_ray", "diffraction"):
        # change displayed side-tab
        app[f"{event}_tab"].update(visible=True)
        app[f"{gb.current_mode}_tab"].update(visible=False)
        gb.current_mode = event
        # clear sub_mode variables
        gb.current_sub_mode = None
        gb.last_click = None
        gb.selected_t = None
        gb.selected_r1 = None
        gb.selected_r2 = None
        gb.diff_point = None
        clear_rays()
        gb.reflection_wall.clear()
