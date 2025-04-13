import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import io
from PIL import Image
import time

# Set page config
st.set_page_config(
    page_title="Interactive Sound Wave Visualizer",
    page_icon="🔊",
    layout="wide"
)

# App title and description
st.title("🔊 Interactive Sound Wave Visualizer")
st.markdown("""
Explore the fascinating world of sound waves with this interactive app! 
Adjust the parameters to see how different waveforms, frequencies, and amplitudes affect sound waves.
""")

# Create sidebar for controls
st.sidebar.header("Wave Controls")

# Waveform selection
waveform = st.sidebar.selectbox(
    "Select Waveform",
    ["Sine", "Square", "Sawtooth", "Triangle"]
)

# Frequency slider (Hz)
freq = st.sidebar.slider(
    "Frequency (Hz)", 
    min_value=1, 
    max_value=20, 
    value=5,
    help="Number of complete cycles per second"
)

# Amplitude slider
amplitude = st.sidebar.slider(
    "Amplitude", 
    min_value=0.1, 
    max_value=1.0, 
    value=0.8,
    step=0.1,
    help="Maximum displacement from the center line"
)

# Phase slider (degrees)
phase = st.sidebar.slider(
    "Phase (degrees)", 
    min_value=0, 
    max_value=360, 
    value=0,
    help="Horizontal shift of the wave"
)

# Damping factor for special effects
damping = st.sidebar.slider(
    "Damping Factor", 
    min_value=0.0, 
    max_value=0.2, 
    value=0.0,
    step=0.01,
    help="Rate at which the amplitude decreases over time/distance"
)

# Animation speed
speed = st.sidebar.slider(
    "Animation Speed", 
    min_value=0.1, 
    max_value=2.0, 
    value=1.0,
    step=0.1
)

# Color selection
color = st.sidebar.color_picker("Wave Color", "#1E90FF")

# Advanced options with expander
with st.sidebar.expander("Advanced Options"):
    show_envelope = st.checkbox("Show Envelope", value=False)
    show_particles = st.checkbox("Show Particle Motion", value=False)
    grid_visible = st.checkbox("Show Grid", value=True)
    dark_mode = st.checkbox("Dark Mode", value=False)

# Function to generate different waveforms
def generate_waveform(x, time_point, waveform_type, freq, amp, phase_rad, damping):
    phase_adjusted = phase_rad + time_point * freq * 2 * np.pi * speed
    
    # Apply damping if needed
    if damping > 0:
        # Exponential decay based on x position
        damping_factor = np.exp(-damping * np.abs(x))
        effective_amp = amp * damping_factor
    else:
        effective_amp = amp
        
    if waveform_type == "Sine":
        return effective_amp * np.sin(2 * np.pi * freq * x + phase_adjusted)
    elif waveform_type == "Square":
        return effective_amp * np.sign(np.sin(2 * np.pi * freq * x + phase_adjusted))
    elif waveform_type == "Sawtooth":
        return effective_amp * (2 * ((freq * x + phase_adjusted/(2*np.pi)) % 1) - 1)
    elif waveform_type == "Triangle":
        return effective_amp * (2 * np.abs(2 * ((freq * x + phase_adjusted/(2*np.pi)) % 1) - 1) - 1)

# Function to create animation frames
def create_animation_frame(time_point):
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Setting the theme
    if dark_mode:
        plt.style.use('dark_background')
        grid_color = 'gray'
    else:
        plt.style.use('default')
        grid_color = 'lightgray'
    
    # Setting axes
    ax.set_xlim(0, 2)
    ax.set_ylim(-1.2, 1.2)
    ax.set_xlabel('Distance')
    ax.set_ylabel('Displacement')
    ax.grid(grid_visible, color=grid_color, linestyle='--', alpha=0.7)
    
    # Convert phase from degrees to radians
    phase_rad = np.deg2rad(phase)
    
    # Generate x values
    x = np.linspace(0, 2, 1000)
    
    # Calculate wave
    y = generate_waveform(x, time_point, waveform, freq, amplitude, phase_rad, damping)
    
    # Plot the wave
    ax.plot(x, y, color=color, linewidth=3)
    
    # Add envelope if selected
    if show_envelope and damping > 0:
        envelope_up = amplitude * np.exp(-damping * np.abs(x))
        envelope_down = -amplitude * np.exp(-damping * np.abs(x))
        ax.plot(x, envelope_up, '--', color='red', alpha=0.5)
        ax.plot(x, envelope_down, '--', color='red', alpha=0.5)
    
    # Add particles if selected
    if show_particles:
        particle_x = np.linspace(0, 2, 30)
        particle_y = generate_waveform(particle_x, time_point, waveform, freq, amplitude, phase_rad, damping)
        ax.scatter(particle_x, particle_y, color='red', s=30, zorder=3)
    
    # Add waveform info
    info_text = f"Waveform: {waveform} | Frequency: {freq} Hz | Amplitude: {amplitude}"
    ax.text(0.02, 0.95, info_text, transform=ax.transAxes, 
            fontsize=10, va='top', bbox=dict(boxstyle="round,pad=0.3", 
            fc='white' if not dark_mode else 'black', ec="gray", alpha=0.7))
    
    plt.tight_layout()
    
    # Convert plot to image
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=100)
    buf.seek(0)
    img = Image.open(buf)
    plt.close(fig)
    
    return img

# Main display area split into two columns
col1, col2 = st.columns([3, 1])

with col2:
    st.subheader("What Am I Seeing?")
    st.write("""
    This visualization shows how sound waves propagate through a medium.
    
    **Waveform Types**:
    - **Sine**: The purest tone, with smooth transitions
    - **Square**: Rich in harmonics, sounds buzzy
    - **Sawtooth**: Bright, harsh sound with many harmonics
    - **Triangle**: Softer than square, with odd harmonics
    
    **Controls**:
    - **Frequency**: Number of cycles per second (Hz)
    - **Amplitude**: How loud the sound is
    - **Phase**: Shifts the wave left/right
    - **Damping**: How quickly the wave dies out
    """)
    
    # Fun facts in an expander
    with st.expander("Fun Facts About Sound"):
        st.markdown("""
        - Sound cannot travel in a vacuum - it needs a medium to propagate
        - The speed of sound in air is about 343 meters per second
        - Human ears can typically hear frequencies between 20 Hz and 20,000 Hz
        - A sound wave's amplitude determines how loud it sounds
        - Interference occurs when two sound waves meet and combine
        """)

# Create placeholder for animation
animation_placeholder = col1.empty()

# Display wave explanation based on selected waveform
with col1:
    st.subheader(f"About {waveform} Waves")
    
    if waveform == "Sine":
        st.write("""
        **Sine waves** are the fundamental building blocks of sound. They represent pure tones 
        with a single frequency. All other complex sounds can be created by combining sine waves 
        of different frequencies and amplitudes.
        """)
    elif waveform == "Square":
        st.write("""
        **Square waves** alternate between two fixed values, creating a buzzy sound. They contain 
        a fundamental frequency plus odd harmonics. In music synthesis, square waves are often 
        used for bass and lead sounds.
        """)
    elif waveform == "Sawtooth":
        st.write("""
        **Sawtooth waves** rise linearly and then drop vertically. They contain both odd and 
        even harmonics, creating a bright, harsh sound. They're commonly used in synthesizers 
        for strings and brass simulations.
        """)
    elif waveform == "Triangle":
        st.write("""
        **Triangle waves** rise and fall linearly. They contain only odd harmonics that decrease 
        more rapidly than square waves, creating a softer sound. They're often used for flute-like 
        sounds in synthesis.
        """)

# Function to update animation
def update_animation():
    time_points = np.linspace(0, 1, 20)  # 20 frames per cycle
    frames = []
    
    # Generate all frames first
    progress_bar = st.progress(0)
    for i, t in enumerate(time_points):
        frames.append(create_animation_frame(t))
        progress_bar.progress((i + 1) / len(time_points))
    
    progress_bar.empty()
    
    # Display animation in a loop
    frame_idx = 0
    while True:
        animation_placeholder.image(frames[frame_idx], use_column_width=True)
        frame_idx = (frame_idx + 1) % len(frames)
        time.sleep(0.05 / speed)  # Adjust speed

# Run the animation in a try-except block to handle session state
try:
    update_animation()
except:
    # If there's an issue with animation, just show a static frame
    animation_placeholder.image(create_animation_frame(0), use_column_width=True)
    st.warning("Animation paused. Adjust parameters to see changes.")
