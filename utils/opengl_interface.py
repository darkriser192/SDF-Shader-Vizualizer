## Imports
# Standard Python imports for handling basic requirements
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import numpy as np
import numpy.typing as npt
from typing import Dict, Any, TYPE_CHECKING
import tkinter as tk
from tkinter import filedialog
import trimesh
from OpenGL.GL import *  # pyright: ignore[reportWildcardImportFromLibrary]

# Custom Imports
from utils.globals import *  # For constants if needed
from utils.geometry_structures import MESH
from utils.context_managers import OPENGL_CONTEXT
from utils.support_function import _generate_fault_cube_geometry

if TYPE_CHECKING:
    from utils.context_managers import OPENGL_CONTEXT
    from utils.geometry_structures import MESH

__all__ = ['_create_orthographic_matrix',
           '_create_perspective_matrix',
           '_framebuffer_size_callback',
           '_load_meshes_to_context',
           '_create_mesh_buffers',
           '_create_view_matrix',
           '_get_all_uniform_locations']

## OpenGL Matrix Creation Functions

def _create_orthographic_matrix(aspect_ratio: float = ASPECT_RATIO) -> npt.NDArray[np.float64]:
    """
    Create an orthographic projection matrix.
    
    Args:
        aspect_ratio (float): Window aspect ratio (width/height)
        
    Returns:
        npt.NDArray[np.float64]: 4x4 orthographic projection matrix
    """
    left = -aspect_ratio
    right = aspect_ratio
    bottom = -1.0
    top = 1.0
    near = -1.0
    far = 1.0

    proj = np.array([
        [2/(right-left), 0, 0, -(right+left)/(right-left)],
        [0, 2/(top-bottom), 0, -(top+bottom)/(top-bottom)],
        [0, 0, -2/(far-near), -(far+near)/(far-near)],
        [0, 0, 0, 1]
    ], dtype=np.float64)

    return proj

def _create_perspective_matrix(fov: float = FOV, 
                              aspect_ratio: float = ASPECT_RATIO, 
                              near: float = NEAR, 
                              far: float = FAR) -> npt.NDArray[np.float64]:
    """
    Create a perspective projection matrix.
    
    Args:
        fov (float): Field of view in degrees
        aspect_ratio (float): Window aspect ratio (width/height)
        near (float): Near clipping plane distance
        far (float): Far clipping plane distance
        
    Returns:
        npt.NDArray[np.float32]: 4x4 perspective projection matrix
    """
    f = 1.0 / np.tan(np.radians(fov) / 2.0)
    proj = np.array([
        [f/aspect_ratio, 0, 0, 0],
        [0, f, 0, 0], 
        [0, 0, (far+near)/(near-far), (2*far*near)/(near-far)],
        [0, 0, -1, 0]
    ], dtype=np.float64)
    
    return proj    

## OpenGL Callback Functions

def _framebuffer_size_callback(window: Any, width: int, height: int) -> None:
    """
    GLFW callback function for framebuffer resize events.
    
    Adjusts the OpenGL viewport to the new window size and ensures
    proper depth testing is enabled.
    
    Args:
        window (Any): GLFW window handle
        width (int): New framebuffer width in pixels
        height (int): New framebuffer height in pixels
    """
    # Adjust the OpenGL viewport to the new window size
    glViewport(0, 0, width, height)
    glEnable(GL_DEPTH_TEST)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT) # pyright: ignore
    
## Mesh Management Functions

def _load_meshes_to_context(gl_context: "OPENGL_CONTEXT", name: str, where: str = "test" ) -> None:
    """
    Load default meshes into the OpenGL context.
    
    Creates a test cube mesh and stores it in the context's mesh dictionary.
    This function serves as a placeholder for future mesh loading capabilities.
    
    Args:
        gl_context (OPENGL_CONTEXT): The OpenGL context to load meshes into
        
    Notes:
        Currently creates only a single test cube. Future versions will support
        loading meshes from files and other sources.
        
    TODO:
        - Implement mesh loading from files
        - Add support for multiple mesh formats
        - Add tkinter file explorer functionality to search for and load meshes
        - If "where" = "test" then use the test cube, if "file" use tkinter
        - Add mesh validation and error handling

    """
    New_MESH = MESH()

    if where == "test":
        cube_mesh_Vertices, cube_mesh_Facets = _generate_fault_cube_geometry(Size = np.float64(0.75))
        New_MESH.Name = name
        New_MESH.Parent = gl_context.Transforms["World_Frame"].Name
        New_MESH.Vertices = cube_mesh_Vertices
        New_MESH.Facets= cube_mesh_Facets
        gl_context.Meshes[New_MESH.Name] = New_MESH

    else:
                # Create hidden root window
        root = tk.Tk()
        root.withdraw()
        
        # Get file path
        STL_address = filedialog.askopenfilename(
            title= "Select STL file",
            filetypes=[("STL files", "*.stl"), ("All files", "*.*")]
        )
        Trimesh_geometry = trimesh.load_mesh(STL_address, file_type='stl')
        New_MESH.Name = name
        New_MESH.Parent = gl_context.Transforms["World_Frame"].Name
        New_MESH.Vertices = Trimesh_geometry.vertices
        New_MESH.Facets = Trimesh_geometry.faces.astype(np.uint32)  # Convert to uint32
        gl_context.Meshes[New_MESH.Name] = New_MESH
        
        root.destroy()

def _create_mesh_buffers(mesh: MESH) -> None:
    """
    Create OpenGL buffers (VAO, VBO, EBO) for a given mesh.
    
    Sets up vertex array object, vertex buffer object, and element buffer object
    for efficient GPU rendering. Also configures vertex attribute pointers.
    
    Args:
        mesh (MESH): The mesh object containing vertices and facets
        
    Returns:
        Tuple[int, int, int]: A tuple containing (VAO, VBO, EBO) buffer IDs
        
    Notes:
        - Vertices are uploaded as float32 for GPU compatibility
        - Facets remain as uint32 for index buffering
        - Vertex attributes are configured for location 0 (position)
        - Buffers are unbound after creation for safety
    """
    # Create and bind Vertex Array Object
    vao = glGenVertexArrays(1)
    glBindVertexArray(vao)

    # Create and setup Vertex Buffer Object
    vbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(
        GL_ARRAY_BUFFER,
        mesh.Vertices.astype(np.float32, copy=False).nbytes,
        mesh.Vertices.astype(np.float32, copy=False),
        GL_STATIC_DRAW
    )

    # Create and setup Element Buffer Object
    ebo = glGenBuffers(1)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo)
    glBufferData(
        GL_ELEMENT_ARRAY_BUFFER, 
        mesh.Facets.nbytes, 
        mesh.Facets, 
        GL_STATIC_DRAW
    )

    # Configure vertex attribute pointers
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)
    glEnableVertexAttribArray(0)

    # Unbind buffers for safety
    glBindBuffer(GL_ARRAY_BUFFER, 0)
    glBindVertexArray(0)
    
    # Store buffer IDs in mesh object for later reference
    mesh.VAO = vao
    mesh.VBO = vbo
    mesh.EBO = ebo

## View Matrix and Projection Functions

def _create_view_matrix(gl_context: OPENGL_CONTEXT) -> npt.NDArray[np.float32]:
    """
    Create a projection matrix based on the context's current projection mode.
    
    Selects between orthographic and perspective projection based on the
    context's Projection_Mode setting. Falls back to orthographic if mode
    is unrecognized.
    
    Args:
        gl_context (OPENGL_CONTEXT): The OpenGL context containing projection parameters
        
    Returns:
        npt.NDArray[np.float32]: 4x4 projection matrix
        
    Notes:
        - Orthographic mode uses current aspect ratio
        - Perspective mode uses FOV, aspect ratio, near, and far planes
        - Unknown modes default to orthographic projection
    """
    if gl_context.Projection_Mode == ORTHOGRAPHIC_MODE:
        projection_matrix = _create_orthographic_matrix(aspect_ratio=gl_context.Aspect_Ratio)
    elif gl_context.Projection_Mode == PERSPECTIVE_MODE:
        projection_matrix = _create_perspective_matrix(
            fov=gl_context.FOV,
            aspect_ratio=gl_context.Aspect_Ratio, 
            near=gl_context.Near, 
            far=gl_context.Far
        )
    else:
        # Default to orthographic for unknown modes
        projection_matrix = _create_orthographic_matrix(aspect_ratio=gl_context.Aspect_Ratio)

    return projection_matrix.astype(np.float32)

## Shader Uniform Management Functions

def _get_all_uniform_locations(shader_program: int) -> Dict[str, int]:
    """
    Retrieve all uniform locations from an OpenGL shader program.
    
    Queries the shader program for all active uniforms and returns a dictionary
    mapping uniform names to their OpenGL location IDs.
    
    Args:
        shader_program (int): The OpenGL shader program ID
        
    Returns:
        Dict[str, int]: Dictionary mapping uniform names to location IDs
        
    Notes:
        - Handles various string encoding formats from OpenGL
        - Strips null characters from uniform names
        - Returns empty dict if no uniforms found
    """
    num_uniforms = glGetProgramiv(shader_program, GL_ACTIVE_UNIFORMS)
    uniform_locations: Dict[str, int] = {}
    
    for i in range(num_uniforms):
        name, size, type_ = glGetActiveUniform(shader_program, i)
        
        # Convert name to proper string handling various OpenGL return formats
        if hasattr(name, 'tobytes'):
            name_str = name.tobytes().decode('utf-8').rstrip('\x00')
        elif isinstance(name, bytes):
            name_str = name.decode('utf-8').rstrip('\x00')
        elif hasattr(name, 'decode'):
            name_str = name.decode('utf-8').rstrip('\x00')
        else:
            # Already a string
            name_str = str(name).rstrip('\x00')
        
        location = glGetUniformLocation(shader_program, name_str)
        uniform_locations[name_str] = location
        
    return uniform_locations

## Self-Test and Module Entry Point

def _self_test() -> bool:
    """
    Basic self-test for OpenGL interface functionality.
    
    Returns:
        bool: True if all tests pass, False otherwise
        
    Notes:
        Does not require OpenGL context, only tests matrix generation.
    """
    try:
        # Test matrix generation functions
        ortho_matrix = _create_orthographic_matrix()
        assert ortho_matrix.shape == (4, 4)
        
        persp_matrix = _create_perspective_matrix()
        assert persp_matrix.shape == (4, 4)
        
        # Test that matrices are different
        assert not np.allclose(ortho_matrix, persp_matrix)
        
        return True
    except Exception as e:
        print(f"OpenGL interface self-test failed: {e}")
        return False


def _main() -> int:
    """
    Module entry point for testing OpenGL interface.
    
    Returns:
        int: Exit code (0 for success)
    """
    return 0

if __name__ == "__main__":
    _main()
