"""
Mesh converter: exports CAD shapes to GLTF format.
Requires trimesh + numpy. Falls back gracefully if unavailable.
"""
import os
from typing import Optional
from ..utils import setup_logger

logger = setup_logger("mesh_converter")

try:
    import trimesh
    import numpy as np
    TRIMESH_AVAILABLE = True
except ImportError:
    TRIMESH_AVAILABLE = False
    logger.warning("trimesh not installed — mesh export disabled")

MESH_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "static", "meshes")


def ensure_mesh_dir() -> None:
    """
    Ensure the mesh directory exists.
    """
    os.makedirs(MESH_DIR, exist_ok=True)


def shape_to_gltf(shape, obj_id: str) -> Optional[str]:
    """
    Convert a CadQuery shape to a GLTF file.
    Returns the relative URL path or None.
    """
    if not TRIMESH_AVAILABLE:
        logger.warning("Cannot export mesh: trimesh not available")
        return None

    try:
        from cadquery import exporters
        import tempfile

        ensure_mesh_dir()

        # Export to STL first (CadQuery native)
        stl_path = os.path.join(MESH_DIR, f"{obj_id}.stl")
        exporters.export(shape, stl_path)

        # Convert STL → GLTF via trimesh
        mesh = trimesh.load(stl_path)
        gltf_path = os.path.join(MESH_DIR, f"{obj_id}.glb")
        mesh.export(gltf_path, file_type="glb")

        # Cleanup STL
        os.remove(stl_path)

        logger.info(f"Exported mesh: {gltf_path}")
        return f"/static/meshes/{obj_id}.glb"

    except Exception as e:
        logger.error(f"Mesh export failed for {obj_id}: {e}")
        return None