## Imports
import os
import tkinter as tk
from typing import Optional, Dict, Any, List
from utils.globals import *  # For constants if needed
from utils.geometry_structures import AFFINE_TRANSFORM, MESH
from utils.globals import *

__all__ = ['OPENGL_CONTEXT',
           'TKINTER_CONTEXT']

## Data Structures
class OPENGL_CONTEXT():
    """
    OpenGL Context Class
    
    Manages all OpenGL-related state including window properties, transforms,
    meshes, and rendering configuration.
    
    Attributes:
        Name (str): Identifier for this context instance
        Width (int): Window width in pixels
        Height (int): Window height in pixels
        Aspect_Ratio (float): Width/Height ratio
        Last_Time (float): Timestamp of previous frame
        Delta_Time (float): Time elapsed since last frame
        Keys (Dict[str, Any]): Input state tracking dictionary
        Background_Color (List[float]): RGBA background color values
        Window (Any): GLFW window handle
        Color_Mode (str): Current color rendering mode
        FOV (float): Field of view in degrees for perspective projection
        Near (float): Near clipping plane distance
        Far (float): Far clipping plane distance
        Projection_Mode (str): Current projection type
        Shader_Program (Optional[int]): OpenGL shader program ID
        Transforms (Dict[str, AFFINE_TRANSFORM]): Named transform storage
        Meshes (Dict[str, MESH]): Named mesh storage
        Notes (str): Development notes and context
    """
    
    def __init__(self,
                 name: str = "OpenGL_Context",
                 width: int = WINDOW_WIDTH,
                 height: int = WINDOW_HEIGHT,
                 aspect_ratio: np.float64 = ASPECT_RATIO,
                 last_time: np.float64 = np.float64(LAST_TIME),
                 delta_time: np.float64 = DELTA_TIME,
                 keys: Dict[str, Any] = KEYS,
                 background_color = DARK_BLUE,
                 window: Any = 0,  # GLFW window handle
                 color_mode: str = SOLID_COLOR_MODE,
                 fov: np.float64 = FOV,
                 near: np.float64 = NEAR,
                 far: np.float64 = FAR,
                 projection_mode: str = ORTHOGRAPHIC_MODE,
                 shader_program: Optional[int] = None,
                 transforms: Dict[str, AFFINE_TRANSFORM] = {},
                 meshes: Dict[str, MESH] = {},
                 azimut = 0.0,
                 camera_elevation = 0.0,
                 orbital_distance = 50.0,
                 notes: str = "") -> None:
        """Initialize OpenGL context with default values."""
        self.Name: str = name
        self.Width: int = width
        self.Height: int = height
        self.Aspect_Ratio: np.float64 = aspect_ratio
        self.Last_Time: np.float64 = np.float64(last_time)
        self.Delta_Time: np.float64 = delta_time
        self.Keys: Dict[str, Any] = keys.copy()
        self.Background_Color = background_color
        self.Window: Any = window  # GLFW window handle
        self.Color_Mode: str = color_mode
        self.FOV: np.float64 = fov
        self.Near: np.float64 = near
        self.Far: np.float64 = far
        self.Projection_Mode: str = projection_mode
        self.Shader_Program: Optional[int] = shader_program
        self.Transforms: Dict[str, AFFINE_TRANSFORM] = transforms
        self.Meshes: Dict[str, MESH] = meshes
        self.Azimut = azimut # Y Axis rotation around the World frame of the focus point
        self.Camera_Elevation = camera_elevation # X axis rotation around the World Frame of the focus point
        self.Orbital_Distance = orbital_distance # Initial orbital distance of camera to focus point
        self.Notes: str = notes

class TKINTER_CONTEXT():
    """
    Tkinter Context Class
    
    Manages Tkinter GUI state and windows associated with an OpenGL context.
    
    Attributes:
        Dirty_Flag (bool): Indicates if the context has unprocessed changes
        Name (str): Identifier for this context instance
        Related_OpenGL_Context (str): Name of associated OpenGL context
        Root (tk.Tk): Tkinter root window instance
        File_Dialog_Path (str): Default directory for file operations
        Notes (str): Development notes and context
    """
    
    def __init__(self, window_context: OPENGL_CONTEXT, name: str = "Tkinter_Context") -> None:
        """
        Initialize Tkinter context with associated OpenGL context.
        
        Args:
            window_context (OPENGL_CONTEXT): Associated OpenGL context
            name (str): Name identifier for this context
        """
        self.Dirty_Flag: bool = False  # Must be first for state management
        self.Name: str = name
        self.Related_OpenGL_Context: str = window_context.Name
        self.Root: tk.Tk = tk.Tk()
        self.File_Dialog_Path: str = os.getcwd()
        self.Notes: str = ""

## Self-Test and Module Entry Point
def _self_test() -> bool:
    """
    Basic self-test for context management functionality.
    
    Returns:
        bool: True if all tests pass, False otherwise
    """
    try:
        # Test OpenGL context creation
        test_gl_context = OPENGL_CONTEXT()
        assert test_gl_context.Name == "OpenGL_Context"
        assert test_gl_context.Projection_Mode == ORTHOGRAPHIC_MODE
        
        # Test Tkinter context creation
        test_tk_context = TKINTER_CONTEXT(test_gl_context)
        assert test_tk_context.Name == "Tkinter_Context"
        assert test_tk_context.Related_OpenGL_Context == test_gl_context.Name
        
        # Clean up Tkinter window
        test_tk_context.Root.destroy()
        
        return True
    except Exception as e:
        print(f"Context manager self-test failed: {e}")
        return False

def _main() -> int:
    """
    Module entry point for testing context management.
    
    Returns:
        int: Exit code (0 for success)
    """
    success = _self_test()
    print(f"Context manager self-test: {'PASSED' if success else 'FAILED'}")
    return 0

if __name__ == "__main__":
    _main()
