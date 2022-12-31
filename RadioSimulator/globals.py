# ======================================================================================================================
# Configuration
# ======================================================================================================================
WALL_COLOR = "#ffffff"
WALL_WIDTH = 5

TRANSMITTER_COLOR = "#ff0000"
TRANSMITTER_SIZE = 6

RAY_COLOR = "#ffff00"
RAY_SIZE = 2

SCENE_SIZE = (500, 300)  # size of scene in pixels
SCENE_GRID = (20, 20)  # size of one rectangle of grid in pixels
SIMULATION_GRID = ()  # size of one rectangle of grid in pixels
GRID_DOT_SIZE = 1
GRID_DOT_COLOR = "#969696"

BUTTON_ACTIVE_COLOR = "#50b800"
BUTTON_INACTIVE_COLOR = "#283b5b"

# scene parameters
SCALE = 1
FLOAT_COMP = 0.05

# ======================================================================================================================
# Global variables
# ======================================================================================================================
graph = None
current_mode = "draw_scene"

boundaries = [(0, 0, SCENE_SIZE[0], 0),
              (0, 0, 0, SCENE_SIZE[1]),
              (SCENE_SIZE[0], 0, SCENE_SIZE[0], SCENE_SIZE[1]),
              (0, SCENE_SIZE[1], SCENE_SIZE[0], SCENE_SIZE[1])]

# on scene objects
walls = list()
transmitters = list()
rays = list()


# common mode variables
current_sub_mode = None
last_click = None

# draw scene mode variables
edit_prop = None

# multi ray variables
reflection_wall = list()
