import streamlit as st
import numpy as np
from core import geometry

st.set_page_config(page_title="CF-Dyno Phase 2", layout="wide")
st.title("CF-Dyno: Phase 2 (3D Mesh Engine)")
st.markdown("**Status:** Ready for 3D Geometry | **Mode:** Voxelization Test")

# --- SIDEBAR ---
st.sidebar.header("Geometry Input")
uploaded_file = st.sidebar.file_uploader("Upload .STL or .OBJ", type=['stl', 'obj'])
resolution = st.sidebar.slider("Mesh Resolution", 32, 128, 64)

# --- MAIN DISPLAY ---
col1, col2 = st.columns(2)

if uploaded_file is not None:
    with col1:
        st.info(f"File: {uploaded_file.name}")
        if st.button("Generate Voxel Mesh"):
            with st.spinner("Voxelizing... (This happens on Google Colab)"):
                # CALL THE NEW CORE MODULE
                grid = geometry.load_and_voxelize(uploaded_file, resolution)

                st.success(f"Mesh Generated! Grid Shape: {grid.shape}")

                # Store in session state to keep it active
                st.session_state['grid'] = grid

    with col2:
        if 'grid' in st.session_state:
            grid = st.session_state['grid']
            nz, ny, nx = grid.shape

            # VISUALIZE A SLICE
            # We can't easily show 3D in Streamlit without heavy lags yet,
            # so we show a 'CT Scan' slice of the mesh.
            slice_idx = st.slider("Slice View (Z-Axis)", 0, nz-1, nz//2)

            st.write(f"Cross-section at Z={slice_idx}")
            # 1 = Solid (Yellow), 0 = Fluid (Purple)
            st.image(grid[slice_idx, :, :] * 255, width=400, caption="White=Solid, Black=Fluid")

else:
    st.warning("Please upload a 3D file to test the mesher.")
    st.markdown("""
    **No file?** Download a simple cube or sphere STL from the internet, 
    or search "low poly stl" on Google.
    """)
