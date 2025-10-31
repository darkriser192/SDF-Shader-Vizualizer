# Vectorization Design Patterns for Graphics and Robotics

## Overview

This guide covers design patterns for creating functions that can handle both scalar inputs and vectorized array operations efficiently. This approach is crucial for graphics applications, robotics, and scientific computing where you need to operate on large datasets.

---

## Core Type Hint Strategy

### Basic Pattern
```python
from typing import Union
import numpy as np
import numpy.typing as npt

# Define common type aliases for clarity
ScalarFloat = float
VectorFloat = npt.NDArray[np.floating]
ScalarOrVector = Union[ScalarFloat, VectorFloat]

def transform_function(input_data: ScalarOrVector) -> ScalarOrVector:
    """Function that handles both scalars and arrays"""
    pass
```

### Extended Pattern for Multiple Parameters
```python
from typing import Union, overload
import numpy as np
import numpy.typing as npt

# Type aliases for clarity
Scalar = Union[float, int, np.floating, np.integer]
Vector1D = npt.NDArray[np.floating]
Vector3D = npt.NDArray[np.floating]  # Shape (3,) or (N, 3)
Matrix3D = npt.NDArray[np.floating]  # Shape (3, 3) or (N, 3, 3)

ScalarOrArray = Union[Scalar, npt.NDArray[np.floating]]
```

---

## Pattern 1: Angle/Scalar Vectorization

### Rotation Function Example
```python
def _rotX(X: ScalarOrArray = 0.0) -> Union[AFFINE_TRANSFORM, list[AFFINE_TRANSFORM]]:
    """
    Generate rotation(s) around X-axis
    
    Parameters:
    -----------
    X : float or array-like
        Angle(s) in radians. Can be:
        - Single float: returns single AFFINE_TRANSFORM
        - Array of floats: returns list of AFFINE_TRANSFORM objects
    """
    
    # Handle scalar case
    if np.isscalar(X):
        return _single_rotX(float(X))
    
    # Handle array case
    X_array = np.asarray(X)
    return [_single_rotX(float(angle)) for angle in X_array.flat]

def _single_rotX(angle: float) -> AFFINE_TRANSFORM:
    """Internal function for single rotation"""
    Result_Affine = AFFINE_TRANSFORM()
    Result_Affine.Name = f"X Rotation ({angle:.3f} rad)"
    Result_Affine.Rotation = np.array([
        [1,              0,               0],
        [0, np.cos(angle), -np.sin(angle)],
        [0, np.sin(angle),  np.cos(angle)]
    ])
    return Result_Affine
```

### Optimized Matrix-Only Version
```python
def rotX_matrices(X: ScalarOrArray) -> npt.NDArray[np.floating]:
    """
    Generate rotation matrices around X-axis (optimized for bulk operations)
    
    Returns:
    --------
    ndarray : shape (3, 3) or (N, 3, 3)
        Rotation matrices
    """
    X = np.asarray(X)
    scalar_input = X.ndim == 0
    
    if scalar_input:
        X = X.reshape(1)
    
    # Vectorized computation
    cos_x = np.cos(X)
    sin_x = np.sin(X)
    
    # Create batch of rotation matrices
    n = len(X)
    matrices = np.zeros((n, 3, 3))
    
    # Fill matrices vectorized
    matrices[:, 0, 0] = 1
    matrices[:, 1, 1] = cos_x
    matrices[:, 1, 2] = -sin_x  
    matrices[:, 2, 1] = sin_x
    matrices[:, 2, 2] = cos_x
    
    return matrices[0] if scalar_input else matrices
```

---

## Pattern 2: Point/Vector Transformation

### Point Cloud Rotation
```python
def rotate_points(points: npt.NDArray[np.floating], 
                 rotation_matrix: npt.NDArray[np.floating]) -> npt.NDArray[np.floating]:
    """
    Rotate point(s) by rotation matrix
    
    Parameters:
    -----------
    points : ndarray
        Points to rotate. Shape options:
        - (3,): Single 3D point
        - (N, 3): N points in 3D
        - (3, N): 3D coordinates of N points (transposed format)
    
    rotation_matrix : ndarray  
        Rotation matrix. Shape options:
        - (3, 3): Single rotation for all points
        - (N, 3, 3): Individual rotation for each point
    """
    
    points = np.asarray(points)
    rotation_matrix = np.asarray(rotation_matrix)
    
    # Handle different point formats
    if points.ndim == 1:
        # Single point (3,)
        assert points.shape[0] == 3, "Single point must be 3D"
        return rotation_matrix @ points
        
    elif points.shape[0] == 3 and points.ndim == 2:
        # Points as columns (3, N) - common in graphics
        return rotation_matrix @ points
        
    elif points.shape[1] == 3:
        # Points as rows (N, 3) - common in data science
        if rotation_matrix.ndim == 2:
            # Single rotation for all points
            return (rotation_matrix @ points.T).T
        else:
            # Individual rotations (broadcasting)
            return np.einsum('nij,nj->ni', rotation_matrix, points)
    
    else:
        raise ValueError(f"Unsupported point shape: {points.shape}")
```

### Vertex Buffer Operations
```python
def transform_vertex_buffer(vertices: npt.NDArray[np.floating],
                          transforms: Union[AFFINE_TRANSFORM, list[AFFINE_TRANSFORM]]) -> npt.NDArray[np.floating]:
    """
    Apply transformation(s) to vertex buffer data
    
    Parameters:
    -----------
    vertices : ndarray, shape (N, 3) or (N, 4)
        Vertex positions (homogeneous coordinates supported)
    transforms : AFFINE_TRANSFORM or list
        Single transform or per-vertex transforms
    """
    
    vertices = np.asarray(vertices)
    n_vertices = vertices.shape[0]
    
    # Ensure homogeneous coordinates
    if vertices.shape[1] == 3:
        ones = np.ones((n_vertices, 1))
        vertices_hom = np.hstack([vertices, ones])
    else:
        vertices_hom = vertices
    
    # Handle single transform
    if isinstance(transforms, AFFINE_TRANSFORM):
        transform_matrix = transforms.get_matrix()
        return (transform_matrix @ vertices_hom.T).T[:, :3]
    
    # Handle multiple transforms
    else:
        result = np.zeros_like(vertices_hom)
        for i, transform in enumerate(transforms):
            if i < n_vertices:
                transform_matrix = transform.get_matrix()
                result[i] = transform_matrix @ vertices_hom[i]
        
        return result[:, :3]
```

---

## Pattern 3: Conditional Processing with Overloads

### Type-Safe Overloads
```python
from typing import overload

@overload
def apply_transform(data: float, transform: AFFINE_TRANSFORM) -> float: ...

@overload 
def apply_transform(data: npt.NDArray[np.floating], transform: AFFINE_TRANSFORM) -> npt.NDArray[np.floating]: ...

@overload
def apply_transform(data: npt.NDArray[np.floating], transform: list[AFFINE_TRANSFORM]) -> npt.NDArray[np.floating]: ...

def apply_transform(data, transform):
    """
    Apply transformation with automatic type dispatch
    """
    
    if np.isscalar(data):
        # Scalar case - interpret as angle or single coordinate
        return _transform_scalar(data, transform)
        
    elif isinstance(data, np.ndarray):
        if isinstance(transform, list):
            # Array data, multiple transforms
            return _transform_array_multiple(data, transform)
        else:
            # Array data, single transform
            return _transform_array_single(data, transform)
    
    else:
        raise TypeError(f"Unsupported data type: {type(data)}")
```

---

## Pattern 4: Performance-Optimized Vectorization

### Batch Matrix Operations
```python
def compose_transforms_vectorized(
    rotations: npt.NDArray[np.floating],    # Shape (N, 3, 3)
    translations: npt.NDArray[np.floating]  # Shape (N, 3)
) -> npt.NDArray[np.floating]:              # Returns (N, 4, 4)
    """
    Vectorized composition of rotation and translation into 4x4 matrices
    """
    
    n = rotations.shape[0]
    transforms = np.zeros((n, 4, 4))
    
    # Vectorized assignment
    transforms[:, :3, :3] = rotations
    transforms[:, :3, 3] = translations  
    transforms[:, 3, 3] = 1
    
    return transforms

def batch_matrix_multiply(matrices_a: npt.NDArray[np.floating], 
                         matrices_b: npt.NDArray[np.floating]) -> npt.NDArray[np.floating]:
    """
    Batch multiply corresponding matrices
    
    Parameters:
    -----------
    matrices_a, matrices_b : ndarray, shape (N, M, K) and (N, K, P)
        Batches of matrices to multiply
    
    Returns:
    --------
    result : ndarray, shape (N, M, P)
        Batch of resulting matrices
    """
    return np.matmul(matrices_a, matrices_b)
```

---

## Pattern 5: GPU-Ready Vectorization

### Preparing Data for GPU Operations
```python
def prepare_gpu_transforms(transforms: list[AFFINE_TRANSFORM]) -> dict[str, npt.NDArray[np.floating]]:
    """
    Convert list of transforms to GPU-friendly arrays
    
    Returns:
    --------
    dict with keys:
        'matrices': (N, 4, 4) - Transform matrices
        'rotations': (N, 3, 3) - Rotation components  
        'translations': (N, 3) - Translation components
    """
    
    n = len(transforms)
    matrices = np.zeros((n, 4, 4))
    rotations = np.zeros((n, 3, 3))
    translations = np.zeros((n, 3))
    
    for i, transform in enumerate(transforms):
        matrices[i] = transform.get_matrix()
        rotations[i] = transform.Rotation
        translations[i] = transform.Translation
    
    return {
        'matrices': matrices,
        'rotations': rotations, 
        'translations': translations
    }
```

---

## Implementation Guidelines

### 1. Input Validation Pattern
```python
def validate_vectorized_input(data: ScalarOrArray, expected_shape: tuple = None) -> np.ndarray:
    """Standard input validation for vectorized functions"""
    
    # Convert to numpy array
    data_array = np.asarray(data)
    
    # Validate shape if specified
    if expected_shape is not None:
        if data_array.ndim == 0:
            # Scalar - should broadcast to expected shape
            pass
        elif data_array.shape != expected_shape:
            raise ValueError(f"Expected shape {expected_shape}, got {data_array.shape}")
    
    return data_array
```

### 2. Output Consistency Pattern
```python
def ensure_output_consistency(result: npt.NDArray, input_was_scalar: bool) -> ScalarOrArray:
    """Ensure output type matches input type (scalar in → scalar out)"""
    
    if input_was_scalar and result.ndim > 0:
        return result.item() if result.size == 1 else result[0]
    
    return result
```

### 3. Memory-Efficient Pattern
```python
def vectorized_operation_inplace(data: npt.NDArray, 
                               operation: callable,
                               chunk_size: int = 1000) -> npt.NDArray:
    """Process large arrays in chunks to manage memory"""
    
    if data.size <= chunk_size:
        return operation(data)
    
    # Process in chunks
    result = np.empty_like(data)
    for i in range(0, data.size, chunk_size):
        end_idx = min(i + chunk_size, data.size)
        result[i:end_idx] = operation(data[i:end_idx])
    
    return result
```

---

## Usage Examples

### Camera System Application
```python
# Single camera pose
single_pose = orbital_camera_transform(
    focus_params=[0, 0, 0],
    orbital_params=[np.pi/4, np.pi/6, 10.0]
)

# Multiple camera poses for animation
focus_positions = np.array([[0, 0, 0], [1, 1, 1], [2, 2, 2]])  # 3 positions
orbital_angles = np.linspace(0, 2*np.pi, 100)  # 100 frames

animation_poses = orbital_camera_transform(
    focus_params=focus_positions[0],  # Fixed focus
    orbital_params=[orbital_angles, np.pi/6, 10.0]  # Rotating azimuth
)
```

### Vertex Processing Application  
```python
# Transform single mesh
mesh_vertices = load_mesh("model.obj")  # Shape (N, 3)
transformed_vertices = transform_vertex_buffer(mesh_vertices, camera_transform)

# Transform multiple instances
instance_transforms = [
    create_transform(pos, rot) for pos, rot in zip(positions, rotations)
]
all_transformed = transform_vertex_buffer(mesh_vertices, instance_transforms)
```

---

## Performance Considerations

### Benchmarking Results (Typical)
- **Scalar operations**: No significant overhead
- **Small arrays (< 1000 elements)**: 2-5x speedup vs loops
- **Large arrays (> 10000 elements)**: 10-50x speedup vs loops
- **GPU-ready format**: Additional 2-3x speedup when uploading to GPU

### Memory Usage
- **Vectorized**: O(N) memory allocation
- **Loop-based**: O(1) memory, but slower
- **Hybrid chunking**: Balance between memory and speed

This vectorization strategy provides a clean foundation for high-performance graphics and robotics applications while maintaining code clarity and type safety.
