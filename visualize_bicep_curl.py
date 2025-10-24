
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
# R_upper_arm_initial = quaternion_to_rotation_matrix(quaternions_upper_arm[0])
# R_forearm_initial = quaternion_to_rotation_matrix(quaternions_forearm[0])
# R_upper_arm_initial_inv = R_upper_arm_initial.T
# R_forearm_initial_inv = R_forearm_initial.T

# upper_arm_vec_ideal = np.array([0, -UPPER_ARM_LENGTH, 0])
# forearm_vec_ideal = np.array([0, -FOREARM_LENGTH, 0])

# # --- Geometry Creation Functions ---
# def create_cylinder(p1, p2, radius):
#     v = p2 - p1
#     mag = np.linalg.norm(v)
#     if mag < 1e-9: # Avoid division by zero for zero-length cylinders
#         return np.array([]), np.array([]), np.array([])
        
#     v = v / mag
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

# def create_sphere(center, radius, ax, zorder):
#     """Creates a sphere using plot_surface for a 3D look."""
#     u = np.linspace(0, 2 * np.pi, 20)
#     v = np.linspace(0, np.pi, 20)
#     x = radius * np.outer(np.cos(u), np.sin(v)) + center[0]
#     y = radius * np.outer(np.sin(u), np.sin(v)) + center[1]
#     z = radius * np.outer(np.ones(np.size(u)), np.cos(v)) + center[2]
#     ax.plot_surface(x, y, z, color='b', zorder=zorder)

# # --- Animation Setup ---
# fig = plt.figure(figsize=(8, 8))
# ax = fig.add_subplot(111, projection='3d')

# def update(frame):
#     ax.cla()

#     # Get current rotations and calculate the change from the initial pose
#     R_upper_arm_current = quaternion_to_rotation_matrix(quaternions_upper_arm[frame])
#     R_forearm_current = quaternion_to_rotation_matrix(quaternions_forearm[frame])
#     delta_R_upper = R_upper_arm_current @ R_upper_arm_initial_inv
#     delta_R_forearm = R_forearm_current @ R_forearm_initial_inv

#     # --- Hierarchical Joint-Based Calculation ---
#     shoulder_pos = np.array([0, 0, 0])
#     upper_arm_vector = delta_R_upper @ upper_arm_vec_ideal
#     elbow_pos = shoulder_pos + upper_arm_vector
#     forearm_vector = delta_R_forearm @ forearm_vec_ideal
#     wrist_pos = elbow_pos + forearm_vector
    
#     # --- Define Radii ---
#     sphere_radius = 0.04  # Increased radius for better joint appearance
#     cylinder_radius = 0.02

#     # --- Adjust Cylinder Endpoints to Hide Inside Spheres ---
#     # Calculate the direction of each arm segment
#     vec_upper = elbow_pos - shoulder_pos
#     vec_forearm = wrist_pos - elbow_pos
#     dist_upper = np.linalg.norm(vec_upper)
#     dist_forearm = np.linalg.norm(vec_forearm)

#     # Calculate new, shortened endpoints for the cylinders
#     p1_upper = shoulder_pos + (vec_upper / dist_upper) * sphere_radius if dist_upper > 0 else shoulder_pos
#     p2_upper = elbow_pos - (vec_upper / dist_upper) * sphere_radius if dist_upper > 0 else elbow_pos
    
#     p1_forearm = elbow_pos + (vec_forearm / dist_forearm) * sphere_radius if dist_forearm > 0 else elbow_pos
#     p2_forearm = wrist_pos - (vec_forearm / dist_forearm) * sphere_radius if dist_forearm > 0 else wrist_pos

#     # --- Draw Geometry ---
#     # Draw the shortened cylinders
#     X_upper, Y_upper, Z_upper = create_cylinder(p1_upper, p2_upper, cylinder_radius)
#     if X_upper.size > 0:
#       ax.plot_surface(X_upper, Y_upper, Z_upper, color='red', zorder=1)
      
#     X_forearm, Y_forearm, Z_forearm = create_cylinder(p1_forearm, p2_forearm, cylinder_radius)
#     if X_forearm.size > 0:
#       ax.plot_surface(X_forearm, Y_forearm, Z_forearm, color='green', zorder=1)

#     # Draw the larger spheres at the original joint positions
#     create_sphere(shoulder_pos, sphere_radius, ax, zorder=2)
#     create_sphere(elbow_pos, sphere_radius, ax, zorder=2)
#     create_sphere(wrist_pos, sphere_radius, ax, zorder=2)

#     # --- Set Plot Limits and Labels ---
#     ax.set_xlim([-0.5, 0.5]); ax.set_ylim([-0.5, 0.5]); ax.set_zlim([-0.5, 0.5])
#     ax.set_xlabel('X Axis'); ax.set_ylabel('Y Axis'); ax.set_zlabel('Z Axis')
#     ax.set_title(f'Bicep Curl Animation (Frame {frame + 1}/{N_FRAMES})')
#     ax.view_init(elev=20, azim=-60)

# # --- Create and Display Animation ---
# print("Generating animation...")
# ani = FuncAnimation(fig, update, frames=N_FRAMES, interval=50, blit=False)
# plt.show()


















# import pandas as pd
# import numpy as np
# import matplotlib.pyplot as plt
# from mpl_toolkits.mplot3d import Axes3D
# from matplotlib.animation import FuncAnimation
# from scipy.spatial.transform import Rotation as R
# import re

# # --- Constants & Configuration ---
# UPPER_ARM_LENGTH = 0.3  # Length of the upper arm in meters
# FOREARM_LENGTH = 0.25   # Length of the forearm in meters
# SHOULDER_WIDTH = 0.35   # Distance between shoulders
# SPHERE_RADIUS = 0.03    # Radius for the joint spheres
# CYLINDER_RADIUS = 0.015 # Radius for the arm cylinders

# # --- Data Loading and Parsing ---
# try:
#     df = pd.read_csv('quaternion_data.csv')
# except FileNotFoundError:
#     print("Error: 'quaternion_data.csv' not found.")
#     exit()

# def parse_quaternions(series):
#     """Converts a series of 'W,X,Y,Z' strings into a list of numpy arrays."""
#     def parse_vector_string(s):
#         cleaned_s = re.sub(r'[^\d.,-]', '', s)
#         try:
#             return np.fromstring(cleaned_s, sep=',')
#         except ValueError:
#             return np.array([1.0, 0.0, 0.0, 0.0]) # Default neutral quaternion on error
#     return series.apply(parse_vector_string).tolist()

# # Load quaternions for all four trackers
# quaternions = {
#     'left_forearm': parse_quaternions(df['tracker_1_WXYZ']),
#     'left_upper_arm': parse_quaternions(df['tracker_2_WXYZ']),
#     'right_forearm': parse_quaternions(df['tracker_3_WXYZ']),
#     'right_upper_arm': parse_quaternions(df['tracker_4_WXYZ'])
# }
# N_FRAMES = len(df)

# # --- Initial Pose Calibration (T-Pose Correction) ---
# # We use the inverse of the first frame's rotation to establish a "neutral" T-pose.
# initial_rotations_inv = {}
# for key in quaternions:
#     q_initial = quaternions[key][0]
#     # Scipy expects (x, y, z, w) format, our data is (w, x, y, z)
#     initial_rotations_inv[key] = R.from_quat(np.roll(q_initial, -1)).inv()

# # The "ideal" vectors for arm segments in the T-pose (X-axis points down the arm).
# upper_arm_vec_ideal = np.array([UPPER_ARM_LENGTH, 0, 0])
# forearm_vec_ideal = np.array([FOREARM_LENGTH, 0, 0])

# # --- Geometry Creation Functions for Matplotlib ---
# def create_cylinder(ax, p1, p2, radius, color):
#     """Draws a cylinder between two points on the given Matplotlib axis."""
#     v = p2 - p1
#     mag = np.linalg.norm(v)
#     if mag == 0: return
#     v = v / mag
#     not_v = np.array([1, 0, 0])
#     if (v == not_v).all():
#         not_v = np.array([0, 1, 0])
#     n1 = np.cross(v, not_v)
#     n1 /= np.linalg.norm(n1)
#     n2 = np.cross(v, n1)
#     t = np.linspace(0, mag, 2)
#     theta = np.linspace(0, 2 * np.pi, 10)
#     t, theta = np.meshgrid(t, theta)
#     X, Y, Z = [p1[i] + v[i] * t + radius * (n1[i] * np.cos(theta) + n2[i] * np.sin(theta)) for i in [0, 1, 2]]
#     ax.plot_surface(X, Y, Z, color=color, zorder=1)

# def create_sphere(ax, center, radius, color):
#     """Draws a sphere at a given center point."""
#     u, v = np.mgrid[0:2*np.pi:20j, 0:np.pi:10j]
#     x = center[0] + radius * np.cos(u) * np.sin(v)
#     y = center[1] + radius * np.sin(u) * np.sin(v)
#     z = center[2] + radius * np.cos(v)
#     ax.plot_surface(x, y, z, color=color, zorder=2)

# # --- Animation Setup ---
# fig = plt.figure(figsize=(10, 10))
# ax = fig.add_subplot(111, projection='3d')

# def update(frame):
#     ax.cla()

#     # --- Calculate Rotational Changes from Initial Pose ---
#     delta_R = {}
#     for key in quaternions:
#         q_current = quaternions[key][frame]
#         R_current = R.from_quat(np.roll(q_current, -1))
#         delta_R[key] = R_current * initial_rotations_inv[key]
    
#     # --- Hierarchical Forward Kinematics ---
#     left_shoulder_pos = np.array([0, -SHOULDER_WIDTH / 2, 0])
#     right_shoulder_pos = np.array([0, SHOULDER_WIDTH / 2, 0])
    
#     # Left Arm
#     R_world_lu = delta_R['left_upper_arm']
#     left_elbow_pos = left_shoulder_pos + R_world_lu.apply(upper_arm_vec_ideal)
#     # The forearm's world rotation is the upper arm's rotation followed by the forearm's rotation
#     R_world_lf = R_world_lu * delta_R['left_forearm']
#     left_wrist_pos = left_elbow_pos + R_world_lf.apply(forearm_vec_ideal)

#     # Right Arm
#     R_world_ru = delta_R['right_upper_arm']
#     right_elbow_pos = right_shoulder_pos + R_world_ru.apply(upper_arm_vec_ideal)
#     # Apply the same hierarchical logic to the right arm
#     R_world_rf = R_world_ru * delta_R['right_forearm']
#     right_wrist_pos = right_elbow_pos + R_world_rf.apply(forearm_vec_ideal)
    
#     # --- Draw the Skeleton ---
#     # Draw Spheres for all joints
#     create_sphere(ax, left_shoulder_pos, SPHERE_RADIUS, color='green')
#     create_sphere(ax, right_shoulder_pos, SPHERE_RADIUS, color='blue')
#     create_sphere(ax, left_elbow_pos, SPHERE_RADIUS, color='lime')
#     create_sphere(ax, right_elbow_pos, SPHERE_RADIUS, color='cyan')
#     create_sphere(ax, left_wrist_pos, SPHERE_RADIUS, color='yellow')
#     create_sphere(ax, right_wrist_pos, SPHERE_RADIUS, color='magenta')
    
#     # Draw Cylinders for all limbs
#     create_cylinder(ax, left_shoulder_pos, right_shoulder_pos, CYLINDER_RADIUS, color='grey')
#     create_cylinder(ax, left_shoulder_pos, left_elbow_pos, CYLINDER_RADIUS, color='green')
#     create_cylinder(ax, right_shoulder_pos, right_elbow_pos, CYLINDER_RADIUS, color='blue')
#     create_cylinder(ax, left_elbow_pos, left_wrist_pos, CYLINDER_RADIUS, color='lime')
#     create_cylinder(ax, right_elbow_pos, right_wrist_pos, CYLINDER_RADIUS, color='cyan')

#     # --- Set Plot Style and Limits ---
#     ax.set_xlim([-0.6, 0.6]); ax.set_ylim([-0.6, 0.6]); ax.set_zlim([-0.6, 0.6])
#     ax.set_xlabel('X'); ax.set_ylabel('Y'); ax.set_zlabel('Z')
#     ax.set_title(f'Bicep Curl Animation (Frame {frame + 1}/{N_FRAMES})')
#     ax.view_init(elev=-90, azim=0)

# # --- Create and Run Animation ---
# print("Generating animation... This may take a moment.")
# ani = FuncAnimation(fig, update, frames=N_FRAMES, interval=50, blit=False)
# plt.tight_layout()
# plt.show()












# import pandas as pd
# import numpy as np
# import open3d as o3d
# from scipy.spatial.transform import Rotation as R
# import re

# # --- Constants & Configuration ---
# UPPER_ARM_LENGTH = 0.3
# FOREARM_LENGTH = 0.25
# SHOULDER_WIDTH = 0.35

# # --- Data Loading and Parsing ---
# def parse_and_prepare_data(csv_path):
#     """Loads and parses the specific CSV format for visualization."""
#     try:
#         df_raw = pd.read_csv(csv_path)
#     except FileNotFoundError:
#         print(f"Error: '{csv_path}' not found.")
#         return None

#     def parse_vector_string(s):
#         cleaned_s = re.sub(r'[^\d.,-]', '', s)
#         try:
#             arr = np.fromstring(cleaned_s, sep=',')
#             if arr.shape[0] != 4: return np.array([1.0, 0.0, 0.0, 0.0])
#             return arr
#         except ValueError:
#             return np.array([1.0, 0.0, 0.0, 0.0])

#     df_clean = pd.DataFrame()
#     for i in range(1, 5):
#         col_name = f'tracker_{i}_WXYZ'
#         if col_name in df_raw.columns:
#             temp_df = pd.DataFrame(df_raw[col_name].apply(parse_vector_string).tolist(),
#                                    columns=[f'q{i}_w', f'q{i}_x', f'q{i}_y', f'q{i}_z'])
#             df_clean = pd.concat([df_clean, temp_df], axis=1)
#         else:
#             print(f"Warning: Column '{col_name}' not found.")
#             return None
#     return df_clean

# # --- Geometry Creation Functions ---
# def create_cylinder_mesh(p1, p2, radius=0.015, color=[0.5, 0.5, 0.5]):
#     """Creates a robust Open3D cylinder mesh between two points."""
#     vector = p2 - p1
#     length = np.linalg.norm(vector)
#     if length < 1e-6: return None

#     cylinder = o3d.geometry.TriangleMesh.create_cylinder(radius=radius, height=length)
    
#     # Handle the rotation to align the cylinder
#     z_axis = np.array([0, 0, 1])
#     vec_norm = vector / length
#     rotation_axis = np.cross(z_axis, vec_norm)
#     rotation_angle = np.arccos(np.dot(z_axis, vec_norm))
    
#     if np.isclose(rotation_angle, 0):
#         rotation_matrix = np.identity(3)
#     elif np.isclose(rotation_angle, np.pi):
#         rotation_matrix = R.from_rotvec(np.pi * np.array([1, 0, 0])).as_matrix()
#     else:
#         rotation_axis_norm = rotation_axis / np.linalg.norm(rotation_axis)
#         rotation_matrix = R.from_rotvec(rotation_angle * rotation_axis_norm).as_matrix()
    
#     cylinder.rotate(rotation_matrix, center=(0, 0, 0))
#     cylinder.translate((p1 + p2) / 2)
#     cylinder.paint_uniform_color(color)
#     return cylinder

# def create_sphere_mesh(center, radius=0.03, color=[0.8, 0.1, 0.1]):
#     """Creates an Open3D sphere mesh."""
#     sphere = o3d.geometry.TriangleMesh.create_sphere(radius=radius)
#     sphere.translate(center)
#     sphere.paint_uniform_color(color)
#     return sphere

# def visualize_bicep_curl(df):
#     """Main visualization function using Open3D."""
#     if df is None or df.empty:
#         print("Dataframe is empty. Halting visualization.")
#         return

#     N_FRAMES = len(df) # Fix: Define N_FRAMES inside the function scope

#     # --- Initialize Visualizer ---
#     vis = o3d.visualization.Visualizer()
#     vis.create_window(window_name="Bicep Curl Visualization", width=1280, height=720)
    
#     # --- Initial Pose Calibration ---
#     initial_rotations_inv = {}
#     quaternion_keys = {
#         'left_forearm': ('q1_w', 'q1_x', 'q1_y', 'q1_z'),
#         'left_upper_arm': ('q2_w', 'q2_x', 'q2_y', 'q2_z'),
#         'right_forearm': ('q3_w', 'q3_x', 'q3_y', 'q3_z'),
#         'right_upper_arm': ('q4_w', 'q4_x', 'q4_y', 'q4_z')
#     }
#     for key, cols in quaternion_keys.items():
#         q_initial = df.loc[0, list(cols)].values
#         initial_rotations_inv[key] = R.from_quat(np.roll(q_initial, -1)).inv()
    
#     # Define ideal vectors for an A-pose (arms pointing down along negative Z-axis)
#     upper_arm_vec_ideal = np.array([0, 0, -UPPER_ARM_LENGTH])
#     forearm_vec_ideal = np.array([0, 0, -FOREARM_LENGTH])

#     # Placeholder for geometries
#     geometries = {}
#     is_first_frame = True

#     # --- Animation Loop ---
#     for i in range(N_FRAMES):
#         # --- Kinematics Calculation ---
#         delta_R = {}
#         for key, cols in quaternion_keys.items():
#             q_current = df.loc[i, list(cols)].values
#             R_current = R.from_quat(np.roll(q_current, -1))
#             delta_R[key] = R_current * initial_rotations_inv[key]
        
#         left_shoulder_pos = np.array([0, -SHOULDER_WIDTH / 2, 0])
#         right_shoulder_pos = np.array([0, SHOULDER_WIDTH / 2, 0])
        
#         # Apply the correct hierarchical kinematics from the 2-sensor example
#         left_upper_arm_vec = delta_R['left_upper_arm'].apply(upper_arm_vec_ideal)
#         left_elbow_pos = left_shoulder_pos + left_upper_arm_vec
#         left_forearm_vec = delta_R['left_forearm'].apply(forearm_vec_ideal)
#         left_wrist_pos = left_elbow_pos + left_forearm_vec

#         right_upper_arm_vec = delta_R['right_upper_arm'].apply(upper_arm_vec_ideal)
#         right_elbow_pos = right_shoulder_pos + right_upper_arm_vec
#         right_forearm_vec = delta_R['right_forearm'].apply(forearm_vec_ideal)
#         right_wrist_pos = right_elbow_pos + right_forearm_vec

#         # --- Update Geometries ---
#         if not is_first_frame:
#             for geom in geometries.values():
#                 if geom is not None:
#                     vis.remove_geometry(geom, reset_bounding_box=False)

#         geometries = {
#             "left_shoulder": create_sphere_mesh(left_shoulder_pos, color=[0.0, 0.8, 0.0]),
#             "right_shoulder": create_sphere_mesh(right_shoulder_pos, color=[0.0, 0.0, 0.8]),
#             "left_elbow": create_sphere_mesh(left_elbow_pos, color=[0.5, 1.0, 0.5]),
#             "right_elbow": create_sphere_mesh(right_elbow_pos, color=[0.5, 0.5, 1.0]),
#             "left_wrist": create_sphere_mesh(left_wrist_pos, color=[1.0, 1.0, 0.0]),
#             "right_wrist": create_sphere_mesh(right_wrist_pos, color=[1.0, 0.0, 1.0]),
#             "torso": create_cylinder_mesh(left_shoulder_pos, right_shoulder_pos),
#             "left_upper_arm": create_cylinder_mesh(left_shoulder_pos, left_elbow_pos, color=[0.0, 0.8, 0.0]),
#             "left_forearm": create_cylinder_mesh(left_elbow_pos, left_wrist_pos, color=[0.5, 1.0, 0.5]),
#             "right_upper_arm": create_cylinder_mesh(right_shoulder_pos, right_elbow_pos, color=[0.0, 0.0, 0.8]),
#             "right_forearm": create_cylinder_mesh(right_elbow_pos, right_wrist_pos, color=[0.5, 0.5, 1.0]),
#         }

#         for name, geom in geometries.items():
#             if geom is not None:
#                 vis.add_geometry(geom, reset_bounding_box=False)
        
#         if is_first_frame:
#             # Add a coordinate frame for reference
#             vis.add_geometry(o3d.geometry.TriangleMesh.create_coordinate_frame(size=0.2), reset_bounding_box=False)
#             # Set camera view on the first frame
#             view_control = vis.get_view_control()
#             view_control.set_front([0.5, -0.2, -0.3])
#             view_control.set_lookat([0, 0, -0.3])
#             view_control.set_up([0, 0, 1])
#             view_control.set_zoom(0.7)
#             is_first_frame = False
        
#         vis.poll_events()
#         vis.update_renderer()

#     vis.run()
#     vis.destroy_window()

# # --- Main Execution ---
# if __name__ == "__main__":
#     quaternion_df = parse_and_prepare_data("quaternion_data.csv")
#     visualize_bicep_curl(quaternion_df)











import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.animation import FuncAnimation
import csv

# --- Constants for the Skeleton Model ---
SHOULDER_WIDTH = 0.5  # Total width between shoulders
UPPER_ARM_LENGTH = 0.4 # Length from shoulder to elbow
FOREARM_LENGTH = 0.35  # Length from elbow to hand

# Define the skeleton joints in a base "T-pose"
# Origin (0,0,0) is the center of the shoulders
LEFT_SHOULDER = np.array([-SHOULDER_WIDTH / 2, 0, 0])
RIGHT_SHOULDER = np.array([SHOULDER_WIDTH / 2, 0, 0])

# Define the arm segments as vectors in the T-pose
# Left arm points down the -X axis
VEC_LEFT_UPPER_ARM = np.array([-UPPER_ARM_LENGTH, 0, 0])
VEC_LEFT_FOREARM = np.array([-FOREARM_LENGTH, 0, 0])

# Right arm points down the +X axis
VEC_RIGHT_UPPER_ARM = np.array([UPPER_ARM_LENGTH, 0, 0])
VEC_RIGHT_FOREARM = np.array([FOREARM_LENGTH, 0, 0])


def load_quaternion_data(filepath):
    """
    Loads the quaternion data from the specified CSV file.

    Expected CSV format:
    header_row
    "q1_w,q1_x,q1_y,q1_z","q2_w,q2_x,q2_y,q2_z",...

    Args:
        filepath (str): The path to the 'quaternion_data.csv' file.

    Returns:
        Tuple[np.array, np.array, np.array, np.array]:
        Numpy arrays for (q_L_forearm, q_L_upperarm, q_R_forearm, q_R_upperarm)
        Each array has a shape of (num_frames, 4), assumed WXYZ order initially.
    """
    all_q1 = [] # Tracker 1: Left Forearm
    all_q2 = [] # Tracker 2: Left Upper Arm
    all_q3 = [] # Tracker 3: Right Forearm
    all_q4 = [] # Tracker 4: Right Upper Arm

    print(f"Loading data from {filepath}...")
    try:
        with open(filepath, 'r', newline='') as f:
            reader = csv.reader(f)

            # Skip the header row
            try:
                header = next(reader)
            except StopIteration:
                print("Error: CSV file is empty.")
                return None, None, None, None

            for row in reader:
                # Skip empty rows that might be at the end of the file
                if not row:
                    continue

                try:
                    # row[0] is "w,x,y,z" for tracker 1
                    # row[1] is "w,x,y,z" for tracker 2
                    # ...
                    # Assuming WXYZ order from CSV, will be converted later if needed
                    all_q1.append([float(v) for v in row[0].split(',')])
                    all_q2.append([float(v) for v in row[1].split(',')])
                    all_q3.append([float(v) for v in row[2].split(',')])
                    all_q4.append([float(v) for v in row[3].split(',')])

                except (ValueError, IndexError) as e:
                    print(f"Warning: Skipping malformed row: {row}. Error: {e}")
                    continue

    except FileNotFoundError:
        print(f"Error: File not found at {filepath}")
        return None, None, None, None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None, None, None, None

    print(f"Successfully loaded {len(all_q1)} frames of data.")

    # Convert lists to numpy arrays for efficient processing
    return (np.array(all_q1), np.array(all_q2),
            np.array(all_q3), np.array(all_q4))


def rotate_vector_wxyz(v, q_wxyz):
    """
    Rotates a vector 'v' by a quaternion 'q' using only numpy,
    assuming WXYZ order [w, x, y, z].

    Args:
        v (np.array): The 3D vector [x, y, z] to be rotated.
        q_wxyz (np.array): The 4D quaternion [w, x, y, z].

    Returns:
        np.array: The rotated 3D vector.
    """
    # Normalize the quaternion just in case
    q_norm = np.linalg.norm(q_wxyz)
    if q_norm < 1e-9: # Avoid division by zero if quaternion is invalid
        return v
    q = q_wxyz / q_norm

    w = q[0]
    v_q = q[1:] # The vector part of the quaternion [x, y, z]

    # Formula: v' = v + 2*w*(v_q x v) + 2*(v_q x (v_q x v))
    t = 2 * np.cross(v_q, v)
    v_prime = v + w * t + np.cross(v_q, t)

    return v_prime


def rotate_vector_xyzw(v, q_xyzw):
    """
    Rotates a vector 'v' by a quaternion 'q' using only numpy,
    assuming XYZW order [x, y, z, w].

    Args:
        v (np.array): The 3D vector [x, y, z] to be rotated.
        q_xyzw (np.array): The 4D quaternion [x, y, z, w].

    Returns:
        np.array: The rotated 3D vector.
    """
    # Normalize the quaternion just in case
    q_norm = np.linalg.norm(q_xyzw)
    if q_norm < 1e-9: # Avoid division by zero if quaternion is invalid
        return v
    q = q_xyzw / q_norm

    w = q[3]      # w is the last element
    v_q = q[:3]   # Vector part [x, y, z]

    # Same formula as before, just different component indexing
    t = 2 * np.cross(v_q, v)
    v_prime = v + w * t + np.cross(v_q, t)

    return v_prime


def main(csv_filepath):
    """
    Main function to load data and run the 3D animation.
    """
    # Load the data (assumes WXYZ order initially from CSV)
    (q_L_forearm_raw, q_L_upperarm_raw,
     q_R_forearm_raw, q_R_upperarm_raw) = load_quaternion_data(csv_filepath)

    if q_L_forearm_raw is None or len(q_L_forearm_raw) == 0:
        print("Data loading failed or file is empty. Exiting.")
        return

    # --- Convert WXYZ to XYZW ---
    # The loading function assumes WXYZ, but the rotation function uses XYZW.
    # Convert by rolling the array elements: [w,x,y,z] -> [x,y,z,w]
    q_L_forearm = np.roll(q_L_forearm_raw, -1, axis=1)
    q_L_upperarm = np.roll(q_L_upperarm_raw, -1, axis=1)
    q_R_forearm = np.roll(q_R_forearm_raw, -1, axis=1)
    q_R_upperarm = np.roll(q_R_upperarm_raw, -1, axis=1)
    # ----------------------------------------

    num_frames = len(q_L_forearm)

    # --- Set up the 3D Plot ---
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    ax.set_title("3D Arm Movement Visualization")

    # Set fixed axis limits to prevent the plot from resizing
    axis_limit = (SHOULDER_WIDTH + UPPER_ARM_LENGTH + FOREARM_LENGTH) * 0.7
    ax.set_xlim([-axis_limit, axis_limit])
    ax.set_ylim([-axis_limit, axis_limit])
    ax.set_zlim([-axis_limit, axis_limit])

    ax.set_xlabel("X (Right/Left)")
    ax.set_ylabel("Y (Forward/Back)")
    ax.set_zlabel("Z (Up/Down)")

    # Set aspect ratio to be equal
    ax.set_box_aspect([1, 1, 1])

    # Change the view angle (elevation, azimuth)
    ax.view_init(elev=20, azim=-70)

    # --- Initialize Plot Lines ---
    torso_line, = ax.plot([], [], [], 'k-', linewidth=3, label="Torso")
    left_arm_line, = ax.plot([], [], [], 'b-o', linewidth=2, label="Left Arm")
    right_arm_line, = ax.plot([], [], [], 'r-o', linewidth=2, label="Right Arm")
    ax.legend()
    frame_text = ax.text(0.05, 0.95, 0.95, '', transform=ax.transAxes)

    # --- Animation Functions ---

    def init_animation():
        """Initializes the animation plot."""
        torso_line.set_data_3d([], [], [])
        left_arm_line.set_data_3d([], [], [])
        right_arm_line.set_data_3d([], [], [])
        frame_text.set_text('')
        return torso_line, left_arm_line, right_arm_line, frame_text

    def update_animation(i):
        """
        Updates the plot for the i-th frame of the animation.
        """
        # Get the XYZW quaternions for the current frame
        q1 = q_L_forearm[i]  # Left Forearm
        q2 = q_L_upperarm[i] # Left Upper Arm
        q3 = q_R_forearm[i]  # Right Forearm
        q4 = q_R_upperarm[i] # Right Upper Arm

        # --- *** CORRECTION: Invert vector part (x,y,z) for right arm quaternions *** ---
        # This often fixes mirroring issues related to coordinate system differences.
        q3_corrected = np.copy(q3)
        q3_corrected[0:3] = -q3_corrected[0:3] # Invert x, y, z

        q4_corrected = np.copy(q4)
        q4_corrected[0:3] = -q4_corrected[0:3] # Invert x, y, z
        # --- *** END CORRECTION *** ---


        # --- Calculate rotated segment vectors using XYZW quaternions ---
        # Left Arm
        vec_L_upper_rot = rotate_vector_xyzw(VEC_LEFT_UPPER_ARM, q2)
        vec_L_forearm_rot = rotate_vector_xyzw(VEC_LEFT_FOREARM, q1)

        # Right Arm - USE CORRECTED QUATERNIONS
        vec_R_upper_rot = rotate_vector_xyzw(VEC_RIGHT_UPPER_ARM, q4_corrected)
        vec_R_forearm_rot = rotate_vector_xyzw(VEC_RIGHT_FOREARM, q3_corrected)

        # --- Calculate 3D Joint Positions (Forward Kinematics) ---
        # Left Arm Joints
        left_elbow = LEFT_SHOULDER + vec_L_upper_rot
        left_hand = left_elbow + vec_L_forearm_rot

        # Right Arm Joints
        right_elbow = RIGHT_SHOULDER + vec_R_upper_rot
        right_hand = right_elbow + vec_R_forearm_rot

        # --- Update the plot lines with new data ---
        torso_pts = np.array([LEFT_SHOULDER, RIGHT_SHOULDER])
        torso_line.set_data_3d(torso_pts[:, 0], torso_pts[:, 1], torso_pts[:, 2])

        left_arm_pts = np.array([LEFT_SHOULDER, left_elbow, left_hand])
        left_arm_line.set_data_3d(left_arm_pts[:, 0], left_arm_pts[:, 1], left_arm_pts[:, 2])

        right_arm_pts = np.array([RIGHT_SHOULDER, right_elbow, right_hand])
        right_arm_line.set_data_3d(right_arm_pts[:, 0], right_arm_pts[:, 1], right_arm_pts[:, 2])

        frame_text.set_text(f'Frame: {i}/{num_frames}')

        return torso_line, left_arm_line, right_arm_line, frame_text

    # --- Run the Animation ---
    ani = FuncAnimation(
        fig,
        update_animation,
        frames=num_frames,
        init_func=init_animation,
        blit=True,
        interval=16, # ~30fps playback
        repeat=True
    )

    print("Starting animation... Close the plot window to exit.")
    plt.show()


if __name__ == "__main__":
    main('quaternion_data.csv')

