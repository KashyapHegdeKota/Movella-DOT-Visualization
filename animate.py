import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d import Axes3D
from scipy.spatial.transform import Rotation as R

# Load the data, skipping the first metadata row, the second row is the header
df = pd.read_csv('logfile_D4-22-CD-00-8C-B7.csv', skiprows=1)

# Downsample the data to every 10th sample to reduce animation time and file size
df = df.iloc[::15, :]

# Extract quaternion data
quaternions = df[['Quat_W', 'Quat_X', 'Quat_Y', 'Quat_Z']].to_numpy()

# Create a figure and a 3D axes
fig = plt.figure(figsize=(8, 8))
ax = fig.add_subplot(111, projection='3d')
ax.set_title('Bicep Curl Animation (Elbow Pivot)')
ax.set_xlabel('X-axis')
ax.set_ylabel('Y-axis')
ax.set_zlabel('Z-axis')

# Set the camera view to be from the side (along the Y-axis)
ax.view_init(elev=20, azim=90)

# Set axis limits
ax.set_xlim([-1, 1])
ax.set_ylim([-1, 1])
ax.set_zlim([-1, 1])
ax.set_aspect('equal') # Ensure the aspect ratio is equal

# Define cylinder properties
radius = 0.1
length = 0.8
resolution = 20

# Create the cylinder vertices so one end is at the origin (0,0,0)
# This makes the origin the pivot point, simulating the elbow joint.
x = np.linspace(0, length, resolution) # Shifted from (-len/2, len/2) to (0, len)
theta = np.linspace(0, 2 * np.pi, resolution)
theta_grid, x_grid = np.meshgrid(theta, x)
y_grid = radius * np.cos(theta_grid)
z_grid = radius * np.sin(theta_grid)

# Store the original vertices
original_vertices = np.stack([x_grid, y_grid, z_grid], axis=2)

# Create the cylinder plot object with a constant color
cylinder_color = 'cyan'
cylinder = ax.plot_surface(x_grid, y_grid, z_grid, color=cylinder_color, alpha=0.7)

# Animation update function
def update(frame):
    global cylinder
    # Get the quaternion for the current frame
    quat = quaternions[frame]

    # Create a rotation object from the quaternion. Note the order is (x, y, z, w) for SciPy
    rotation = R.from_quat([quat[1], quat[2], quat[3], quat[0]])

    # Apply the rotation to the cylinder's vertices
    rotated_vertices = rotation.apply(original_vertices.reshape(-1, 3)).reshape(original_vertices.shape)

    # Remove the old cylinder plot
    cylinder.remove()

    # Plot the rotated cylinder with a constant color
    cylinder = ax.plot_surface(rotated_vertices[:,:,0], rotated_vertices[:,:,1], rotated_vertices[:,:,2], color=cylinder_color, alpha=0.7)

    return cylinder,

# Create the animation with the slower settings
ani = FuncAnimation(fig, update, frames=len(quaternions), blit=False, interval=100)

# Save the animation as a new gif file
ani.save('bicep_curl_elbow_pivot.gif', writer='imagemagick', fps=10)

