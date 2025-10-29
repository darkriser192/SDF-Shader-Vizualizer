## Imports. Make sure to maintain with main.py imports to
# Normal python imports. handles as mch as possible outside of specific requiremens
#import os # For operating system dependent functionality
#import sys # For system-specific parameters and functions
#import sympy as symp # For symbolic mathematics operations like solving equations, simplification, etc.
import numpy as np # For numerical operations, C base code optimized, fast and efficient
import scipy as scp # For scientific computing, advanced numerical methods and algorithms. prefered over numpy
import time # For time-related functions. Used for frame timing and delta time calculations has possible overlap with pygame time functions. Which is better?

# Trimesh Imports. Handles 3D mesh loading and processing if we don't build our own, might build our own later
import trimesh # 3D mesh processing library

## OpenGL Imports.
import OpenGL # For OpenGL bindings
from OpenGL.GL import * # pyright: ignore[reportWildcardImportFromLibrary]
from OpenGL.GLU import * # pyright: ignore[reportWildcardImportFromLibrary]
from OpenGL.GLUT import * # pyright: ignore[reportWildcardImportFromLibrary]
import glfw # For creating windows and contexts

# For game development. Will be used to handle keyboard and mouse input
import pygame as pg # For input handling and other utilities we do not want to develop from scratch
from pygame.locals import * # pyright: ignore[reportWildcardImportFromLibrary]

# Tkinter Imports. For GUI applications like file dialogs and other variables
import tkinter as tk # For GUI applications

### Global Variables

## Window Parameters
WINDOW_WIDTH = 1600 # Width of the OpenGL window
WINDOW_HEIGHT = 1200 # Height of the OpenGL window
ASPECT_RATIO = np.float64(WINDOW_WIDTH) / np.float64(WINDOW_HEIGHT) # Aspect ratio of the OpenGL window

## Camera Parameter
# WORLD_TRANSFORM = np.identity(4) # World transformation matrix. No longer needed since we have a World_Frame AFFINE_TRANSFORM
# CAMERA_FOCUS = np.array([0.0, 0.0, 0.0]) # Point the camera is looking at wrt world origin. No longer needed since we have a Camera_Focus AFFINE_TRANSFORM
# CAMERA_TRANSFORM = np.identity(4) # Camera transformation matrix. No longer needed since we have a Camera_Frame AFFINE_TRANSFORM
FOV = np.float64(70.0) # Field of View for perspective projection in degrees
NEAR = np.float64(50.0) # Near clipping plane for perspective projection
FAR = np.float64(100.0) # Far clipping plane for perspective projection
CAMERA_ORBIT_RADIUS = np.float64(100.0) # Initial distance from camera to focus point origin
CAMERA_STEP_SIZE = np.float64(0.5) 

## Colors (RGBA)
DARK_BLUE = np.array([0.1, 0.1, 0.2, 1.0], dtype=np.float64) # RGBA for dark blue background
LIGHT_GRAY = np.array([0.8, 0.8, 0.8, 1.0], dtype=np.float64) # RGBA for light gray objects
WHITE = np.array([1.0, 1.0, 1.0, 1.0], dtype=np.float64) # RGBA for white objects
RED = np.array([1.0, 0.0, 0.0, 1.0], dtype=np.float64) # RGBA for red objects
GREEN = np.array([0.0, 1.0, 0.0, 1.0], dtype=np.float64) # RGBA for green objects
BLUE = np.array([0.0, 0.0, 1.0, 1.0], dtype=np.float64) # RGBA for blue objects
YELLOW = np.array([1.0, 1.0, 0.0, 1.0], dtype=np.float64) # RGBA for yellow objects
CYAN = np.array([0.0, 1.0, 1.0, 1.0], dtype=np.float64) # RGBA for cyan objects
MAGENTA = np.array([1.0, 0.0, 1.0, 1.0], dtype=np.float64) # RGBA for magenta objects

## Tolerances
EPS = np.float64(1e-6) # Small value for random use in calculations to avoid division by zero or similar issues
F32PS = np.float64(1.19e-07)
F64EPS = np.float64(2.22e-16)
F128EPS = np.float64(1.93e-34)
LASER_SPOT_DIAMETER = np.float64(0.05)  # mm 
MELT_POOL_DIAMETER = np.float64(2.0 * LASER_SPOT_DIAMETER) # mm
GEOMETRIC_TOLERANCE = np.float64(0.01)  # mm (±0.01 mm mechanical tolerance)
# Area thresholds with safety factors
# Melt pool: equilateral triangle, diameter 0.1mm, with 1/3 safety factor
MELT_POOL_AREA_BASE = np.float64((np.sqrt(3)/4) * (MELT_POOL_DIAMETER * np.sqrt(3))**2)  # ≈ 1.3e-2 mm²
MELT_POOL_AREA_THRESHOLD = np.float64(MELT_POOL_AREA_BASE / 3)  # ≈ 4.3e-3 mm²
# Geometric tolerance: equilateral triangle, side 0.01mm, with 1/3 safety factor  
GEOMETRIC_TOLERANCE_AREA_BASE = np.float64((np.sqrt(3)/4) * GEOMETRIC_TOLERANCE**2)  # ≈ 4.33e-5 mm²
GEOMETRIC_TOLERANCE_AREA = np.float64(GEOMETRIC_TOLERANCE_AREA_BASE / 2)  # ≈ 2.17e-5 mm²
# Numerical precision: well above float64 machine epsilon but practically zero
NUMERICAL_PRECISION_AREA = np.float64(1e-12)  # mm²

## Timing
FPS = np.float64(60.0) # Target frames per second target for rendering 1 Million faces at 60 FPS with solid color is the goal of this program

## SDF Parameters
SDF_BOX_SIZE = np.float64(10.0) # Size of the SDF bounding box
SDF_GRID_SIZE = np.float64(0.01) # Grid size of the SDF
SDF_STEP_SIZE = np.float64(0.1) # Step size for ray marching in the SDF

## Other
GLOBAL_TIME = time.time() # Global time variable at start of program
LAST_TIME = GLOBAL_TIME # Last measured time
DELTA_TIME = np.float64(np.abs(LAST_TIME - GLOBAL_TIME)) # Difference between Global_Time and Last_Time
KEYS = { # Dictionary to hold key states. There are the leys supported by the program, if new ones are needed we msut add them here first. lets try not to create a new dictionary at runtime
    "W": False, "W_FLAG": False,
    "A": False, "A_FLAG": False,
    "S": False, "S_FLAG": False,
    "D": False, "D_FLAG": False,
    "Q": False, "Q_FLAG": False,
    "E": False, "E_FLAG": False,
    "UP": False, "UP_FLAG": False,
    "DOWN": False, "DOWN_FLAG": False,
    "LEFT": False, "LEFT_FLAG": False,
    "RIGHT": False, "RIGHT_FLAG": False,
    "PAGE_UP": False, "PAGE_UP_FLAG": False,
    "PAGE_DOWN": False, "PAGE_DOWN_FLAG": False,
    "SHIFT": False, "SHIFT_FLAG": False,
    "CTRL": False, "CTRL_FLAG": False,
    "ALT": False, "ALT_FLAG": False,
    "SPACE": False, "SPACE_FLAG": False,
    "ESCAPE": False, "ESCAPE_FLAG": False,
    "MOUSE_LEFT": False, "MOUSE_LEFT_FLAG": False,
    "MOUSE_RIGHT": False, "MOUSE_RIGHT_FLAG": False,
    "MOUSE_X": np.float64(0.0), "LAST_MOUSE_X": np.float64(0.0),
    "MOUSE_Y": np.float64(0.0), "LAST_MOUSE_Y": np.float64(0.0),
    "1": False, "2": False, "3": False, "4": False, "5": False, "6": False, "7": False, "8": False, "9": False, "0": False,
    "1_FLAG": False, "2_FLAG": False, "3_FLAG": False, "4_FLAG": False, "5_FLAG": False, "6_FLAG": False, "7_FLAG": False, "8_FLAG": False, "9_FLAG": False, "0_FLAG": False,
    "+": False, "-": False,
    "+_FLAG": False, "-_FLAG": False
    } # TODO: Should this be a np.array for faster access? can we vectorize input handling? I am not aware of a way to do this without a loop or direct line by line access
TRANSFORMS = {} # Global dictionary to hold AFFINE_TRANSFORM objects
MESHES = {} # Global dictionary to hold RENDER_MESH objects
## MESH CONSTANTS
DEFAULT_MESH_SIZE = 250000
INVALID_BUFFER_ID = -1

# Transform Identity Constants
IDENTITY_TRANSLATION = np.array([0.0, 0.0, 0.0], dtype=np.float64)
IDENTITY_ROTATION = np.eye(3, dtype=np.float64)
IDENTITY_SCALE = np.array([1.0, 1.0, 1.0], dtype=np.float64)

# Frame Name Constants
DEFAULT_AFFINE_NAME = "Affine_Transform"
DEFAULT_AFFINE_PARENT = "Canonical_Frame"
DEFAULT_AFINE_CHILD = "None" # Meaning it is a frame and not a transform

# Mesh Name Constrants
DEFAULT_MESH_NAME = "Default_Mesh"
DEFAULT_MESH_PARENT = "World_Frame"

# Projection Mode Constants
ORTHOGRAPHIC_MODE = "Orthographic"
PERSPECTIVE_MODE = "Perspective"

# Render Mode Constants
SOLID_COLOR_MODE = "Solid"
VERTEX_COLOR_MODE = "Vertex"
NORMAL_COLOR_MODE = "Normal"
POINT_CLOUD = "Point_Cloud"

def precision_test():
    # float32 precision breakdown
    f32 = np.float32(1.0)
    f32_eps = np.finfo(np.float32).eps
    print(f"float32 epsilon: {f32_eps}")
    print(f"1.0 + eps/2 == 1.0: {f32 + f32_eps/2 == f32}")  # True
    print(f"1.0 + eps == 1.0: {f32 + f32_eps == f32}")      # False
    
    # float64 precision breakdown  
    f64 = np.float64(1.0)
    f64_eps = np.finfo(np.float64).eps
    print(f"float64 epsilon: {f64_eps}")
    
    # Rotation matrix precision example
    angle = np.pi/3  # 60 degrees
    cos_32 = np.cos(np.float32(angle))
    cos_64 = np.cos(np.float64(angle))
    cos_128 = np.cos(np.longdouble(angle))  # float128 equivalent
    
    print(f"cos(π/3) float32:  {cos_32}")
    print(f"cos(π/3) float64:  {cos_64}")  
    print(f"cos(π/3) float128: {cos_128}")

def _main():
    """
    Write any tests we might want to perform about any of the constants here
    """
    precision_test()
    return 0

## Entry point
if __name__ == "__main__":
    _main()