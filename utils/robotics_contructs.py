## Imports
# Standard Imports
from typing import Union
import numpy.typing as npt

# Custom Imports
from .globals import *
from .geometry_structures import *
from .support_function import *

## Import control
__all__ =[]

## Local global variables



## Data Clases





## Support Functions
## General Utilities

def translateXYZ(x_coord: float = 0.0, 
                 y_coord: float = 0.0, 
                 z_coord: float = 0.0,
                 Temp_Trasnform: AFFINE_TRANSFORM = AFFINE_TRANSFORM()) -> AFFINE_TRANSFORM:
    """
    Returns an affine transform representing a finite trasnlation
    """


    return AFFINE_TRANSFORM()

def _rotX(angle: Union[float, npt.NDArray[np.float64]] = 0.0, 
          Temp_Trasnform: AFFINE_TRANSFORM = AFFINE_TRANSFORM()) -> AFFINE_TRANSFORM:
    """
    Generated an affine TRANSFORM representing a rotation around X axis
    """

    Temp_Trasnform.Name = "An X Rotation"
    Temp_Trasnform.Parent = "None"
    Temp_Trasnform.Child = "None"
    Temp_Trasnform.Rotation = np.array([[ 1,             0,              0],
                                        [0, np.cos(angle), -np.sin(angle)],
                                        [0, np.sin(angle),  np.cos(angle)]], dtype=np.float64)

    return Temp_Trasnform

def _rotY(angle: Union[float, npt.NDArray[np.float64]] = 0.0,
          Temp_Trasnform: AFFINE_TRANSFORM = AFFINE_TRANSFORM()) -> AFFINE_TRANSFORM: 
    """
    Generated an affine TRANSFORM representing a rotation around Y axis
    """
    Temp_Trasnform.Name = "A Y Rotation"
    Temp_Trasnform.Parent = "None"
    Temp_Trasnform.Child = "None"
    Temp_Trasnform.Rotation = np.array([[  np.cos(angle),         0, np.sin(angle)],
                                        [             0,         1,             0],
                                        [-np.sin(angle),         0, np.cos(angle)]], dtype=np.float64)

    return Temp_Trasnform

def _rotZ(angle: Union[float, npt.NDArray[np.float64]] = 0.0, 
          Temp_Trasnform: AFFINE_TRANSFORM = AFFINE_TRANSFORM()) -> AFFINE_TRANSFORM: 
    """
    Generated an affine TRANSFORM representing a rotation around Z axis
    """

    Temp_Trasnform.Name = "A Z Rotation"
    Temp_Trasnform.Parent = "None"
    Temp_Trasnform.Child = "None"
    Temp_Trasnform.Rotation = np.array([[ np.cos(angle), -np.sin(angle), 0],
                                        [np.sin(angle),  np.cos(angle), 0],
                                        [            0,              0, 1]], dtype=np.float64)

    return Temp_Trasnform

def _rotVect(w_vect = (0.0, 0.0, 1.0), angle = 0,
             Temp_Trasnform: AFFINE_TRANSFORM = AFFINE_TRANSFORM()) -> AFFINE_TRANSFORM:
    """
    Generate rotation around arbitrary vector using explicit Rodrigues formula
    
    Parameters:
    -----------
    w_vect : tuple or array-like, shape (3,)
        Rotation axis vector (will be normalized)
    angle : float
        Rotation angle in radians
        
    Returns:
    --------
    AFFINE_TRANSFORM with rotation matrix using explicit Rodrigues components
    """
    
    Temp_Trasnform.Name = f"Vector Rotation ({angle:.3f} rad)"
    Temp_Trasnform.Parent = "None"
    Temp_Trasnform.Child = "None"
    
    # Convert to numpy and normalize the axis vector
    w = np.array(w_vect, dtype=np.float64)
    w_norm = np.linalg.norm(w)
    
    # Handle zero vector case
    if w_norm < F64EPS:
        Temp_Trasnform.Rotation = np.eye(3)
        return Temp_Trasnform
    
    w = w / w_norm  # Normalize to unit vector
    w1, w2, w3 = w[0], w[1], w[2]
    
    # Handle zero angle case
    if abs(angle) < F64EPS:
        Temp_Trasnform.Rotation = np.eye(3)
        return Temp_Trasnform
    
    # Precompute trigonometric terms
    c_theta = np.cos(angle)
    s_theta = np.sin(angle)
    one_minus_c = 1 - c_theta
    
    # Explicit Rodrigues formula components
    Temp_Trasnform.Rotation = np.array([
        [c_theta + w1*w1*one_minus_c,    w1*w2*one_minus_c - w3*s_theta,  w1*w3*one_minus_c + w2*s_theta],
        [w1*w2*one_minus_c + w3*s_theta, c_theta + w2*w2*one_minus_c,    w2*w3*one_minus_c - w1*s_theta], 
        [w1*w3*one_minus_c - w2*s_theta, w2*w3*one_minus_c + w1*s_theta, c_theta + w3*w3*one_minus_c   ]
    ], dtype=np.float64)
    
    return Temp_Trasnform

def _rodriguez_formula(w_vect = (0.0, 0.0, 1.0), angle = 0,
                       Temp_Trasnform: AFFINE_TRANSFORM = AFFINE_TRANSFORM()) -> AFFINE_TRANSFORM:
    """
    Generate rotation around arbitrary vector using Rodrigues formula
    
    Parameters:
    -----------
    w_vect : tuple or array-like, shape (3,)
        Rotation axis vector (will be normalized)
    angle : float
        Rotation angle in radians
        
    Returns:
    --------
    AFFINE_TRANSFORM with rotation matrix R = I + sin(θ)[w]× + (1-cos(θ))[w]×²
    """
    
    Temp_Trasnform.Name = f"Vector Rotation ({angle:.3f} rad)"
    Temp_Trasnform.Parent = "None"
    Temp_Trasnform.Child = "None"
    
    # Convert to numpy and normalize the axis vector
    w = np.array(w_vect, dtype=np.float64)
    w_norm = np.linalg.norm(w)
    
    # Handle zero vector case
    if w_norm < 1e-10:
        Temp_Trasnform.Rotation = np.eye(3)
        return Temp_Trasnform
    
    w = w / w_norm  # Normalize to unit vector
    
    # Handle zero angle case
    if abs(angle) < 1e-10:
        Temp_Trasnform.Rotation = np.eye(3)
        return Temp_Trasnform
    
    # Rodrigues formula: R = I + sin(θ)[w]× + (1-cos(θ))[w]×²
    
    # Create skew-symmetric matrix [w]×
    w_skew = np.array([[    0, -w[2],  w[1]],
                       [ w[2],     0, -w[0]],
                       [-w[1],  w[0],     0]], dtype=np.float64)
    
    # Calculate trigonometric terms
    sin_angle = np.sin(angle)
    cos_angle = np.cos(angle)
    
    # Rodrigues formula
    I = np.eye(3)
    w_skew_squared = w_skew @ w_skew
    
    Temp_Trasnform.Rotation = I + sin_angle * w_skew + (1 - cos_angle) * w_skew_squared
    
    return Temp_Trasnform

def _affine_det(Affine_Transform: AFFINE_TRANSFORM) -> float:
    """
    Returns the simplified determinant of a 4x4 affine transformation matrix
    
    For affine transforms, det(4x4) = det(3x3 rotation part) since:
    |R t|
    |0 1| = det(R)
    """
    return np.linalg.det(Affine_Transform.Rotation)

def _skew2vect(skew_matrix):
    """
    Converts from a skew symmetric matrix to a 3x1 vector
    
    Extracts [x, y, z] from:
    [[ 0, -z,  y],
     [ z,  0, -x], 
     [-y,  x,  0]]
    """
    skew_matrix = np.asarray(skew_matrix)
    
    return np.array([
        skew_matrix[2, 1],  # x component
        skew_matrix[0, 2],  # y component  
        skew_matrix[1, 0]   # z component
    ], dtype=np.float64)

def _vect2skew(vector):
    """
    Converts from a 3x1 vector to a skew symmetric matrix
    
    Creates skew-symmetric matrix from [x, y, z]:
    [[ 0, -z,  y],
     [ z,  0, -x],
     [-y,  x,  0]]
    """
    vector = np.asarray(vector)
    x, y, z = vector[0], vector[1], vector[2]
    
    return np.array([
        [ 0, -z,  y],
        [ z,  0, -x],
        [-y,  x,  0]
    ], dtype=np.float64)

def validate_rotation_matrix(affine_transform: AFFINE_TRANSFORM, tolerance = F64EPS) -> bool:
    """Check if rotation matrix is proper"""
    det_value = _affine_det(affine_transform)
    return abs(det_value - 1.0) < tolerance

def check_transform_type(affine_transform: AFFINE_TRANSFORM) -> str:
    """Classify the transformation type"""
    det_value = _affine_det(affine_transform)
    
    if abs(det_value - 1.0) < F64EPS:
        return "Proper rotation"
    elif abs(det_value + 1.0) < F64EPS:
        return "Improper rotation (with reflection)"
    else:
        return f"Scaled transformation (det = {det_value})"

## D-H Utilities

def dh_chain_to_affine(dh_params: np.ndarray) -> tuple[AFFINE_TRANSFORM, list]:
    """
    Compute the final transformation matrix from a sequence of DH parameters.

    Parameters:
        dh_params (np.ndarray): Nx4 array, each row is [theta, d, a, alpha] for a joint (in radians/meters).

    Returns:
        final_transform (AFFINE_TRANSFORM): The resulting transform from base to end-effector.
        transforms_list (list): List of AFFINE_TRANSFORM for each joint (cumulative).
    """
    N = dh_params.shape[0]
    transforms_list = []
    T = np.eye(4)

    for i in range(N):
        theta, d, a, alpha = dh_params[i]
        # DH transformation for one joint
        ct, st = np.cos(theta), np.sin(theta)
        ca, sa = np.cos(alpha), np.sin(alpha)
        T_i = np.array([
            [ct, -st*ca,  st*sa, a*ct],
            [st,  ct*ca, -ct*sa, a*st],
            [0,      sa,     ca,    d],
            [0,       0,      0,    1]
        ], dtype=np.float64)
        T = T @ T_i
        # Store as AFFINE_TRANSFORM
        aff = AFFINE_TRANSFORM()
        aff.Rotation = T[:3, :3]
        aff.Translation = T[:3, 3]
        aff.Name = f"Joint_{i+1}"
        transforms_list.append(aff)

    # Final transform
    final_affine = AFFINE_TRANSFORM()
    final_affine.Rotation = T[:3, :3]
    final_affine.Translation = T[:3, 3]
    final_affine.Name = "EndEffector"

    return final_affine, transforms_list


## Screw Vector Utilities






## Self-Test and Module Entry Point

def _self_test() -> bool:
    """
    Basic self-test for robotic concepts functionality
    
    Returns:
        bool: True if all tests pass, False otherwise
        
    Notes:
        
    """

    return False # Not implemented

def _main() -> int:
    """
    Module entry point for testing robotic concepts.
    
    Returns:
        int: Exit code (0 for success)
    """

    return 0

if __name__ == "__main__":
    _main()
