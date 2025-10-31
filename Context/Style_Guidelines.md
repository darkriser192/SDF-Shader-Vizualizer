# Play Project - Style Guidelines & Code Standards

## Document Purpose
This document establishes coding standards, naming conventions, and architectural patterns for the Play SDF visualizer project. It serves as a reference for maintaining consistency across development sessions and context transfers.

---

## 1. Naming Conventions

### Function Naming
- **Private functions**: Use `_function_name` (lowercase with underscores)
- **Public functions**: Use `function_name` (lowercase with underscores)
- **Consistency**: Avoid mixed case like `_Create_mesh_buffers` → use `_create_mesh_buffers`

### Variable Naming
- **Constants**: ALL_CAPS with underscores (`WINDOW_WIDTH`, `TARGET_FPS`)
- **Local variables**: lowercase_with_underscores (`workloop_counter`, `projection_matrix`)
- **Class attributes**: PascalCase (`GL_Context.Width`, `GL_Context.Height`)

### Dictionary Keys
- **Mesh storage**: Use underscores consistently (`"Test_Cube"` not `"Test Cube"`)
- **Transform storage**: Use descriptive keys (`"Canonical_Frame"` not `"Cannonical_Frame"`)
- **Frame notation**: Use mathematical notation (`"T_E_Fp"` for Transform Canonical→Focus)

### File and Module Naming
- **Module files**: lowercase_with_underscores (`opengl_interface.py`, `geometry_structures.py`)
- **Class names**: SCREAMING_SNAKE_CASE for data structures (`OPENGL_CONTEXT`, `AFFINE_TRANSFORM`)

---

## 2. Constants Formalization

### Required Constants (to be added to globals.py)
```python
# Buffer Management
DEFAULT_MESH_SIZE = 250000
INVALID_BUFFER_ID = -1
CANONICAL_FRAME_ID = -1

# Transform Identity Constants
IDENTITY_TRANSLATION = np.array([0.0, 0.0, 0.0])
IDENTITY_ROTATION = np.eye(3)
IDENTITY_SCALE = np.array([1.0, 1.0, 1.0])

# Frame Name Constants
CANONICAL_FRAME = "Canonical_Frame"
WORLD_FRAME = "World_Frame"
FOCUS_FRAME = "Focus_Frame"
CAMERA_FRAME = "Camera_Frame"

# Projection Mode Constants
ORTHOGRAPHIC_MODE = "Orthographic"
PERSPECTIVE_MODE = "Perspective"

# Color Mode Constants
SOLID_COLOR_MODE = "Solid"
VERTEX_COLOR_MODE = "Vertex"
NORMAL_COLOR_MODE = "Normal"
```

### Eliminate Magic Numbers
- Replace `1.0` with named constants like `DEFAULT_CUBE_SIZE`
- Replace `0.75` with `DEFAULT_TETRAHEDRON_SIZE`
- Replace hardcoded array sizes with `DEFAULT_MESH_SIZE`

---

## 3. Type Hints Standards

### Required Imports
```python
from typing import Optional, Dict, List, Tuple, Callable, Any
import numpy.typing as npt
```

### Function Signatures
```python
def _create_mesh_buffers(mesh: MESH) -> Tuple[int, int, int]:
    """Create OpenGL buffers for a given mesh."""
    
def _create_view_matrix(context: OPENGL_CONTEXT) -> npt.NDArray[np.float32]:
    """Create view matrix based on context parameters."""
    
def _load_meshes_to_context(context: OPENGL_CONTEXT) -> None:
    """Load meshes into the OpenGL context."""
```

### Class Type Hints
```python
class OPENGL_CONTEXT:
    Width: int
    Height: int
    Aspect_Ratio: float
    Meshes: Dict[str, MESH]
    Transforms: Dict[str, AFFINE_TRANSFORM]
    Shader_Program: Optional[int]
```

---

## 4. Documentation Standards

### Function Documentation Template
```python
def function_name(param1: Type1, param2: Type2) -> ReturnType:
    """
    Brief description of what the function does.
    
    Args:
        param1 (Type1): Description of parameter 1
        param2 (Type2): Description of parameter 2
    
    Returns:
        ReturnType: Description of return value
        
    Raises:
        ExceptionType: When this exception is raised
        
    Notes:
        Additional implementation details or mathematical context
    """
```

### Module Documentation
- **File header**: Project context, author, requirements
- **Section headers**: Clear separation with `##` for major sections
- **TODO format**: Consistent format with priority levels

### Inline Comments
- **Above complex logic**: Explain the "why" not the "what"
- **TODO comments**: Include priority and context
- **Math comments**: Reference equations, coordinate systems, conventions

---

## 5. Frame/Transform Notation System

### Mathematical Frame Notation
- **Canonical Frame**: `{E}` (E-Frame, identity)
- **World Frame**: `{W}` (World-Frame)
- **Focus Frame**: `{Fp}` (Focus-Point-Frame)
- **Camera Frame**: `{C}` (Camera-Frame)

### Transform Notation
- **Transform syntax**: `T_A_B` means "Transform from Frame A to Frame B"
- **Dictionary keys**: Use this notation (`"T_E_Fp"`, `"T_Fp_C"`)
- **Comments**: Reference frames in documentation

### Transform Hierarchy
```
{E} Canonical Frame (Z+ up, identity)
├── T_E_W → {W} World Frame  
├── T_E_Fp → {Fp} Focus Frame
│   └── T_Fp_C → {C} Camera Frame (Z+ toward user)
└── T_E_Obj → {Obj} Object Frames
```

### Coordinate System Conventions
- **World Frame**: Z+ up (floor normal), Y+ forward, X+ right
- **Camera Frame**: Z+ toward user, Y+ up screen, X+ right screen
- **Transform Order**: `A * B` means "apply A, then apply B"

---

## 6. Error Handling Standards

### Custom Exception Hierarchy
```python
class PlayError(Exception):
    """Base exception for Play application."""
    pass

class TransformError(PlayError):
    """Raised when transform operations fail."""
    pass

class MeshError(PlayError):
    """Raised when mesh operations fail."""
    pass

class RenderError(PlayError):
    """Raised when rendering operations fail."""
    pass

class ContextError(PlayError):
    """Raised when OpenGL context operations fail."""
    pass
```

### Error Handling Patterns
```python
def _affine_inverse(transform: AFFINE_TRANSFORM) -> AFFINE_TRANSFORM:
    """Compute inverse of affine transform with validation."""
    if transform.Rotation.shape != (3, 3):
        raise TransformError(f"Invalid rotation matrix shape: {transform.Rotation.shape}")
    
    try:
        # Compute inverse
        pass
    except np.linalg.LinAlgError as e:
        raise TransformError(f"Singular matrix in transform inverse: {e}")
```

---

## 7. Configuration Management

### Configuration Class Pattern
```python
class PlayConfig:
    """Centralized configuration management."""
    # Debug Settings
    DEBUG: bool = True
    PERFORMANCE_LOGGING: bool = True
    
    # Performance Settings
    TARGET_FPS: float = 60.0
    MAX_TRIANGLES: int = 1_000_000
    
    # Memory Settings
    MESH_PREALLOC_SIZE: int = 250_000
    
    @classmethod
    def validate(cls) -> None:
        """Validate configuration consistency."""
        if cls.MESH_PREALLOC_SIZE <= 0:
            raise ValueError("MESH_PREALLOC_SIZE must be positive")
        if cls.TARGET_FPS <= 0:
            raise ValueError("TARGET_FPS must be positive")
```

---

## 8. Import Organization

### Import Ordering
```python
# 1. Standard library
import sys
import time
import os

# 2. Third-party libraries
import numpy as np
import glfw
from OpenGL.GL import *

# 3. Local imports (grouped by functionality)
from utils.globals import *
from utils.context_managers import OPENGL_CONTEXT, AFFINE_TRANSFORM
from utils.geometry_structures import MESH
from utils.opengl_interface import *
```

### Wildcard Import Guidelines
- **Avoid** except for OpenGL constants (`from OpenGL.GL import *`)
- **Use specific imports** for utils modules when possible
- **Document** wildcard imports with purpose

---

## 9. Testing Infrastructure

### Self-Test Pattern
```python
def _self_test() -> bool:
    """Basic self-test for module functionality."""
    try:
        # Test basic operations
        test_transform = AFFINE_TRANSFORM()
        result = _affine_inverse(test_transform)
        return True
    except Exception as e:
        LOGGER.error(f"Self-test failed: {e}")
        return False

if __name__ == "__main__":
    if DEBUG:
        success = _self_test()
        LOGGER.info(f"Module self-test: {'PASSED' if success else 'FAILED'}")
```

---

## 10. Performance Guidelines

### Performance-Critical Patterns
- **Avoid copies**: Use `copy=False` in numpy operations
- **Cache uniform locations**: Get once, reuse many times
- **Minimize state changes**: Batch OpenGL operations
- **Pre-allocate**: Use `DEFAULT_MESH_SIZE` for known sizes

### Timing and Profiling
```python
# Performance measurement pattern
start_time = time.perf_counter()
# ... operation ...
operation_time = time.perf_counter() - start_time
if DEBUG and operation_time > PERFORMANCE_THRESHOLD:
    LOGGER.warning(f"Slow operation: {operation_time:.4f}s")
```

---

## 11. Camera System Standards

### Camera Implementation Guidelines
- **Orbit camera**: Focus point + radius + angles
- **No camera class**: Keep in OPENGL_CONTEXT until necessary
- **Transform integration**: Use existing AFFINE_TRANSFORM system
- **Input handling**: Through existing flag-based system

### Camera Transform Hierarchy
```
{E} → T_E_Fp → {Fp} Focus Frame
              └── T_Fp_C → {C} Camera Frame
```

---

## 12. Common Pitfalls to Avoid

### Naming Inconsistencies
- ❌ `"Test Cube"` vs `"Test_Cube"`
- ❌ `_Create_mesh_buffers` vs `_create_mesh_buffers`
- ❌ `workloop_counter` vs `WORKLOOP_COUNTER`

### Transform Math Errors
- ❌ Euler angles (gimbal lock)
- ✅ Rotation matrices
- ❌ Inconsistent composition order
- ✅ A * B = "apply A then B"

### OpenGL State Issues
- ❌ Clear after drawing
- ✅ Clear before drawing
- ❌ Missing buffer unbinding
- ✅ Explicit cleanup

---

## Context Transfer Checklist

When resuming development or switching contexts:

1. **✅ Verify naming consistency** across all files
2. **✅ Check TODO priorities** and current phase status
3. **✅ Validate transforms** and coordinate systems
4. **✅ Review performance targets** and current metrics
5. **✅ Check debug settings** and logging verbosity
6. **✅ Verify file organization** matches current state

---

## Current Project Status Reference

**Phase**: Camera system implementation (Phase 2)
**Files**: ~810 lines total, well-organized after globals extraction
**Performance**: Single cube rendering @ 60 FPS
**Target**: 1M triangles @ 60 FPS
**Next Priority**: Orbital camera with mouse controls

**Critical Functions Status**:
- ✅ `_create_mesh_buffers`: Working
- ✅ `_load_meshes_to_context`: Working  
- ✅ `_create_view_matrix`: Working
- ✅ `_get_all_uniform_locations`: Working
- 🔄 Camera input handling: In progress

---

*This document should be updated as the project evolves and new patterns emerge.*
