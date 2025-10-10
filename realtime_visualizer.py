import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.animation import FuncAnimation
import threading
from collections import deque
import time


class RealtimeArmVisualizer:
    """Real-time 3D visualization of arm movement from Movella DOT trackers"""
    
    def __init__(self, upper_arm_length=0.3, forearm_length=0.25):
        self.upper_arm_length = upper_arm_length
        self.forearm_length = forearm_length
        
        # Thread-safe quaternion buffer
        self.quat_lock = threading.Lock()
        self.current_quat_forearm = np.array([1, 0, 0, 0])  # w, x, y, z
        self.current_quat_upper_arm = np.array([1, 0, 0, 0])
        
        # Initial calibration quaternions
        self.initial_quat_forearm = None
        self.initial_quat_upper_arm = None
        self.is_calibrated = False
        
        # Visualization state
        self.is_running = False
        self.fig = None
        self.ax = None
        
        # Ideal arm vectors (straight down)
        self.upper_arm_vec_ideal = np.array([0, -self.upper_arm_length, 0])
        self.forearm_vec_ideal = np.array([0, -self.forearm_length, 0])
        
    def calibrate(self, quat_forearm, quat_upper_arm):
        """Set the initial reference orientation"""
        with self.quat_lock:
            self.initial_quat_forearm = np.array(quat_forearm)
            self.initial_quat_upper_arm = np.array(quat_upper_arm)
            self.is_calibrated = True
            print("Real-time visualizer calibrated!")
    
    def update_quaternions(self, quat_forearm, quat_upper_arm):
        """Update the current quaternion data (called from recording thread)"""
        with self.quat_lock:
            self.current_quat_forearm = np.array(quat_forearm)
            self.current_quat_upper_arm = np.array(quat_upper_arm)
    
    def quaternion_to_rotation_matrix(self, q):
        """Converts a quaternion into a rotation matrix"""
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
    
    def create_cylinder(self, p1, p2, radius):
        """Create a cylinder between two points"""
        v = p2 - p1
        mag = np.linalg.norm(v)
        v = v / mag if mag > 0 else np.array([0, 0, 1])
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
    
    def create_sphere(self, center, radius, ax):
        """Create a sphere at a point"""
        u = np.linspace(0, 2 * np.pi, 20)
        v = np.linspace(0, np.pi, 20)
        x = radius * np.outer(np.cos(u), np.sin(v)) + center[0]
        y = radius * np.outer(np.sin(u), np.sin(v)) + center[1]
        z = radius * np.outer(np.ones(np.size(u)), np.cos(v)) + center[2]
        ax.plot_surface(x, y, z, color='b')
    
    def update_frame(self, frame):
        """Update function called by FuncAnimation"""
        if not self.is_calibrated:
            return
        
        self.ax.cla()
        
        # Get current quaternions (thread-safe)
        with self.quat_lock:
            quat_forearm = self.current_quat_forearm.copy()
            quat_upper_arm = self.current_quat_upper_arm.copy()
        
        # Calculate rotation matrices
        R_upper_arm_current = self.quaternion_to_rotation_matrix(quat_upper_arm)
        R_forearm_current = self.quaternion_to_rotation_matrix(quat_forearm)
        
        R_upper_arm_initial = self.quaternion_to_rotation_matrix(self.initial_quat_upper_arm)
        R_forearm_initial = self.quaternion_to_rotation_matrix(self.initial_quat_forearm)
        
        # Calculate change in rotation from initial
        delta_R_upper = R_upper_arm_current @ R_upper_arm_initial.T
        delta_R_forearm = R_forearm_current @ R_forearm_initial.T
        
        # Apply to ideal arm vectors
        current_upper_arm_vec = delta_R_upper @ self.upper_arm_vec_ideal
        current_forearm_vec = delta_R_forearm @ self.forearm_vec_ideal
        
        # Calculate joint positions
        shoulder_pos = np.array([0, 0, 0])
        elbow_pos = shoulder_pos + current_upper_arm_vec
        wrist_pos = elbow_pos + current_forearm_vec
        
        # Draw geometry
        self.create_sphere(shoulder_pos, 0.03, self.ax)
        self.create_sphere(elbow_pos, 0.03, self.ax)
        self.create_sphere(wrist_pos, 0.03, self.ax)
        
        X_upper, Y_upper, Z_upper = self.create_cylinder(shoulder_pos, elbow_pos, 0.02)
        self.ax.plot_surface(X_upper, Y_upper, Z_upper, color='red', alpha=0.8)
        
        X_forearm, Y_forearm, Z_forearm = self.create_cylinder(elbow_pos, wrist_pos, 0.02)
        self.ax.plot_surface(X_forearm, Y_forearm, Z_forearm, color='green', alpha=0.8)
        
        # Set plot properties
        self.ax.set_xlim([-0.5, 0.5])
        self.ax.set_ylim([-0.5, 0.5])
        self.ax.set_zlim([-0.5, 0.5])
        self.ax.set_xlabel('X Axis')
        self.ax.set_ylabel('Y Axis')
        self.ax.set_zlabel('Z Axis')
        self.ax.set_title('Real-time Arm Tracking')
        self.ax.view_init(elev=20, azim=-60)
    
    def start(self):
        """Start the real-time visualization (blocking call)"""
        self.is_running = True
        
        # Create figure and axis
        self.fig = plt.figure(figsize=(10, 8))
        self.ax = self.fig.add_subplot(111, projection='3d')
        
        # Create animation (update at ~30 FPS)
        ani = FuncAnimation(self.fig, self.update_frame, interval=33, blit=False, cache_frame_data=False)
        
        plt.show()
        self.is_running = False
    
    def stop(self):
        """Stop the visualization"""
        self.is_running = False
        if self.fig:
            plt.close(self.fig)


def test_realtime_visualizer():
    """Test function with simulated data"""
    visualizer = RealtimeArmVisualizer()
    
    # Start with identity quaternions
    visualizer.calibrate([1, 0, 0, 0], [1, 0, 0, 0])
    
    # Simulate updating quaternions in a separate thread
    def simulate_movement():
        t = 0
        while visualizer.is_running:
            # Simulate bicep curl motion
            angle = np.sin(t * 0.1) * np.pi / 4  # Swing between 0 and 45 degrees
            
            # Forearm rotation (around x-axis)
            quat_forearm = [np.cos(angle/2), np.sin(angle/2), 0, 0]
            quat_upper_arm = [1, 0, 0, 0]  # Upper arm stays fixed
            
            visualizer.update_quaternions(quat_forearm, quat_upper_arm)
            
            t += 1
            time.sleep(0.05)
    
    # Start simulation thread
    sim_thread = threading.Thread(target=simulate_movement, daemon=True)
    sim_thread.start()
    
    # Start visualization (blocking)
    visualizer.start()


if __name__ == "__main__":
    test_realtime_visualizer()
