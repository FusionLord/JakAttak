VERSION = "alpha v0.4"

SCREENSIZE = (800,600) #do (0,0) if you want the same size as the main screen
FRAMERATE = 60  # default is 60. This is maximum framerate you allow, and it will affect the gameplay.
FULLSCREEN_MODE = False
SKIP_INTRO = False

MOTION_BLUR_UNPAUSED = 1  # default 1. can be anything between 1 to infinity, 1 being no blur
MOTION_BLUR_PAUSED = 1  # default 3. can be anything between 1 to infinity, 1 being no blur

WALL_THICKNESS = 0.1 #0.1  # default is 0.2, can be 0 to 1
TILE_SHADOW_SIZE = 0.3  # AT LEAST WALL THICKNESS, max is 1

GRIDSCALE = 40  # minimum is 10, and must be an int, prefer numbers that can evenly divide both dimensions of the screen's size
PRECISION = 1
SHOW_GRID = True
GRID_COLOR = (0, 0, 0)
GRID_ALPHA = 8
HUDSIZE = 32 #default is 16 or 32

DEBUG_HULL_TRACE = False
DEBUG_DISABLE_GIBS = False
DEBUG_QUADTREE = False
DEBUG_WORLD_RERENDER = False
DEBUG_TIME_MACHINE = False
DEBUG_TIME_MACHINE_SHOW_VARS = True
