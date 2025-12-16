import streamlit as st
import numpy as np
import plotly.graph_objects as go
from core import geometry

st.set_page_config(page_title="CF-Dyno High-Res Mesh", layout="wide")
st.title("CF-Dyno: High-Res Mesh Inspector")
st.markdown("**Mode:** Geometry Check (Phase 3.5) | **Max Res:** 200")

# --- SIDEBAR ---
st.sidebar.header("1. Geometry Input")
uploaded_file = st.sidebar.file_uploader("Upload .STL", type=['stl'])

# UNLOCKED: We allow up to 200 for high-detail meshing
resolution = st.sidebar.slider("Grid Resolution", 50, 200, 100) 

# --- MAIN ---
col1, col2 = st.columns([1, 2])

if uploaded_file is not None:
    # 1. GENERATE GRID
    if 'grid' not in st.session_state or st.sidebar.button("Regenerate Mesh"):
        with st.spinner(f"Voxelizing at High Resolution ({resolution})..."):
            # This runs on Colab (Fast CPU)
            grid = geometry.load_and_voxelize(uploaded_file, resolution)
            st.session_state['grid'] = grid
            st.success(f"Mesh Ready: {grid.shape} cells")

    # 2. VISUALIZE
    if 'grid' in st.session_state:
        grid = st.session_state['grid']
        
        with col1:
            st.markdown("### Mesh Stats")
            st.write(f"**Grid Size:** {grid.shape}")
            st.write(f"**Solid Voxels:** {np.sum(grid)}")
            
            # Advice
            if max(grid.shape) > 120:
                st.warning("⚠️ High Resolution detected. Downsampling view to prevent browser crash.")

        with col2:
            st.markdown("### 3D Voxel Preview")
            with st.spinner("Rendering Plot..."):
                
                # --- INTELLIGENT DOWNSAMPLING ---
                # We skip pixels ONLY for the visualizer.
                # The actual grid in memory stays High-Res for Phase 4.
                stride = 1
                if max(grid.shape) > 100: stride = 2
                if max(grid.shape) > 150: stride = 3
                
                # Create a lighter version for Plotly
                d_grid = grid[::stride, ::stride, ::stride]
                
                # Create Coordinates
                X, Y, Z = np.mgrid[0:d_grid.shape[0], 0:d_grid.shape[1], 0:d_grid.shape[2]]
                
                # Render Volume
                fig = go.Figure(data=go.Volume(
                    x=X.flatten(),
                    y=Y.flatten(),
                    z=Z.flatten(),
                    value=d_grid.flatten(),
                    isomin=0.5, # Show only solids (1)
                    isomax=1.5,
                    opacity=0.6,
                    surface_count=1, # Just the surface
                    colorscale='Spectral', 
                    caps=dict(x_show=False, y_show=False, z_show=False)
                ))
                
                fig.update_layout(scene=dict(
                    xaxis=dict(visible=False),
                    yaxis=dict(visible=False),
                    zaxis=dict(visible=False)
                ))
                
                st.plotly_chart(fig, use_container_width=True)

else:
    st.info("Upload an STL file to test the High-Res Engine.")
