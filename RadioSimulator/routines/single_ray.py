import PySimpleGUI as sg
import RadioSimulator.globals as gb
from RadioSimulator.ray import Ray


# ======================================================================================================================
# Single ray simulation
# ======================================================================================================================
def single_ray_routine(app, event, values):
    if event == "graph":
        if gb.last_click:
            vec = (values[event][0] - gb.last_click.point[0],
                   values[event][1] - gb.last_click.point[1])
            gb.rays.append(Ray(gb.last_click, vec, 10))
            gb.rays[-1].propagate(gb.walls)
            draw_ray(gb.rays[-1])
            gb.last_click = None
        else:
            figures = gb.graph.get_figures_at_location(values[event])
            transmitter_list = [t for t in gb.transmitters if t.graph_id in figures]
            if transmitter_list:
                gb.last_click = transmitter_list[0]


def draw_ray(ray: Ray):
    sources = [ray.transmitter.point] + [line[0] for line in ray.reflections_list]
    destinations = [line[0] for line in ray.reflections_list]
    for src, dst in zip(sources, destinations):
        gb.graph.draw_line(src, dst, width=gb.RAY_SIZE, color=gb.RAY_COLOR)
    pass
