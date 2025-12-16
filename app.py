import streamlit as st
import numpy as np
import pyvista as pv
import tempfile
import streamlit.components.v1 as components
from core import geometry
from pyvirtualdisplay import Display

# --- HEADLESS DISPLAY SETUP ---
# This allows 3D rendering on Google Colab without a monitor
if 'display_started' not in st.session_state:
    try:
        display = Display(visible=0, size=(1280, 1024))
        display.start()
        st.session_state['display_started'] = True
    except:
        pass # Pass if running locally with a screen

st.set_page_config(page_title="CF-Dyno Phase 3", layout="wide")
st.title("CF-Dyno: Phase 3 (Interactive 3D View)")

# --- SIDEBAR ---
st.sidebar.header("1. Input")
uploaded_file = st.sidebar.file_uploader("Upload .STL", type=['stl'])
resolution = st.sidebar.slider("Resolution", 32, 128, 64)

# --- MAIN ---
col1, col2 = st.columns([1, 2]) # Make the viewer wider

if uploaded_file is not None:
    # 1. GENERATE GRID
    if 'grid' not in st.session_state or st.sidebar.button("Regenerate Mesh"):
        with st.spinner("Voxelizing..."):
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
            st.info("Rotate and Zoom the model on the right ->")

        with col2:
            st.markdown("### Interactive 3D Preview")
            with st.spinner("Rendering 3D Scene..."):
                # --- PYVISTA CONVERSION ---
                # 1. Create a structured grid compatible with the numpy array
                pv_grid = pv.ImageData()
                pv_grid.dimensions = np.array(grid.shape) + 1
                pv_grid.spacing = (1, 1, 1)
                pv_grid.cell_data["values"] = grid.flatten(order="F") 
                
                # 2. Threshold: Only show the SOLID parts (Value == 1)
                # This makes the fluid transparent so we can see the object
                mesh = pv_grid.threshold([0.9, 1.1])
                
                # 3. Create Plotter
                plotter = pv.Plotter(window_size=[800, 600], off_screen=True)
                plotter.add_mesh(mesh, color="orange", show_edges=True, opacity=0.8)
                plotter.set_background("white")
                plotter.view_isometric()
                
                # 4. Export to HTML (Client-side interactivity)
                # We save it to a temp file and read it back
                with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as tmp:
                    plotter.export_html(tmp.name)
                    tmp.seek(0)
                    html_content = tmp.read().decode('utf-8')
                
                # 5. Embed in Streamlit
                components.html(html_content, height=600, scrolling=False)

else:
    st.info("Upload an STL file to see the 3D Voxel Engine in action.")
