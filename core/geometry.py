import numpy as np
import trimesh
import tempfile
import os

def load_and_voxelize(uploaded_file, resolution=64):
    """
    1. Reads an Uploaded File.
    2. Normalizes it (fits it in a box).
    3. Voxelizes it (turns it into a grid).
    """
    # Save file temporarily so Trimesh can read it
    file_ext = uploaded_file.name.split('.')[-1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_ext}") as tmp:
        tmp.write(uploaded_file.getvalue())
        tmp_path = tmp.name

    # Load Mesh
    mesh = trimesh.load(tmp_path)

    # Normalize (Center and Scale to 1.0)
    mesh.apply_translation(-mesh.centroid)
    scale = 1.0 / np.max(mesh.extents)
    mesh.apply_scale(scale)

    # Voxelize (The magic step)
    # pitch = size of one block
    voxel_grid = mesh.voxelized(pitch=1.0/resolution)

    # Convert to Numpy (1=Solid, 0=Fluid)
    grid_matrix = voxel_grid.matrix.astype(int)

    # Pad with 2 empty cells on all sides (so walls don't touch edges)
    padded_grid = np.pad(grid_matrix, 2, mode='constant', constant_values=0)

    # Clean up
    os.remove(tmp_path)

    return padded_grid
