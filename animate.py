import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d import Axes3D
from scipy.spatial.transform import Rotation as R

# Load the data, skipping the first metadata row, the second row is the header
df = pd.read_csv('logfile_D4-22-CD-00-8C-B7.csv', skiprows=1)

# Downsample the data to every 15th sample for smoother and faster animation
df = df.iloc[::15, :]

# Extract quaternion data and handle potential zero-norm quaternions
quaternions = df[['Quat_W', 'Quat_X', 'Quat_Y', 'Quat_Z']].to_numpy()
valid_indices = np.linalg.norm(quaternions, axis=1) > 1e-6
quaternions = quaternions[valid_indices]


# --- 1. Define Geometry for Forearm and Hand ---

# Common properties
resolution = 20 # Number of points to define the shapes

# Forearm (Cylinder) properties
forearm_length = 0.8
forearm_radius = 0.1

# Create the forearm vertices with one end at the origin (elbow pivot)
x_forearm = np.linspace(0, forearm_length, resolution)
theta = np.linspace(0, 2 * np.pi, resolution)
theta_grid, x_grid = np.meshgrid(theta, x_forearm)
y_grid = forearm_radius * np.cos(theta_grid)
z_grid = forearm_radius * np.sin(theta_grid)
original_forearm_vertices = np.stack([x_grid, y_grid, z_grid], axis=2)

# Hand (Sphere) properties
fist_radius = 0.15 # Slightly larger than forearm

# Create the fist vertices, centered at the end of the forearm
phi = np.linspace(0, 2 * np.pi, resolution)
theta = np.linspace(0, np.pi, resolution)
phi_grid, theta_grid = np.meshgrid(phi, theta)

# Place the sphere at the end of the forearm
x_fist = fist_radius * np.sin(theta_grid) * np.cos(phi_grid) + forearm_length
y_fist = fist_radius * np.sin(theta_grid) * np.sin(phi_grid)
z_fist = fist_radius * np.cos(theta_grid)
original_fist_vertices = np.stack([x_fist, y_fist, z_fist], axis=2)



# Elbow (Sphere) properties
elbow_radius = 0.12 # Make it slightly larger than the forearm

# Create the elbow vertices, centered at the origin (0,0,0)
# This is the same formula as the fist, but without the forearm_length offset
x_elbow = elbow_radius * np.sin(theta_grid) * np.cos(phi_grid)
y_elbow = elbow_radius * np.sin(theta_grid) * np.sin(phi_grid)
z_elbow = elbow_radius * np.cos(theta_grid)
original_elbow_vertices = np.stack([x_elbow, y_elbow, z_elbow], axis=2)


# --- 2. Set up the 3D Plot ---

fig = plt.figure(figsize=(8, 8))
ax = fig.add_subplot(111, projection='3d')
ax.set_title('Bicep Curl Animation')

# Set a better camera angle to view the curl
ax.view_init(elev=20, azim=70)

# Set axis limits and aspect ratio
ax.set_xlim([-1, 1])
ax.set_ylim([-1, 1])
ax.set_zlim([-1, 1])
ax.set_aspect('equal')

# Create the initial plot objects for the arm and hand
forearm_plot = ax.plot_surface(
    original_forearm_vertices[:,:,0],
    original_forearm_vertices[:,:,1],
    original_forearm_vertices[:,:,2],
    color='lightcoral', alpha=0.8)

fist_plot = ax.plot_surface(
    original_fist_vertices[:,:,0],
    original_fist_vertices[:,:,1],
    original_fist_vertices[:,:,2],
    color='darksalmon', alpha=0.9)


# Draw the stationary elbow joint
elbow_plot = ax.plot_surface(
    original_elbow_vertices[:,:,0],
    original_elbow_vertices[:,:,1],
    original_elbow_vertices[:,:,2],
    color='royalblue', alpha=0.9)
# --- 3. Animation Update Function ---

def update(frame):
    global forearm_plot, fist_plot
    
    # Get the quaternion for the current frame
    quat = quaternions[frame]
    
    # Create a rotation object (x, y, z, w)
    rotation = R.from_quat([quat[1], quat[2], quat[3], quat[0]])

    # Apply the same rotation to both the forearm and the fist vertices
    rotated_forearm = rotation.apply(original_forearm_vertices.reshape(-1, 3)).reshape(original_forearm_vertices.shape)
    rotated_fist = rotation.apply(original_fist_vertices.reshape(-1, 3)).reshape(original_fist_vertices.shape)

    # Remove the old plots
    forearm_plot.remove()
    fist_plot.remove()

    # Plot the newly rotated forearm and fist
    forearm_plot = ax.plot_surface(
        rotated_forearm[:,:,0],
        rotated_forearm[:,:,1],
        rotated_forearm[:,:,2],
        color='lightcoral', alpha=0.8)
        
    fist_plot = ax.plot_surface(
        rotated_fist[:,:,0],
        rotated_fist[:,:,1],
        rotated_fist[:,:,2],
        color='darksalmon', alpha=0.9)

    return forearm_plot, fist_plot

# --- 4. Create and Save the Animation ---

ani = FuncAnimation(fig, update, frames=len(quaternions), blit=False, interval=100)

# Save the animation (you may need to install imagemagick or use a different writer)
# Using 'pillow' writer is a good alternative if 'imagemagick' is not installed.
ani.save('bicep_curl_animation.gif', writer='pillow', fps=15)

plt.show() # Optional: displays the animation window