# ======================================================================================================================
# Configuration
# ======================================================================================================================
WALL_COLOR = "#ffffff"
WALL_WIDTH = 5

SCENE_SIZE = (500, 300)  # size of scene in pixels
SCENE_GRID = (20, 20)  # size of one rectangle of grid in pixels
SIMULATION_GRID = ()  # size of one rectangle of grid in pixels
GRID_DOT_SIZE = 1
GRID_DOT_COLOR = "#969696"

BUTTON_ACTIVE_COLOR = "#50b800"
BUTTON_INACTIVE_COLOR = "#283b5b"

# ======================================================================================================================
# Global variables
# ======================================================================================================================
graph = None
current_mode = "draw_scene"

# on scene objects
walls = []
transmitters = []

# scene parameters
scale = 1

# common mode variables
current_sub_mode = None

# draw scene mode variables
last_click = None
edit_wall = None


