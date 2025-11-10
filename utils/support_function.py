## Imports
import numpy as np
from .globals import *  # For constants if needed
from .geometry_structures import AFFINE_TRANSFORM
from .context_managers import OPENGL_CONTEXT

__all__ =['_affine_transform',
          '_affine_inverse',
          '_affine_transform_delta',
          '_recursive_affine_transform',
          '_generate_fault_cube_geometry',
          '_generate_tetrahedron_geometry']

## Support Functions

def _affine_transform(LHS_Transform: AFFINE_TRANSFORM, RHS_Transform: AFFINE_TRANSFORM, Mode = "Numeric") -> AFFINE_TRANSFORM:
    """
    Multiply two AFFINE_TRANSFORM objects to get a new AFFINE_TRANSFORM object.
    Return needs to be caught by the caller.
    Args:
    - LHS_Transform (AFFINE_TRANSFORM): The starting transform
    - RHS_Transform (AFFINE_TRANSFORM): The ending transform
    - Mode (str): "Numeric" for numerical computation, "Symbolic" for symbolic computation (not implemented yet)
    Returns:
    - AFFINE_TRANSFORM: The resulting transform after multiplication
    
    # TODO: Implement symbolic mode    
    """
    # New Transform
    New_Transform = AFFINE_TRANSFORM()
    New_Transform.Rotation = np.dot(LHS_Transform.Rotation , RHS_Transform.Rotation)
    New_Transform.Translation = np.dot(LHS_Transform.Rotation , RHS_Transform.Translation) + LHS_Transform.Translation

    return New_Transform 

def _affine_inverse(Transform: AFFINE_TRANSFORM, Mode = "Numeric") -> AFFINE_TRANSFORM:
    """
    Computes the inverse of an AFFINE_TRANSFORM object.
    Return needs to be caught by the caller.
    Args:
    - transform (AFFINE_TRANSFORM): The transform to invert
    - Mode (str): "Numeric" for numerical computation, "Symbolic" for symbolic computation (not implemented yet)
    Returns
    - AFFINE_TRANSFORM: The inverted transform
    
    # TODO: Implement symbolic mode
    """
    New_Transform = AFFINE_TRANSFORM()
    # Inverse rotation is the transpose for orthogonal matrices
    New_Transform.Rotation = np.transpose(Transform.Rotation)
    # Inverse translation is -R^T * T
    New_Transform.Translation = -np.dot(New_Transform.Rotation, Transform.Translation)
    # Copy other parameters. How to handle "inverse" of scale? For now just copy
    New_Transform.Scale = Transform.Scale
    New_Transform.Name = "Inverse " + Transform.Name
    return New_Transform # Placeholder return

def _affine_transform_delta(LHS_Transform: AFFINE_TRANSFORM, RHS_Transform: AFFINE_TRANSFORM, Mode = "Numeric") -> AFFINE_TRANSFORM:
    """
    Computes the conceptual "difference" between 2 AFFINE_TRANSFORMS that are not identity. 
    Conceptually the diference between an identity transform and any trasnform should be the trasnform or its inverse
    It has the same concept as substraction in the real numbers as End - Start - Difference
    Args:
    - LHS_Transform (AFFINE_TRANSFORM): The starting transform
    - RHS_Transform (AFFINE_TRANSFORM): The ending transform
    - Mode (str): "Numeric" for numerical computation, "Symbolic" for symbolic computation (not implemented yet)
    Returns:
    - AFFINE_TRANSFORM: The resulting transform after "substraction"

    # TODO: Review thesis documents and replciate here.
    # TODO: Implement symbolic mode
    """
    # New Trasnforms
    New_Transform = AFFINE_TRANSFORM()
    
    return New_Transform

def _recursive_affine_transform(GL_Context: OPENGL_CONTEXT, Transform_ID: str, Mode = "Numeric") -> AFFINE_TRANSFORM:
    """
    Recursively computes the global AFFINE_TRANSFORM for a given Transform_ID in the context.
    Args:
    - Context (OPENGL_CONTEXT): The OpenGL context containing the transforms
    - Transform_ID (int): The ID of the transform to compute
    - Mode (str): "Numeric" for numerical computation, "Symbolic" for symbolic computation (not implemented yet)
    Returns:
    - AFFINE_TRANSFORM: The global transform
    
    # TODO: Implement symbolic mode    
    """
    Current_Transform = GL_Context.Transforms[str(Transform_ID)]
    if Current_Transform.Parent == DEFAULT_AFFINE_PARENT:
        return Current_Transform
    else:
        Parent_Transform = _recursive_affine_transform(GL_Context, Current_Transform.Parent)
        Global_Transform = _affine_transform(Parent_Transform, Current_Transform)
        return Global_Transform

def _generate_fault_cube_geometry(Size = np.float64(1.0)):
    """
    Generates a cube with vertices scaled by the given size.
    Vertices are centered at the origin, with size defining the half-length of each edge.
    Decided to leave winding as it is to debug the normals when rendering is implemented

    Args:
    - Size (float): Half-length of each edge of the cube.
    
    """
    # Vertices of a cube centered at the origin
    v0 = np.array([ 0.5,  0.5,  0.5], dtype=np.float64) # top 1 vertex num 1
    v1 = np.array([-0.5,  0.5,  0.5], dtype=np.float64) # top 2 vertex num 2
    v2 = np.array([ 0.5, -0.5,  0.5], dtype=np.float64) # top 3 vertex num 3
    v3 = np.array([-0.5, -0.5,  0.5], dtype=np.float64) # top 4 vertex num 4
    v4 = np.array([ 0.5,  0.5, -0.5], dtype=np.float64) # bottom 1 vertex num 5
    v5 = np.array([-0.5,  0.5, -0.5], dtype=np.float64) # bottom 2 vertex num 6
    v6 = np.array([ 0.5, -0.5, -0.5], dtype=np.float64) # bottom 3 vertex num 7
    v7 = np.array([-0.5, -0.5, -0.5], dtype=np.float64) # bottom 4 vertex num 8

    Vertices = np.array([v0, v1, v2, v3, v4, v5, v6, v7]) * Size
    Facets = np.array([
        [0,1,3],
        [1,3,2],
        [0,4,5],
        [5,1,0],
        [1,5,6],
        [6,3,1],
        [2,7,6],
        [7,2,3],
        [4,7,5],
        [5,0,4],
        [4,6,5],
        [5,6,7]],
        dtype = np.uint32)

    return Vertices, Facets

def _generate_tetrahedron_geometry(Size = np.float64(1.0)):
    """
    Takes a dimension and creates a tetrahedron that can be inscribed inside a sphere of radious 
    equal to the size
    """
    a = Size * np.sqrt(8/9)  # Distance from center to face centers
    b = Size * np.sqrt(2/9)  # Distance in xy-plane
    c = Size / 3             # Height offset
    
    v0 = np.array([0.0, 0.0, Size])                    # Top vertex
    v1 = np.array([a, 0.0, -c])                        # Bottom vertex 1
    v2 = np.array([-b,  np.sqrt(2/3)*Size, -c])        # Bottom vertex 2  
    v3 = np.array([-b, -np.sqrt(2/3)*Size, -c])        # Bottom vertex 3
    Vertices = np.array([v0,v1,v2,v3])
    Facets = np.array([
        [0,1,2],
        [0,2,3],
        [0,3,1],
        [1,3,2]],
        dtype = np.uint32)
    return Vertices, Facets

def _affine_to_mat(Affine_Transform: AFFINE_TRANSFORM): # Returns a 4x4 Matrix from an AFFINE_TRANSFORM object
    """
    Takes an AFFINE_TRASNFORM() and returns a 4x4 np.array object
    """
    return np.array([Affine_Transform.Rotation[0],Affine_Transform.Rotation[1],Affine_Transform.Rotation[2],Affine_Transform.Translation[0],
                     Affine_Transform.Rotation[3],Affine_Transform.Rotation[4],Affine_Transform.Rotation[5],Affine_Transform.Translation[1],
                     Affine_Transform.Rotation[6],Affine_Transform.Rotation[7],Affine_Transform.Rotation[8],Affine_Transform.Translation[2],
                                                0,                           0,                           0,Affine_Transform.Homogeneous]).reshape((4,4))

def _3D_to_1D(x_dim: int, y_dim: int, z_dim: int, 
              x_pos: int, y_pos: int, z_pos: int) -> int:
    """
    Takes a 3D position (integers) and returns a 1D index position of the flattened array
    Args:
        x_dim (int) : size of array in X
        y_dim (int) : size of array in y
        z_dim (int) : size of array in z
        x_pos (int) : position in array in X
        y_pos (int) : position in array in y
        z_pos (int) : position in array in z

    Return
        1D index position
    
    """

    return 0


## Self-Test and Module Entry Point
def _main() -> int:
    return 0

if __name__ == "__main__":
    _main()