import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from core import solver2d
import time

st.set_page_config(page_title="CF-Dyno Phase 1", layout="wide")
st.title("CF-Dyno: Phase 1 (Connectivity Test)")
st.markdown("**Status:** Pipeline Active | **Mode:** 2D Verification")

col1, col2 = st.columns(2)
with col1:
    grid_size = st.slider("Grid Resolution", 50, 200, 100)
    viscosity = st.slider("Viscosity", 0.01, 0.1, 0.02)
with col2:
    st.info("This interface runs on Google Colab via Ngrok tunnel.")
    start_btn = st.button("Start Simulation")

if start_btn:
    nx, ny = grid_size * 2, grid_size
    omega = 1.0 / (3.0 * viscosity + 0.5)

    nl = 9
    F = np.ones((ny, nx, nl)) + 0.01 * np.random.randn(ny, nx, nl)
    F[:, :, 3] += 2.0

    y, x = np.ogrid[0:ny, 0:nx]
    obstacle = (x - nx/4)**2 + (y - ny/2)**2 < (ny/9)**2

    plot_placeholder = st.empty()

    for i in range(100):
        F, velocity = solver2d.solve_lbm_frame(F, obstacle, omega)

        fig, ax = plt.subplots(figsize=(10, 3))
        velocity[obstacle] = np.nan 
        ax.imshow(velocity, cmap='jet')
        ax.axis('off')
        ax.set_title(f"Velocity Magnitude - Frame {i}")

        plot_placeholder.pyplot(fig)
        plt.close(fig)

    st.success("Simulation Complete")
