# ======================================================================================================================
# Configuration
# ======================================================================================================================
# scene parameters
SCENE_SIZE = (500, 300)  # size of scene in pixels
SCENE_GRID = (20, 20)  # size of one rectangle of grid in pixels
SIMULATION_GRID = ()  # size of one rectangle of grid in pixels
SCALE = 1  # scaling parameter for scene, scale = 1 means 1px = 1m

# calculation parameters
FLOAT_COMP = 0.05
FLOAT_ZERO = 1e-6
MULTI_RAY_STEP = 100
DIFFRACTION_POINT_MARGIN = 10

# props colors and sizes - do not remove scale multiplier
WALL_COLOR = "#ffffff"
WALL_WIDTH = 5 * SCALE

TRANSMITTER_COLOR = "#ff0000"
TRANSMITTER_SIZE = 6 * SCALE

RECEIVER_COLOR = "#1a1aff"
RECEIVER_SIZE = 6 * SCALE

RAY_COLOR = "#ffff00"
RAY_SIZE = 2 * SCALE

GRID_DOT_SIZE = 1 * SCALE
GRID_DOT_COLOR = "#969696"

BUTTON_ACTIVE_COLOR = "#50b800"
BUTTON_INACTIVE_COLOR = "#283b5b"

# ======================================================================================================================
# Global variables - do not change
# ======================================================================================================================
graph = None
current_mode = "draw_scene"

boundaries = [(0, 0, SCENE_SIZE[0]*SCALE, 0),
              (0, 0, 0, SCENE_SIZE[1]*SCALE),
              (SCENE_SIZE[0]*SCALE, 0, SCENE_SIZE[0]*SCALE, SCENE_SIZE[1]*SCALE),
              (0, SCENE_SIZE[1]*SCALE, SCENE_SIZE[0]*SCALE, SCENE_SIZE[1]*SCALE)]

# on scene objects
walls = list()
transmitters = list()
receivers = list()
rays = list()


# common mode variables
current_sub_mode = None
last_click = None
selected_t = None
selected_r1 = None
selected_r2 = None
diff_point = None

# draw scene mode variables
edit_prop = None

# multi ray variables
reflection_wall = list()
