import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d import Axes3D
from scipy.spatial.transform import Rotation as R

# --- 1. Load and Prepare Data ---
df_forearm = pd.read_csv('logfile_forearm_D4-22-CD-00-8C-B7.csv', skiprows=1)
df_forearm = df_forearm.iloc[::15, :]
quat_forearm = df_forearm[['Quat_W', 'Quat_X', 'Quat_Y', 'Quat_Z']].to_numpy()

df_upper_arm = pd.read_csv('logfile_upper_arm_D4-22-CD-00-8C-86.csv', skiprows=1)
df_upper_arm = df_upper_arm.iloc[::15, :]
quat_upper_arm = df_upper_arm[['Quat_W', 'Quat_X', 'Quat_Y', 'Quat_Z']].to_numpy()

min_frames = min(len(quat_forearm), len(quat_upper_arm))
quat_forearm = quat_forearm[:min_frames]
quat_upper_arm = quat_upper_arm[:min_frames]


# --- 2. Define Geometry ---
# Shoulder is at origin (0,0,0). Upper arm extends down (-Z). Forearm extends further down.
resolution = 20
theta = np.linspace(0, 2 * np.pi, resolution)
phi = np.linspace(0, 2 * np.pi, resolution)
theta_sphere, phi_sphere = np.meshgrid(theta, phi)

# Upper Arm (Cylinder) - Extends from origin down the Z-axis
upper_arm_length = 0.8
upper_arm_radius = 0.12
z_upper_arm = np.linspace(0, -upper_arm_length, resolution)
theta_grid_u, z_grid_u = np.meshgrid(theta, z_upper_arm)
x_grid_u = upper_arm_radius * np.cos(theta_grid_u)
y_grid_u = upper_arm_radius * np.sin(theta_grid_u)
original_upper_arm_vertices = np.stack([x_grid_u, y_grid_u, z_grid_u], axis=2)

# Shoulder (Sphere) - at the origin
shoulder_radius = 0.15
x_shoulder = shoulder_radius * np.sin(theta_sphere) * np.cos(phi_sphere)
y_shoulder = shoulder_radius * np.sin(theta_sphere) * np.sin(phi_sphere)
z_shoulder = shoulder_radius * np.cos(theta_sphere)
original_shoulder_vertices = np.stack([x_shoulder, y_shoulder, z_shoulder], axis=2)

# Forearm (Cylinder) - Also defined locally, starting from origin and extending down
forearm_length = 0.8
forearm_radius = 0.1
z_forearm = np.linspace(0, -forearm_length, resolution)
theta_grid_f, z_grid_f = np.meshgrid(theta, z_forearm)
x_grid_f = forearm_radius * np.cos(theta_grid_f)
y_grid_f = forearm_radius * np.sin(theta_grid_f)
original_forearm_vertices = np.stack([x_grid_f, y_grid_f, z_grid_f], axis=2)

# Hand (Sphere) - At the end of the local forearm definition
fist_radius = 0.12
x_fist = fist_radius * np.sin(theta_sphere) * np.cos(phi_sphere)
y_fist = fist_radius * np.sin(theta_sphere) * np.sin(phi_sphere)
z_fist = fist_radius * np.cos(theta_sphere) - forearm_length
original_fist_vertices = np.stack([x_fist, y_fist, z_fist], axis=2)

# Elbow (Sphere) - Also defined locally at the origin
elbow_radius = 0.1
x_elbow = elbow_radius * np.sin(theta_sphere) * np.cos(phi_sphere)
y_elbow = elbow_radius * np.sin(theta_sphere) * np.sin(phi_sphere)
z_elbow = elbow_radius * np.cos(theta_sphere)
original_elbow_vertices = np.stack([x_elbow, y_elbow, z_elbow], axis=2)


# --- 3. Set up the 3D Plot ---
fig = plt.figure(figsize=(8, 8)) # Adjusted figure size for better aspect ratio
ax = fig.add_subplot(111, projection='3d')
ax.set_title('Bicep Curl Animation (Side View)')

# <<< CHANGE IS HERE >>>
ax.view_init(elev=15, azim=0) # Set camera to a side view

ax.set_xlim([-1.5, 1.5]); ax.set_ylim([-1.5, 1.5]); ax.set_zlim([-1.5, 1.5])
ax.set_xlabel('X'); ax.set_ylabel('Y'); ax.set_zlabel('Z')
ax.set_aspect('equal')

# Create initial plot objects
shoulder_plot = ax.plot_surface(*original_shoulder_vertices.T, color='mediumslateblue')
upper_arm_plot = ax.plot_surface(*original_upper_arm_vertices.T, color='skyblue')
elbow_plot = ax.plot_surface(*original_elbow_vertices.T, color='royalblue')
forearm_plot = ax.plot_surface(*original_forearm_vertices.T, color='lightcoral')
fist_plot = ax.plot_surface(*original_fist_vertices.T, color='darksalmon')


# --- 4. Define Correction and Animation Function ---
# Calculate initial offset rotations to align sensor data with the model's T-pose
initial_upper_arm_rot_inv = R.from_quat(np.roll(quat_upper_arm[0], -1)).inv()
initial_forearm_rot_inv = R.from_quat(np.roll(quat_forearm[0], -1)).inv()

def update(frame):
    global shoulder_plot, upper_arm_plot, elbow_plot, forearm_plot, fist_plot

    # Get current sensor orientations and normalize them to the start of the recording
    rot_upper_arm_abs = R.from_quat(np.roll(quat_upper_arm[frame], -1)) * initial_upper_arm_rot_inv
    rot_forearm_abs = R.from_quat(np.roll(quat_forearm[frame], -1)) * initial_forearm_rot_inv

    # --- Hierarchical Rotation ---
    # 1. Upper arm rotates from the shoulder (origin)
    rotated_upper_arm = rot_upper_arm_abs.apply(original_upper_arm_vertices.reshape(-1, 3)).reshape(original_upper_arm_vertices.shape)

    # 2. Calculate the elbow's new position at the end of the rotated upper arm
    elbow_pos = rot_upper_arm_abs.apply([0, 0, -upper_arm_length])
    
    # 3. The forearm's rotation is relative to the world, so we apply it directly.
    #    Then we translate the entire rotated forearm to the new elbow position.
    rotated_forearm_local = rot_forearm_abs.apply(original_forearm_vertices.reshape(-1, 3)).reshape(original_forearm_vertices.shape)
    translated_forearm = rotated_forearm_local + elbow_pos
    
    # 4. Attach the other parts to their respective segments
    translated_elbow = rot_forearm_abs.apply(original_elbow_vertices.reshape(-1, 3)).reshape(original_elbow_vertices.shape) + elbow_pos
    translated_fist = rot_forearm_abs.apply(original_fist_vertices.reshape(-1, 3)).reshape(original_fist_vertices.shape) + elbow_pos

    # Remove and redraw all plots
    upper_arm_plot.remove()
    elbow_plot.remove()
    forearm_plot.remove()
    fist_plot.remove()
    
    upper_arm_plot = ax.plot_surface(*rotated_upper_arm.T, color='skyblue')
    elbow_plot = ax.plot_surface(*translated_elbow.T, color='royalblue')
    forearm_plot = ax.plot_surface(*translated_forearm.T, color='lightcoral')
    fist_plot = ax.plot_surface(*translated_fist.T, color='darksalmon')

    return shoulder_plot, upper_arm_plot, elbow_plot, forearm_plot, fist_plot

# --- 5. Create and Save the Animation ---
ani = FuncAnimation(fig, update, frames=min_frames, blit=False, interval=100)
ani.save('bicep_curl_final.gif', writer='pillow', fps=4)
plt.close()