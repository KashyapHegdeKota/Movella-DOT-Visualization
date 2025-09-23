# import pandas as pd
# import numpy as np
# import matplotlib.pyplot as plt
# from mpl_toolkits.mplot3d import Axes3D
# from matplotlib.animation import FuncAnimation

# # --- Data Loading and Parsing ---
# try:
#     df = pd.read_csv('quaternion_data.csv')
# except FileNotFoundError:
#     print("Error: 'quaternion_data.csv' not found.")
#     print("Please make sure the CSV file is in the same directory as this Python script.")
#     exit()

# def parse_quaternions(series):
#     """Converts a series of quaternion strings to a list of numpy arrays."""
#     return series.apply(lambda x: np.fromstring(x, sep=',')).tolist()

# quaternions_forearm = parse_quaternions(df['tracker_1_WXYZ'])
# quaternions_upper_arm = parse_quaternions(df['tracker_2_WXYZ'])

# # --- Constants ---
# UPPER_ARM_LENGTH = 0.3
# FOREARM_LENGTH = 0.25
# N_FRAMES = len(df)

# # --- Utility Functions ---
# def quaternion_to_rotation_matrix(q):
#     """Converts a quaternion into a rotation matrix."""
#     w, x, y, z = q
#     # Normalize quaternion
#     q_norm = np.linalg.norm(q)
#     if q_norm > 0:
#         w, x, y, z = w/q_norm, x/q_norm, y/q_norm, z/q_norm
    
#     return np.array([
#         [1 - 2*y**2 - 2*z**2, 2*x*y - 2*z*w, 2*x*z + 2*y*w],
#         [2*x*y + 2*z*w, 1 - 2*x**2 - 2*z**2, 2*y*z - 2*x*w],
#         [2*x*z - 2*y*w, 2*y*z + 2*x*w, 1 - 2*x**2 - 2*y**2]
#     ])

# # --- Initial Pose Calibration ---
# # Get the rotation matrices for the very first frame.
# R_upper_arm_initial = quaternion_to_rotation_matrix(quaternions_upper_arm[0])
# R_forearm_initial = quaternion_to_rotation_matrix(quaternions_forearm[0])

# # We need the inverse of the initial rotations to calculate the change.
# # For a rotation matrix, the inverse is its transpose.
# R_upper_arm_initial_inv = R_upper_arm_initial.T
# R_forearm_initial_inv = R_forearm_initial.T

# # Define the arm segments in our ideal "straight down" pose.
# upper_arm_vec_ideal = np.array([0, -UPPER_ARM_LENGTH, 0])
# forearm_vec_ideal = np.array([0, -FOREARM_LENGTH, 0])


# # (The rest of the script for creating cylinders/spheres is the same)
# def create_cylinder(p1, p2, radius):
#     v = p2 - p1
#     mag = np.linalg.norm(v)
#     v = v / mag if mag > 0 else np.array([0, 0, 1])
#     not_v = np.array([1, 0, 0])
#     if (v == not_v).all():
#         not_v = np.array([0, 1, 0])
#     n1 = np.cross(v, not_v)
#     n1 /= np.linalg.norm(n1)
#     n2 = np.cross(v, n1)
#     t = np.linspace(0, mag, 2)
#     theta = np.linspace(0, 2 * np.pi, 10)
#     t, theta2 = np.meshgrid(t, theta)
#     X, Y, Z = [p1[i] + v[i] * t + radius * (n1[i] * np.cos(theta2) + n2[i] * np.sin(theta2)) for i in range(3)]
#     return X, Y, Z

# def create_sphere(center, radius, ax):
#     u = np.linspace(0, 2 * np.pi, 20)
#     v = np.linspace(0, np.pi, 20)
#     x = radius * np.outer(np.cos(u), np.sin(v)) + center[0]
#     y = radius * np.outer(np.sin(u), np.sin(v)) + center[1]
#     z = radius * np.outer(np.ones(np.size(u)), np.cos(v)) + center[2]
#     ax.plot_surface(x, y, z, color='b')

# # --- Animation Setup ---
# fig = plt.figure(figsize=(8, 8))
# ax = fig.add_subplot(111, projection='3d')

# def update(frame):
#     ax.cla()

#     # Get the current global rotation from the trackers
#     R_upper_arm_current = quaternion_to_rotation_matrix(quaternions_upper_arm[frame])
#     R_forearm_current = quaternion_to_rotation_matrix(quaternions_forearm[frame])

#     # Calculate the change in rotation from the initial frame
#     delta_R_upper = R_upper_arm_current @ R_upper_arm_initial_inv
#     delta_R_forearm = R_forearm_current @ R_forearm_initial_inv

#     # Apply this change to our ideal arm vectors to get their current position
#     current_upper_arm_vec = delta_R_upper @ upper_arm_vec_ideal
#     current_forearm_vec = delta_R_forearm @ forearm_vec_ideal

#     # --- Calculate Joint Positions ---
#     shoulder_pos = np.array([0, 0, 0])
#     elbow_pos = shoulder_pos + current_upper_arm_vec
#     # IMPORTANT: The forearm is attached to the elbow and its orientation is now correct
#     wrist_pos = elbow_pos + current_forearm_vec

#     # --- Draw Geometry ---
#     create_sphere(shoulder_pos, 0.03, ax)
#     create_sphere(elbow_pos, 0.03, ax)
#     create_sphere(wrist_pos, 0.03, ax)
#     X_upper, Y_upper, Z_upper = create_cylinder(shoulder_pos, elbow_pos, 0.02)
#     ax.plot_surface(X_upper, Y_upper, Z_upper, color='red')
#     X_forearm, Y_forearm, Z_forearm = create_cylinder(elbow_pos, wrist_pos, 0.02)
#     ax.plot_surface(X_forearm, Y_forearm, Z_forearm, color='green')

#     # --- Set Plot Limits and Labels ---
#     ax.set_xlim([-0.5, 0.5]); ax.set_ylim([-0.5, 0.5]); ax.set_zlim([-0.5, 0.5])
#     ax.set_xlabel('X Axis'); ax.set_ylabel('Y Axis'); ax.set_zlabel('Z Axis')
#     ax.set_title(f'Bicep Curl Animation (Frame {frame + 1}/{N_FRAMES})')
#     ax.view_init(elev=20, azim=-60)

# # --- Create and Display Animation ---
# print("Generating animation...")
# ani = FuncAnimation(fig, update, frames=N_FRAMES, interval=50, blit=False)
# plt.show()




import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.animation import FuncAnimation

# --- Data Loading and Parsing ---
try:
    df = pd.read_csv('quaternion_data.csv')
except FileNotFoundError:
    print("Error: 'quaternion_data.csv' not found.")
    print("Please make sure the CSV file is in the same directory as this Python script.")
    exit()

def parse_quaternions(series):
    """Converts a series of quaternion strings to a list of numpy arrays."""
    return series.apply(lambda x: np.fromstring(x, sep=',')).tolist()

quaternions_forearm = parse_quaternions(df['tracker_1_WXYZ'])
quaternions_upper_arm = parse_quaternions(df['tracker_2_WXYZ'])

# --- Constants ---
UPPER_ARM_LENGTH = 0.3
FOREARM_LENGTH = 0.25
N_FRAMES = len(df)

# --- Utility Functions ---
def quaternion_to_rotation_matrix(q):
    """Converts a quaternion into a rotation matrix."""
    w, x, y, z = q
    # Normalize quaternion
    q_norm = np.linalg.norm(q)
    if q_norm > 0:
        w, x, y, z = w/q_norm, x/q_norm, y/q_norm, z/q_norm
    
    return np.array([
        [1 - 2*y**2 - 2*z**2, 2*x*y - 2*z*w, 2*x*z + 2*y*w],
        [2*x*y + 2*z*w, 1 - 2*x**2 - 2*z**2, 2*y*z - 2*x*w],
        [2*x*z - 2*y*w, 2*y*z + 2*x*w, 1 - 2*x**2 - 2*y**2]
    ])

# --- Initial Pose Calibration ---
R_upper_arm_initial = quaternion_to_rotation_matrix(quaternions_upper_arm[0])
R_forearm_initial = quaternion_to_rotation_matrix(quaternions_forearm[0])
R_upper_arm_initial_inv = R_upper_arm_initial.T
R_forearm_initial_inv = R_forearm_initial.T

upper_arm_vec_ideal = np.array([0, -UPPER_ARM_LENGTH, 0])
forearm_vec_ideal = np.array([0, -FOREARM_LENGTH, 0])

# --- Geometry Creation Functions ---
def create_cylinder(p1, p2, radius):
    v = p2 - p1
    mag = np.linalg.norm(v)
    if mag < 1e-9: # Avoid division by zero for zero-length cylinders
        return np.array([]), np.array([]), np.array([])
        
    v = v / mag
    not_v = np.array([1, 0, 0])
    if (v == not_v).all():
        not_v = np.array([0, 1, 0])
    n1 = np.cross(v, not_v)
    n1 /= np.linalg.norm(n1)
    n2 = np.cross(v, n1)
    t = np.linspace(0, mag, 2)
    theta = np.linspace(0, 2 * np.pi, 10)
    t, theta2 = np.meshgrid(t, theta)
    X, Y, Z = [p1[i] + v[i] * t + radius * (n1[i] * np.cos(theta2) + n2[i] * np.sin(theta2)) for i in range(3)]
    return X, Y, Z

def create_sphere(center, radius, ax, zorder):
    """Creates a sphere using plot_surface for a 3D look."""
    u = np.linspace(0, 2 * np.pi, 20)
    v = np.linspace(0, np.pi, 20)
    x = radius * np.outer(np.cos(u), np.sin(v)) + center[0]
    y = radius * np.outer(np.sin(u), np.sin(v)) + center[1]
    z = radius * np.outer(np.ones(np.size(u)), np.cos(v)) + center[2]
    ax.plot_surface(x, y, z, color='b', zorder=zorder)

# --- Animation Setup ---
fig = plt.figure(figsize=(8, 8))
ax = fig.add_subplot(111, projection='3d')

def update(frame):
    ax.cla()

    # Get current rotations and calculate the change from the initial pose
    R_upper_arm_current = quaternion_to_rotation_matrix(quaternions_upper_arm[frame])
    R_forearm_current = quaternion_to_rotation_matrix(quaternions_forearm[frame])
    delta_R_upper = R_upper_arm_current @ R_upper_arm_initial_inv
    delta_R_forearm = R_forearm_current @ R_forearm_initial_inv

    # --- Hierarchical Joint-Based Calculation ---
    shoulder_pos = np.array([0, 0, 0])
    upper_arm_vector = delta_R_upper @ upper_arm_vec_ideal
    elbow_pos = shoulder_pos + upper_arm_vector
    forearm_vector = delta_R_forearm @ forearm_vec_ideal
    wrist_pos = elbow_pos + forearm_vector
    
    # --- Define Radii ---
    sphere_radius = 0.04  # Increased radius for better joint appearance
    cylinder_radius = 0.02

    # --- Adjust Cylinder Endpoints to Hide Inside Spheres ---
    # Calculate the direction of each arm segment
    vec_upper = elbow_pos - shoulder_pos
    vec_forearm = wrist_pos - elbow_pos
    dist_upper = np.linalg.norm(vec_upper)
    dist_forearm = np.linalg.norm(vec_forearm)

    # Calculate new, shortened endpoints for the cylinders
    p1_upper = shoulder_pos + (vec_upper / dist_upper) * sphere_radius if dist_upper > 0 else shoulder_pos
    p2_upper = elbow_pos - (vec_upper / dist_upper) * sphere_radius if dist_upper > 0 else elbow_pos
    
    p1_forearm = elbow_pos + (vec_forearm / dist_forearm) * sphere_radius if dist_forearm > 0 else elbow_pos
    p2_forearm = wrist_pos - (vec_forearm / dist_forearm) * sphere_radius if dist_forearm > 0 else wrist_pos

    # --- Draw Geometry ---
    # Draw the shortened cylinders
    X_upper, Y_upper, Z_upper = create_cylinder(p1_upper, p2_upper, cylinder_radius)
    if X_upper.size > 0:
      ax.plot_surface(X_upper, Y_upper, Z_upper, color='red', zorder=1)
      
    X_forearm, Y_forearm, Z_forearm = create_cylinder(p1_forearm, p2_forearm, cylinder_radius)
    if X_forearm.size > 0:
      ax.plot_surface(X_forearm, Y_forearm, Z_forearm, color='green', zorder=1)

    # Draw the larger spheres at the original joint positions
    create_sphere(shoulder_pos, sphere_radius, ax, zorder=2)
    create_sphere(elbow_pos, sphere_radius, ax, zorder=2)
    create_sphere(wrist_pos, sphere_radius, ax, zorder=2)

    # --- Set Plot Limits and Labels ---
    ax.set_xlim([-0.5, 0.5]); ax.set_ylim([-0.5, 0.5]); ax.set_zlim([-0.5, 0.5])
    ax.set_xlabel('X Axis'); ax.set_ylabel('Y Axis'); ax.set_zlabel('Z Axis')
    ax.set_title(f'Bicep Curl Animation (Frame {frame + 1}/{N_FRAMES})')
    ax.view_init(elev=20, azim=-60)

# --- Create and Display Animation ---
print("Generating animation...")
ani = FuncAnimation(fig, update, frames=N_FRAMES, interval=50, blit=False)
plt.show()