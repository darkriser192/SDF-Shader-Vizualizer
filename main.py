""" Project Name: Play - Signed Distance Field Visualization and Manipulation Tool

Author: 
    Rodrigo Enriquez Gutierrez

Description:
    Signed Distance Field (SDF) visualization and manipulation tool.
    Everything is created in 3D Space, even 2D shapes are created in the XY plane at Z=0.
    It tries to utilize as many conepts from robotics as possible to describe postions and movements in 3D space.
    While taking advantage of graphics programming concepts to optimize rendering and visualization.

Declaration: 
    Main entry point for the Play application. 

Long tearm declaration: 
    Handles OpenGL context creation, window management, and the main rendering loop.

Design pattern: Struct-and-function based modular design

Requirements:
- Python 3.11+ -> Meant to be a modern python application taking advantage of latest features.
- PyOpenGL
- GLFW
- Pygame
- Numpy
- Sympy
- Trimesh
- Tkinter

Notes:
- This file initializes the OpenGL context using GLFW, sets up the window, and enters the main rendering loop.
- Global variables are used to create a consistent state across functions specially at creation time, but may be used for state management as needed.
- 

Notes on design decisions:
 
 General Approach: Struct-and-function based modular design
 - Clases will have minimal functionality, mainly to hold data.
 - Functions will operate on these classes to perform operations.
 - This approach keeps data and operations separate, making it easier to manage and extend.
 
 Related to Affine Transformations:
 - Right-hand rule convention for coordinate systems.
 - World Frame Z+ is up, Y+ is forward, X+ is right. Important is the Z+ axis direction for gravity and orientation.
 - Transformations are applied in the order: Scale -> Rotate -> Translate -> Shear (if needed).
 - 

Notes on transform/frame mathematics:
 - (0) Canonical Frame [Root/Identity]. Z+ Axis points up and away from the floor
   ├──> (1) Transform Canonical→Focus
   │    └──> (2) Focus Frame
   │         └──> (3) Transform Focus→Camera
   │              └──> (4) Camera Frame Z+ Points towards player
   │                   ├──> (5) Transform Camera→Near Plane
   │                   │    └──> (6) Near Plane Frame. Z+ Points towards FP. Represents the screen
   │                   └──> (5) Transform Camera→Far Plane
   │                        └──> (6) Far Plane Frame Z+ Points towards FP. Used for Far distance clipping.
   │
   └──> (1) Transform Cannonical→World. Full 6-DOF
        └──> (2) World Frame
             └──> (3) Tranform to objects and (4) object frames nested/repeated

- Canonical Frame: {E} = eye(4). "{E}" E-Frame. this might be a good convention to addopt
- Transform Canonical→Focus: T_E_FP. Has full 6-DOF. "T_E_Fp" Transform from {E} to {Fp}. This may be a good convention to addopt.
- Focus Point: {Fp}. I think we only really case about the position of this point. but we might end up just traing everything regardless
- Will definelty need to track the transforms between the Focus Point and the World Frame. Might as well just construct it at creation.  
- 
- 

TODO-List:
- Added more logging events where relevant
- Add more detailed logging for debugging purposes.
- Implement GUI elements using Tkinter for user interaction.
- implement sympy-to-numpy conversion utilities for affine trasnfomation creation and manipulation.
- Implement sympy-to-numpy conversion utilities for SDF manipulation.
- Implement user input handling (keyboard and mouse) for camera and object control.
- Implement orbital focus point camera style for movement and interaction.
- Implement camera controls (zoom, pan, rotate) to keyboard and mouse input.
- Add support for loading and displaying SDFs using shaders and hot reload.
- Implement mesh coloring modes (individual, solid, vertex-based).
- Implement mesh degeneracy detection and visualization.
- Implement saving and loading of SDFs and meshes.
- Optimize rendering loop for performance.
- 
"""

## Imports
# Standard imports
import sys
import glfw

# Custom imports  
from utils.globals import *
from utils.log_setup import setup_logger
from utils.sysinfo import get_system_info
from utils.shaders import _create_shader_program, BASIC_VERTEX_SHADER, BASIC_FRAGMENT_SHADER
from utils.geometry_structures import *
from utils.support_function import * 
from utils.context_managers import *
from utils.opengl_interface import *
from utils.input_manager import *
from utils.robotics_contructs import *

## Debug Setup
LOGGER = setup_logger(Name = "SDF_Render_Logger") # Initialize logger
DEBUG = False # This is the flag to control the trigger of the logger # TODO: Needs to increase functionality to utilize the noraml logger escalation functions
# LOGGER_VERBOSITY = FULL # TODO: There is an actual better way to do this I dont remmeber the call at this moment
if DEBUG:
    LOGGER.info("Debug mode is ON")
    SYSINFO = get_system_info()
    for k, v in SYSINFO.items():
            if k == "Resource_Limits":
                LOGGER.info("=== Resource Limits ===")
                for limit_k, limit_v in v.items():
                    LOGGER.info(f"  {limit_k}: {limit_v}")
            else:
                LOGGER.info(f"{k}: {v}")

    # export_system_info(full_info = SYSINFO, filepath = "contexts", filename = "system_info.json")
    
if DEBUG: LOGGER.debug(f"This is a debug message from main.py")

## Data Structures
# Needed data structures that do not relate to the greater architecture or I do not believe I will reuse

## Support Functions
def _opengl_init() -> OPENGL_CONTEXT:
    """
    Initializes the OpenGL context and GLFW window.
    Returns:
        OPENGL_CONTEXT: The initialized OpenGL context
    """
    
    # Initialize GLFW
    if not glfw.init():
        LOGGER.info("Failed to initialize GLFW")
        sys.exit(-1)
    
    if DEBUG: LOGGER.debug("GLFW initialized successfully")

    # Create OpenGL context and window
    GL_Context = OPENGL_CONTEXT()
    GL_Context.Window = glfw.create_window(GL_Context.Width, GL_Context.Height, "OpenGL Window", None, None)
    
    if not GL_Context.Window:
        LOGGER.info("Failed to create GLFW window")
        glfw.terminate()
        sys.exit(-1)

    if DEBUG: LOGGER.debug("GLFW window created successfully")
    
    GL_Context.Transforms = {DEFAULT_AFFINE_PARENT: AFFINE_TRANSFORM(name = "DEFAULT_AFFINE_PARENT", # Creates the default frame whatever it is defined as in the globals.py
                                                                    parent = DEFAULT_AFFINE_PARENT),
                            "World_Frame": AFFINE_TRANSFORM(name = "World_Frame",
                                                            parent = DEFAULT_AFFINE_PARENT),
                            "Focus_Frame": AFFINE_TRANSFORM(name = "Focus_Frame",
                                                          parent = "World_Frame"),
                            "Camera_Frame": AFFINE_TRANSFORM(name = "Camera_Frame",
                                                           parent = "Focus_Frame")}

    glfw.make_context_current(GL_Context.Window)
    glViewport(0, 0, GL_Context.Width, GL_Context.Height)
    glfw.set_framebuffer_size_callback(GL_Context.Window, _framebuffer_size_callback)

    glEnable(GL_DEPTH_TEST)

    if DEBUG: LOGGER.debug("OpenGL and GLFW initialized successfully")

    return GL_Context

def _workloop(GL_Context: OPENGL_CONTEXT) -> int:
    """
    Main rendering loop
    
    Args:
    - Context (OPENGL_CONTEXT): The OpenGL context containing window and rendering information
    """
    
    # Internal Counter for debugging purposes 
    WORKLOOP_COUNTER = 0
    
    # Create a meshes
    Name = "Test_Cube"
    _load_meshes_to_context(GL_Context, name = Name, size = 1.0 ,where = "file") 

    _create_mesh_buffers(GL_Context.Meshes[Name])
    
    # Verify shader program is initialized (should be set before entering workloop)
    assert GL_Context.Shader_Program is not None, "Shader program not initialized before entering workloop"
    shader_program = GL_Context.Shader_Program  # Store for type safety and clarity
    
    # Get all uniform locations
    UNIFORM_LOCS = _get_all_uniform_locations(shader_program)
    if DEBUG:
        LOGGER.info(f"Uniform locations: {UNIFORM_LOCS}")

    # Get specific uniform locations
    #Currently these are the only 2 uniforms we use
    COLOR_LOC = UNIFORM_LOCS.get('meshColor')
    PROJ_LOC = UNIFORM_LOCS['projection']

    # Log vertex data upload
    if DEBUG:
            test_mesh = GL_Context.Meshes[Name] # TODO Need to change this if multiple meshes are used, but for now testing on the simple cube
            LOGGER.info(f"Vertex data uploaded to GPU: {test_mesh.Vertices.shape[0]} vertices, {test_mesh.Facets.size} facets")
            LOGGER.info(f"Vertex data type: {test_mesh.Vertices.dtype}, facets data type: {test_mesh.Facets.dtype}")
            LOGGER.info(f"Vertex buffer size: {test_mesh.Vertices.nbytes} bytes, facets buffer size: {test_mesh.Facets.nbytes} bytes")

    # Link vertex data to shader layout (location = 0)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)
    glBindBuffer(GL_ARRAY_BUFFER, 0)
    glEnableVertexAttribArray(0) 
    glBindVertexArray(0)
    
    while not glfw.window_should_close(GL_Context.Window):
        """
        Main rendering loop:
            1. Clear the screen
            2. Set up shaders and buffers
            3. Handle window resizing
            4. Swap buffers and poll events
            5. Update counter and log debug information
            6. Repeat until window is closed
        """
        # Process Inputs
        _get_input_events(GL_Context)

        _process_input_events(GL_Context)

        # Render
        glClearColor(*GL_Context.Background_Color)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT) # pyright: ignore

        glUseProgram(shader_program)
        glBindVertexArray(GL_Context.Meshes[Name].VAO)

        GL_Context.Width, GL_Context.Height = glfw.get_window_size(GL_Context.Window)
        GL_Context.Aspect_Ratio = np.float64(GL_Context.Width) / np.float64(GL_Context.Height)

        # Create projection matrix
        projection_matrix = _create_view_matrix(type_of_matrix = GL_Context.Projection_Mode,
                                                aspect_ratio = GL_Context.Aspect_Ratio,
                                                near =  GL_Context.Near,
                                                far = GL_Context.Far,
                                                fov = GL_Context.Fov,
                                                orbital_distance = GL_Context.Orbital_Distance) 
        if DEBUG and WORKLOOP_COUNTER == 0 :LOGGER.debug(f"View Matrix:\n{GL_Context.Projection_Mode}") # TODO: Change logger to only print when the mode changes or is first set
        
        # Set mesh color uniform based on color mode
        if GL_Context.Color_Mode == "Solid":
            if DEBUG: LOGGER.debug(f'Setting solid color uniform to: {GL_Context.Meshes[Name]}') # TODO: Change logger to only print when the mode changes or is first set
            glUniform4f(COLOR_LOC, *GL_Context.Meshes[Name].Solid_Color)
        else:
            if DEBUG: LOGGER.debug(f"Color mode {GL_Context.Color_Mode} not implemented, defaulting to solid color") # TODO: Change logger to only print when the mode changes or is first set
            glUniform4f(COLOR_LOC, *test_mesh.Solid_Color)
        
        print(f"Projection matrix diagonal: {projection_matrix.diagonal()}")

        glUniformMatrix4fv(PROJ_LOC,            # Location of the uniform
                           1,                   # Number of matrices to send
                           GL_FALSE,            # Transpose flag
                           projection_matrix.astype(np.float32, copy=False)) # Projection matrix data

        glDrawElements(GL_TRIANGLES,            # Type of geometry to draw based on the indices
                       GL_Context.Meshes[Name].Num_Facets * 3,   # Number of indices to draw
                       GL_UNSIGNED_INT, None)   # Type of indices and offset (None means start from the beginning)

        glfw.swap_buffers(GL_Context.Window) # Swap front and back buffers
        glfw.poll_events() # Poll for and process events

        # Cleanup bindings
        glBindVertexArray(0) # Unbinds the VAO for code safety
        glUseProgram(0) # Unbinds the shader program for code safety
        
        # Update counter and log debug information
        WORKLOOP_COUNTER += 1
        if DEBUG and WORKLOOP_COUNTER % 500 == 0:
            print(f"Counter: {WORKLOOP_COUNTER}, Window Size: {GL_Context.Width}x{GL_Context.Height}, Aspect Ratio: {GL_Context.Aspect_Ratio:.2f}") # TODO: Change to only print when window size changes
            print("In workloop")
                
        if WORKLOOP_COUNTER == 2000:
            WORKLOOP_COUNTER = 0

    if DEBUG: LOGGER.debug("Workloop End")

    return 0

def _save_context(GL_Context: OPENGL_CONTEXT) -> int:
    """
    Saves the current statete of Tkinter and OpenGL in case if crash or closing
    """
    
    return 0

def _opengl_terminate(GL_Context: OPENGL_CONTEXT) -> int:
    """
    Terminates the OpenGL context and GLFW
    Args:
    - CONTEXT (OPENGL_CONTEXT): The OpenGL context to terminate
    """
    glfw.terminate()
    if DEBUG: LOGGER.debug("OpenGL and GLFW terminated successfully")
    return 0

## Main
def _main() -> int:
    """ 
    Main function to initialize OpenGL context and enter the workloop
    """
    if DEBUG: LOGGER.debug("Entered main() function")

    Main_Context = _opengl_init()

    # Main_Tkinter_Context = TKINTER_CONTEXT(window_context = Main_Context)

    Main_Context.Shader_Program = _create_shader_program(BASIC_VERTEX_SHADER, BASIC_FRAGMENT_SHADER)

    if DEBUG: LOGGER.debug("initialization complete, entering main() loop...")

    if DEBUG: LOGGER.debug("About to enter working loop")
    
    # TODO: Change to run 1 workloop with 2 inner loops: an OpenGL loop and an Tkinter loop.
    """ Notes on application loop design improvements
    No idea if this is the correct way to think about it given my lack of knowledge but I 
    can imagine having 3~6 threads running once this moves to multy-threading
    
    General example:
    
      Spawn_global_state_machine
    
      while != Exit_Button_Clicked or Main_Window_Closed:
          while WORKING_ON_MAIN_WINDOW:
              Run stuff related to that window thread
              For example:
                  Load pass any new 
                  Handle mouse/keyboard input for camera movement
                  Render stuff
                  Transform stuff
                  Handle TKINTER on the main window (sliders and such)
                  Spawn new related TKINTER windows/threads:
                      Load meshfile
                      Open documentation
                      etc.
          while WORKING_ON_TKINTER_WINDOW:
              Run stuff related to the separete TKINTER thread. For example load, opening a sub window, etc etc etc
              Spawn new processing threads to:
                  Preprocess mesh for:
                      Renderable triangles
                      Compute facet area
                      Normal calculations.
                      etc.
          if Things_Need_to_Be_Procesed:
              Excecute any processing steps related to a separe state machine
              For example any pre-procesing requested
              Maybe have a max number of spawnable threads that can be spaened to process a list of requests.
                  This means a new state handler to quee and track process requests  
    
    Assuming this draft implementation is sound or at least resembles existing perfoamnce-related coding patterns
    it should be deterministic on signle thread and set us up to multy-threading later
    """
    
    # while != Main_Context_Terminated
    _workloop(Main_Context)
    # TKINTER_LOOP(Main_Tkinter_Context)
    # PROCESS_LOOP(Something_Goes_Here)

    # save state
    # _save_sate(Main_context)

    _opengl_terminate(Main_Context)
    if DEBUG: LOGGER.debug("This is the inner end of main()")
    return 0

## Entry point
if __name__ == "__main__":
    if DEBUG: LOGGER.debug("This is the outer start of main()")
    _main()
    if DEBUG: LOGGER.debug("This is the outer end of main()")
    