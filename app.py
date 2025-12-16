import streamlit as st
import numpy as np
import plotly.graph_objects as go
from core import geometry

st.set_page_config(page_title="CF-Dyno Phase 3", layout="wide")
st.title("CF-Dyno: Phase 3 (Interactive 3D View)")
st.markdown("**Status:** Rendering with Plotly (Stable) | **Mode:** Voxel Inspector")

# --- SIDEBAR ---
st.sidebar.header("1. Input")
uploaded_file = st.sidebar.file_uploader("Upload .STL", type=['stl'])
resolution = st.sidebar.slider("Resolution", 32, 64, 40) # Keep low for speed

# --- MAIN ---
col1, col2 = st.columns([1, 2])

if uploaded_file is not None:
    # 1. GENERATE GRID
    if 'grid' not in st.session_state or st.sidebar.button("Regenerate Mesh"):
        with st.spinner("Voxelizing geometry..."):
            grid = geometry.load_and_voxelize(uploaded_file, resolution)
            st.session_state['grid'] = grid
            st.success("Mesh Updated!")

    # 2. VISUALIZE
    if 'grid' in st.session_state:
        grid = st.session_state['grid']
        
        with col1:
            st.markdown("### Mesh Stats")
            st.write(f"**Grid Size:** {grid.shape}")
            st.write(f"**Solid Cells:** {np.sum(grid)}")
            st.info("The Plotly engine renders this natively in your browser.")

        with col2:
            st.markdown("### Interactive 3D Preview")
            with st.spinner("Generating 3D Plot..."):
                # Create coordinates for the Volume Plot
                X, Y, Z = np.mgrid[0:grid.shape[0], 0:grid.shape[1], 0:grid.shape[2]]
                
                # We use Isosurface to draw the boundary between 0 (Fluid) and 1 (Solid)
                fig = go.Figure(data=go.Volume(
                    x=X.flatten(),
                    y=Y.flatten(),
                    z=Z.flatten(),
                    value=grid.flatten(),
                    isomin=0.5,
                    isomax=1.5,
                    opacity=0.3, # Semi-transparent
                    surface_count=2,
                    colorscale='Jet',
                ))
                
                fig.update_layout(scene=dict(
                    xaxis=dict(visible=False),
                    yaxis=dict(visible=False),
                    zaxis=dict(visible=False)
                ))
                
                st.plotly_chart(fig, use_container_width=True)

else:
    st.info("Upload an STL file to see the 3D Engine in action.")
