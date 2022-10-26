import window
import PySimpleGUI as sg
from routines import *

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

    # common routines
    if event in ("draw_scene", "dummy"):
        app[f"{event}_tab"].update(visible=True)
        app[f"{gb.current_mode}_tab"].update(visible=False)
        gb.current_mode = event
