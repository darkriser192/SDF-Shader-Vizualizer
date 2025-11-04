## Imports
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import glfw
from utils.globals import *
from utils.context_managers import OPENGL_CONTEXT, TKINTER_CONTEXT

__all__ = ['_get_input_events',
           '_change_color_mode',
           '_process_input_events',
           '_process_tkinter_events']

def _get_input_events(GL_Context: OPENGL_CONTEXT):
    """
    Polls for input events and updates the context's key states.
    
    Args:
        Context (OPENGL_CONTEXT): The OpenGL context to update key states for.
    """
    # Poll for events
    glfw.poll_events()
    
    # Update key states
    #for key_name in Context.Keys.keys():
    prev = GL_Context.Keys['W'] 
    GL_Context.Keys['W'] = glfw.get_key(GL_Context.Window, glfw.KEY_W) == glfw.PRESS
    GL_Context.Keys['W_FLAG'] = (GL_Context.Keys['W'] != prev)

    prev = GL_Context.Keys['A']
    GL_Context.Keys['A'] = glfw.get_key(GL_Context.Window, glfw.KEY_A) == glfw.PRESS
    GL_Context.Keys['A_FLAG'] = (GL_Context.Keys['A'] != prev)

    prev = GL_Context.Keys['S'] 
    GL_Context.Keys['S'] = glfw.get_key(GL_Context.Window, glfw.KEY_S) == glfw.PRESS
    GL_Context.Keys['S_FLAG'] = (GL_Context.Keys['S'] != prev)
    
    prev = GL_Context.Keys['D'] 
    GL_Context.Keys['D'] = glfw.get_key(GL_Context.Window, glfw.KEY_D) == glfw.PRESS
    GL_Context.Keys['D_FLAG'] = (GL_Context.Keys['D'] != prev)

    prev = GL_Context.Keys['Q'] 
    GL_Context.Keys['Q'] = glfw.get_key(GL_Context.Window, glfw.KEY_Q) == glfw.PRESS
    GL_Context.Keys['Q_FLAG'] = (GL_Context.Keys['Q'] != prev)

    prev = GL_Context.Keys['E'] 
    GL_Context.Keys['E'] = glfw.get_key(GL_Context.Window, glfw.KEY_E) == glfw.PRESS
    GL_Context.Keys['E_FLAG'] = (GL_Context.Keys['E'] != prev)

    prev = GL_Context.Keys['UP'] 
    GL_Context.Keys['UP'] = glfw.get_key(GL_Context.Window, glfw.KEY_UP) == glfw.PRESS
    GL_Context.Keys['UP_FLAG'] = (GL_Context.Keys['UP'] != prev)

    prev = GL_Context.Keys['DOWN'] 
    GL_Context.Keys['DOWN'] = glfw.get_key(GL_Context.Window, glfw.KEY_DOWN) == glfw.PRESS
    GL_Context.Keys['DOWN_FLAG'] = (GL_Context.Keys['DOWN'] != prev)

    prev = GL_Context.Keys['LEFT'] 
    GL_Context.Keys['LEFT'] = glfw.get_key(GL_Context.Window, glfw.KEY_LEFT) == glfw.PRESS
    GL_Context.Keys['LEFT_FLAG'] = (GL_Context.Keys['LEFT'] != prev)

    prev = GL_Context.Keys['RIGHT'] 
    GL_Context.Keys['RIGHT'] = glfw.get_key(GL_Context.Window, glfw.KEY_RIGHT) == glfw.PRESS
    GL_Context.Keys['RIGHT_FLAG'] = (GL_Context.Keys['RIGHT'] != prev)

    prev = GL_Context.Keys['PAGE_UP'] 
    GL_Context.Keys['PAGE_UP'] = glfw.get_key(GL_Context.Window, glfw.KEY_PAGE_UP) == glfw.PRESS
    GL_Context.Keys['PAGE_UP_FLAG'] = (GL_Context.Keys['PAGE_UP'] != prev)

    prev = GL_Context.Keys['PAGE_DOWN'] 
    GL_Context.Keys['PAGE_DOWN'] = glfw.get_key(GL_Context.Window, glfw.KEY_PAGE_DOWN) == glfw.PRESS
    GL_Context.Keys['PAGE_DOWN_FLAG'] = (GL_Context.Keys['PAGE_DOWN'] != prev)

    prev = GL_Context.Keys['SHIFT'] 
    GL_Context.Keys['SHIFT'] = glfw.get_key(GL_Context.Window, glfw.KEY_LEFT_SHIFT) == glfw.PRESS or glfw.get_key(GL_Context.Window, glfw.KEY_RIGHT_SHIFT) == glfw.PRESS
    GL_Context.Keys['SHIFT_FLAG'] = (GL_Context.Keys['SHIFT'] != prev)
    
    prev = GL_Context.Keys['CTRL'] 
    GL_Context.Keys['CTRL'] = glfw.get_key(GL_Context.Window, glfw.KEY_LEFT_CONTROL) == glfw.PRESS or glfw.get_key(GL_Context.Window, glfw.KEY_RIGHT_CONTROL) == glfw.PRESS
    GL_Context.Keys['CTRL_FLAG'] = (GL_Context.Keys['CTRL'] != prev)

    prev = GL_Context.Keys['ALT'] 
    GL_Context.Keys['ALT'] = glfw.get_key(GL_Context.Window, glfw.KEY_LEFT_ALT) == glfw.PRESS or glfw.get_key(GL_Context.Window, glfw.KEY_RIGHT_ALT) == glfw.PRESS
    GL_Context.Keys['ALT_FLAG'] = (GL_Context.Keys['ALT'] != prev)

    prev = GL_Context.Keys['SPACE'] 
    GL_Context.Keys['SPACE'] = glfw.get_key(GL_Context.Window, glfw.KEY_SPACE) == glfw.PRESS
    GL_Context.Keys['SPACE_FLAG'] = (GL_Context.Keys['SPACE'] != prev)

    prev = GL_Context.Keys['ESCAPE'] 
    GL_Context.Keys['ESCAPE'] = glfw.get_key(GL_Context.Window, glfw.KEY_ESCAPE) == glfw.PRESS
    GL_Context.Keys['ESCAPE_FLAG'] = (GL_Context.Keys['ESCAPE'] != prev)
    
    prev = GL_Context.Keys['MOUSE_LEFT'] 
    GL_Context.Keys['MOUSE_LEFT'] = glfw.get_mouse_button(GL_Context.Window, glfw.MOUSE_BUTTON_LEFT) == glfw.PRESS
    GL_Context.Keys['MOUSE_LEFT_FLAG'] = (GL_Context.Keys['MOUSE_LEFT'] != prev)

    prev = GL_Context.Keys['MOUSE_RIGHT'] 
    GL_Context.Keys['MOUSE_RIGHT'] = glfw.get_mouse_button(GL_Context.Window, glfw.MOUSE_BUTTON_RIGHT) == glfw.PRESS
    GL_Context.Keys['MOUSE_RIGHT_FLAG'] = (GL_Context.Keys['MOUSE_RIGHT'] != prev)

    GL_Context.Keys['LAST_MOUSE_X'] = GL_Context.Keys['MOUSE_X']
    GL_Context.Keys['LAST_MOUSE_Y'] = GL_Context.Keys['MOUSE_Y']
    GL_Context.Keys['MOUSE_X'], GL_Context.Keys['MOUSE_Y']  = glfw.get_cursor_pos(GL_Context.Window)
    GL_Context.Keys['MOUSE_X_DIR'] = GL_Context.Keys['MOUSE_X'] - GL_Context.Keys['LAST_MOUSE_X']
    GL_Context.Keys['MOUSE_Y_DIR'] = GL_Context.Keys['MOUSE_Y'] - GL_Context.Keys['LAST_MOUSE_Y']

    prev = GL_Context.Keys['+'] 
    GL_Context.Keys['+'] = glfw.get_key(GL_Context.Window, glfw.KEY_KP_ADD) == glfw.PRESS
    GL_Context.Keys['+_FLAG'] = (GL_Context.Keys['+'] != prev)

    prev = GL_Context.Keys['-'] 
    GL_Context.Keys['-'] = glfw.get_key(GL_Context.Window, glfw.KEY_KP_SUBTRACT) == glfw.PRESS
    GL_Context.Keys['-_FLAG'] = (GL_Context.Keys['-'] != prev)

    # Make sure to add all keys defined in the KEYS dictionary. Very important for future expansion
    # I recognize this is slower to maintain, but in the same breadth this should be a faster update than a loop? 
    # I need to see if a Map, a Numpy Array, or Pandas function.
    # Porbably a good idea to write a back of the envelop calculation of the compute overhead here

def _change_color_mode(GL_Context: OPENGL_CONTEXT):
    """
    Changes the render mode of the context window
    """
    # TODO: Implement the process of the color mode
    if GL_Context.Color_Mode == "Solid":
        GL_Context.Color_Mode == "Wire_Frame"  # pyright: ignore 
    
    pass

def _process_input_events(GL_Context: OPENGL_CONTEXT):
    """
    Processes input events and updates the context's key states.
    
    Args:
        Context (OPENGL_CONTEXT): The OpenGL context to process input for.
    """

    # Individual input processing can be added here
    # TODO: Find better ways to check for conditions, crate a function containing all these checks?
    # Camera movement
    # +/- as proxies for scroll wheel movement
    # Use your existing flag system for "just pressed" events

    if GL_Context.Keys['MOUSE_RIGHT'] and GL_Context.Keys['SHIFT']:
            print(f"Position in: {GL_Context.Keys['MOUSE_X']} , {GL_Context.Keys['MOUSE_Y']}")

    if GL_Context.Keys['MOUSE_LEFT'] and GL_Context.Keys['CTRL']:
        print(f"direction in: {GL_Context.Keys['MOUSE_X_DIR']} , {GL_Context.Keys['MOUSE_Y_DIR']}")

    if GL_Context.Keys['+_FLAG'] and GL_Context.Keys['+'] and GL_Context.Orbital_Distance < 100: 
        GL_Context.Orbital_Distance += CAMERA_STEP_SIZE
        print(f"Zoom Out: {GL_Context.Orbital_Distance}")

    if GL_Context.Keys['-_FLAG'] and GL_Context.Keys['-'] and GL_Context.Orbital_Distance > 0.5: 
        GL_Context.Orbital_Distance -= CAMERA_STEP_SIZE
        print(f"Zoom In: {GL_Context.Orbital_Distance}")
        
    return 0

def _process_tkinter_events(Tkinter_Context: TKINTER_CONTEXT):
    # TODO: Implement

    """
    Process all tkinter relevant events like:
        Reading SDF shader file
        Update GUI linked uniforms
        What else is a good idea?
    
    """

    # Clear the Dirty Flag, False means nothing to update
    Tkinter_Context.Dirty_Flag = False
    return 0

## Self-Test and Module Entry Point
def _main() -> int:
    """
    Module entry point for testing geometry structures.
    
    Returns:
        int: Exit code (0 for success)
    """

    return 0

if __name__ == "__main__":
    _main()