import tkinter as tk
from tkinter import ttk, messagebox
import cv2
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import threading
import time
from collections import deque

class LiveRecordingApp:
    def __init__(self, root, dot_manager=None):
        self.root = root
        self.root.title("Live Recording - Movella DOT")
        self.root.geometry("1600x1000")
        
        # Store the manager from device setup
        self.dot_manager = dot_manager
        self.recording = False
        
        # Store latest quaternion data for visualization
        self.latest_quaternions = {}
        if self.dot_manager:
            mapping = self.dot_manager.get_body_position_mapping()
            for pos_key in mapping.keys():
                self.latest_quaternions[pos_key] = np.array([1.0, 0.0, 0.0, 0.0])  # w,x,y,z
        
        self.start_time = None
        self.frame_count = 0
        
        # Arm segment lengths (in meters)
        self.UPPER_ARM_LENGTH = 0.3
        self.FOREARM_LENGTH = 0.25
        self.SHOULDER_WIDTH = 0.35
        
        # Create UI
        self.setup_ui()
        
        # Initialize camera
        self.vid = cv2.VideoCapture(0)
        self.vid.set(cv2.CAP_PROP_FRAME_WIDTH, 800)
        self.vid.set(cv2.CAP_PROP_FRAME_HEIGHT, 600)
        
        self.camera_running = False
        
    def setup_ui(self):
        """Setup the user interface"""
        # Top container for camera and visualization
        self.top_container = tk.Frame(self.root, height=700)
        self.top_container.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # Left side - Camera Feed
        self.left_frame = tk.Frame(self.top_container, bg='black', width=800)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.left_frame.pack_propagate(False)
        
        # Camera label
        self.camera_label = tk.Label(self.left_frame, bg='black')
        self.camera_label.pack(fill=tk.BOTH, expand=True)
        
        # Right side - 3D Visualization
        self.right_frame = tk.Frame(self.top_container, bg='white', width=800)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.right_frame.pack_propagate(False)
        
        # Setup 3D visualization
        self.setup_3d_visualization()
        
        # Bottom control panel
        self.bottom_frame = tk.Frame(self.root, bg='#34495e', height=300)
        self.bottom_frame.pack(side=tk.BOTTOM, fill=tk.BOTH)
        self.bottom_frame.pack_propagate(False)
        
        self.setup_control_panel()
        
    def setup_3d_visualization(self):
        """Setup 3D arm visualization using matplotlib"""
        self.fig = plt.figure(figsize=(8, 6))
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.ax.set_title('Live 3D Arm Visualization', fontsize=12, fontweight='bold')
        
        # Set fixed axis limits
        axis_limit = (self.SHOULDER_WIDTH + self.UPPER_ARM_LENGTH + self.FOREARM_LENGTH) * 0.7
        self.ax.set_xlim([-axis_limit, axis_limit])
        self.ax.set_ylim([-axis_limit, axis_limit])
        self.ax.set_zlim([-axis_limit, axis_limit])
        
        self.ax.set_xlabel("X (Right/Left)")
        self.ax.set_ylabel("Y (Forward/Back)")
        self.ax.set_zlabel("Z (Up/Down)")
        
        self.ax.set_box_aspect([1, 1, 1])
        self.ax.view_init(elev=20, azim=-70)
        
        # Initialize plot lines
        self.torso_line, = self.ax.plot([], [], [], 'k-', linewidth=3, label="Torso")
        self.left_upper_cyl = None
        self.left_lower_cyl = None
        self.right_upper_cyl = None
        self.right_lower_cyl = None
        
        # Embed in tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.right_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
    def create_cylinder(self, p1, p2, radius, color):
        """Create a cylinder between two points"""
        v = p2 - p1
        mag = np.linalg.norm(v)
        if mag < 1e-9:
            return None
            
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
        X = p1[0] + v[0] * t + radius * (n1[0] * np.cos(theta2) + n2[0] * np.sin(theta2))
        Y = p1[1] + v[1] * t + radius * (n1[1] * np.cos(theta2) + n2[1] * np.sin(theta2))
        Z = p1[2] + v[2] * t + radius * (n1[2] * np.cos(theta2) + n2[2] * np.sin(theta2))
        
        return self.ax.plot_surface(X, Y, Z, color=color, alpha=0.8)
    
    def create_sphere(self, center, radius, color):
        """Create a sphere at joint positions"""
        u = np.linspace(0, 2 * np.pi, 20)
        v = np.linspace(0, np.pi, 20)
        x = radius * np.outer(np.cos(u), np.sin(v)) + center[0]
        y = radius * np.outer(np.sin(u), np.sin(v)) + center[1]
        z = radius * np.outer(np.ones(np.size(u)), np.cos(v)) + center[2]
        return self.ax.plot_surface(x, y, z, color=color, alpha=0.9)
    
    def rotate_vector(self, v, q):
        """Rotate vector v by quaternion q (w,x,y,z format)"""
        q_norm = np.linalg.norm(q)
        if q_norm < 1e-9:
            return v
        q = q / q_norm
        
        w = q[0]
        v_q = q[1:]  # Vector part [x, y, z]
        
        t = 2 * np.cross(v_q, v)
        v_prime = v + w * t + np.cross(v_q, t)
        
        return v_prime
        
    def setup_control_panel(self):
        """Setup the control panel"""
        # Title
        title_label = tk.Label(self.bottom_frame, 
                              text="🎮 Control Panel",
                              font=('Arial', 16, 'bold'), 
                              bg='#34495e', fg='white')
        title_label.pack(pady=10)
        
        # Main controls frame
        controls_container = tk.Frame(self.bottom_frame, bg='#34495e')
        controls_container.pack(pady=10)
        
        # Recording controls
        recording_frame = tk.LabelFrame(controls_container, 
                                       text="Recording Controls",
                                       font=('Arial', 11, 'bold'),
                                       bg='#34495e', fg='white',
                                       padx=20, pady=10)
        recording_frame.pack(side=tk.LEFT, padx=10)
        
        self.start_btn = tk.Button(recording_frame, 
                                   text="▶️ Start Recording",
                                   command=self.start_recording,
                                   font=('Arial', 12, 'bold'),
                                   bg='#27ae60', fg='white',
                                   padx=20, pady=10,
                                   cursor='hand2')
        self.start_btn.pack(pady=5)
        
        self.stop_btn = tk.Button(recording_frame,
                                  text="⏹️ Stop Recording",
                                  command=self.stop_recording,
                                  font=('Arial', 12, 'bold'),
                                  bg='#c0392b', fg='white',
                                  padx=20, pady=10,
                                  cursor='hand2',
                                  state='disabled')
        self.stop_btn.pack(pady=5)
        
        # Camera controls
        camera_frame = tk.LabelFrame(controls_container,
                                    text="Camera Controls",
                                    font=('Arial', 11, 'bold'),
                                    bg='#34495e', fg='white',
                                    padx=20, pady=10)
        camera_frame.pack(side=tk.LEFT, padx=10)
        
        self.camera_btn = tk.Button(camera_frame,
                                    text="📹 Start Camera",
                                    command=self.toggle_camera,
                                    font=('Arial', 12),
                                    bg='#3498db', fg='white',
                                    padx=20, pady=10,
                                    cursor='hand2')
        self.camera_btn.pack(pady=5)
        
        # Status panel
        status_container = tk.Frame(self.bottom_frame, bg='#34495e')
        status_container.pack(pady=5)
        
        status_frame = tk.Frame(status_container, bg='#2c3e50', relief=tk.SUNKEN, bd=2)
        status_frame.pack(pady=5)
        
        self.status_label = tk.Label(status_frame,
                                     text="⚪ Status: Stopped",
                                     font=('Arial', 11, 'bold'),
                                     bg='#2c3e50', fg='white',
                                     padx=20, pady=5)
        self.status_label.pack(side=tk.LEFT, padx=10)
        
        self.time_label = tk.Label(status_frame,
                                   text="⏱️ Time: 0.0s",
                                   font=('Arial', 11),
                                   bg='#2c3e50', fg='white',
                                   padx=20, pady=5)
        self.time_label.pack(side=tk.LEFT, padx=10)
        
        self.frame_label = tk.Label(status_frame,
                                    text="📊 Samples: 0",
                                    font=('Arial', 11),
                                    bg='#2c3e50', fg='white',
                                    padx=20, pady=5)
        self.frame_label.pack(side=tk.LEFT, padx=10)
    
    def start_recording(self):
        """Start recording data"""
        if not self.dot_manager:
            messagebox.showerror("Error", "No sensors configured!")
            return
        
        self.recording = True
        self.start_time = time.time()
        self.frame_count = 0
        
        # Update UI
        self.start_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        self.status_label.config(text="🔴 Status: Recording", fg='#e74c3c')
        
        # Start data collection thread
        self.data_thread = threading.Thread(target=self.collect_data, daemon=True)
        self.data_thread.start()
        
        # Start visualization update
        self.update_visualization()
        
        self.log("Recording started")
    
    def stop_recording(self):
        """Stop recording data"""
        self.recording = False
        
        # Update UI
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        self.status_label.config(text="⚪ Status: Stopped", fg='white')
        
        self.log(f"Recording stopped. Total samples: {self.frame_count}")
    
    def collect_data(self):
        """Collect data from sensors in background thread"""
        while self.recording:
            if self.dot_manager and self.dot_manager.handler.packetsAvailable():
                mapping = self.dot_manager.get_body_position_mapping()
                
                for pos_key, info in mapping.items():
                    address = info['address']
                    packet = self.dot_manager.handler.getNextPacket(address)
                    
                    if packet and packet.containsOrientation():
                        quat = packet.orientationQuaternion()
                        self.latest_quaternions[pos_key] = np.array([quat[0], quat[1], quat[2], quat[3]])
                
                self.frame_count += 1
                
            time.sleep(0.01)
    
    def update_visualization(self):
        """Update the 3D visualization with latest data"""
        if self.recording:
            self.ax.cla()
            
            # Re-setup axes
            axis_limit = (self.SHOULDER_WIDTH + self.UPPER_ARM_LENGTH + self.FOREARM_LENGTH) * 0.7
            self.ax.set_xlim([-axis_limit, axis_limit])
            self.ax.set_ylim([-axis_limit, axis_limit])
            self.ax.set_zlim([-axis_limit, axis_limit])
            self.ax.set_xlabel("X (Right/Left)")
            self.ax.set_ylabel("Y (Forward/Back)")
            self.ax.set_zlabel("Z (Up/Down)")
            self.ax.set_box_aspect([1, 1, 1])
            self.ax.view_init(elev=20, azim=-70)
            self.ax.set_title('Live 3D Arm Visualization', fontsize=12, fontweight='bold')
            
            # Define shoulder positions
            left_shoulder = np.array([-self.SHOULDER_WIDTH/2, 0, 0])
            right_shoulder = np.array([self.SHOULDER_WIDTH/2, 0, 0])
            
            # Draw torso line
            torso_pts = np.array([left_shoulder, right_shoulder])
            self.ax.plot(torso_pts[:, 0], torso_pts[:, 1], torso_pts[:, 2], 
                        'k-', linewidth=3, label="Torso")
            
            mapping = self.dot_manager.get_body_position_mapping()
            
            # Define ideal vectors (in T-pose)
            upper_arm_vec_left = np.array([-self.UPPER_ARM_LENGTH, 0, 0])
            forearm_vec_left = np.array([-self.FOREARM_LENGTH, 0, 0])
            upper_arm_vec_right = np.array([self.UPPER_ARM_LENGTH, 0, 0])
            forearm_vec_right = np.array([self.FOREARM_LENGTH, 0, 0])
            
            # LEFT ARM
            if 'upper_left_arm' in mapping and 'lower_left_arm' in mapping:
                q_left_upper = self.latest_quaternions.get('upper_left_arm')
                q_left_lower = self.latest_quaternions.get('lower_left_arm')
                
                if q_left_upper is not None and q_left_lower is not None:
                    vec_left_upper_rot = self.rotate_vector(upper_arm_vec_left, q_left_upper)
                    left_elbow = left_shoulder + vec_left_upper_rot
                    
                    vec_left_lower_rot = self.rotate_vector(forearm_vec_left, q_left_lower)
                    left_hand = left_elbow + vec_left_lower_rot
                    
                    # Draw left arm cylinders and spheres
                    sphere_radius = 0.03
                    cylinder_radius = 0.015
                    
                    self.create_cylinder(left_shoulder, left_elbow, cylinder_radius, 'blue')
                    self.create_cylinder(left_elbow, left_hand, cylinder_radius, 'cyan')
                    self.create_sphere(left_shoulder, sphere_radius, 'darkblue')
                    self.create_sphere(left_elbow, sphere_radius, 'darkblue')
                    self.create_sphere(left_hand, sphere_radius, 'darkblue')
            
            # RIGHT ARM
            if 'upper_right_arm' in mapping and 'lower_right_arm' in mapping:
                q_right_upper = self.latest_quaternions.get('upper_right_arm')
                q_right_lower = self.latest_quaternions.get('lower_right_arm')
                
                if q_right_upper is not None and q_right_lower is not None:
                    vec_right_upper_rot = self.rotate_vector(upper_arm_vec_right, q_right_upper)
                    right_elbow = right_shoulder + vec_right_upper_rot
                    
                    vec_right_lower_rot = self.rotate_vector(forearm_vec_right, q_right_lower)
                    right_hand = right_elbow + vec_right_lower_rot
                    
                    # Draw right arm cylinders and spheres
                    sphere_radius = 0.03
                    cylinder_radius = 0.015
                    
                    self.create_cylinder(right_shoulder, right_elbow, cylinder_radius, 'red')
                    self.create_cylinder(right_elbow, right_hand, cylinder_radius, 'orange')
                    self.create_sphere(right_shoulder, sphere_radius, 'darkred')
                    self.create_sphere(right_elbow, sphere_radius, 'darkred')
                    self.create_sphere(right_hand, sphere_radius, 'darkred')
            
            try:
                self.canvas.draw()
            except Exception as e:
                print(f"[update_visualization] draw warning: {e}")
            
            # Update status labels
            if self.start_time:
                current_time = time.time() - self.start_time
                self.time_label.config(text=f"⏱️ Time: {current_time:.1f}s")
                self.frame_label.config(text=f"📊 Samples: {self.frame_count}")
            
            # Schedule next update
            self.root.after(50, self.update_visualization)  # Update at ~20 Hz
    
    def toggle_camera(self):
        """Toggle camera on/off"""
        if self.camera_running:
            self.stop_camera()
        else:
            self.start_camera()
    
    def start_camera(self):
        """Start camera feed"""
        self.camera_running = True
        self.camera_btn.config(text="📹 Stop Camera", bg='#c0392b')
        self.update_camera()
        self.log("Camera started")
    
    def stop_camera(self):
        """Stop camera feed"""
        self.camera_running = False
        self.camera_btn.config(text="📹 Start Camera", bg='#3498db')
        self.camera_label.config(image='', text='Camera Stopped',
                                fg='white', font=('Arial', 20))
        self.log("Camera stopped")
    
    def update_camera(self):
        """Update camera frame"""
        if self.camera_running:
            ret, frame = self.vid.read()
            if ret:
                # Resize frame
                frame = cv2.resize(frame, (800, 600))
                
                # Add recording indicator if recording
                if self.recording:
                    cv2.circle(frame, (30, 30), 15, (0, 0, 255), -1)
                    cv2.putText(frame, 'REC', (55, 40),
                              cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                
                # Add timestamp
                if self.recording and self.start_time:
                    elapsed = time.time() - self.start_time
                    cv2.putText(frame, f'Time: {elapsed:.1f}s', (10, 580),
                              cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                
                # Convert BGR to RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Convert to PIL Image
                img = Image.fromarray(frame_rgb)
                
                # Convert to PhotoImage
                photo = ImageTk.PhotoImage(image=img)
                
                # Update label
                self.camera_label.config(image=photo, text='')
                self.camera_label.image = photo
            
            # Schedule next update
            self.root.after(33, self.update_camera)  # ~30 FPS
    
    def log(self, message):
        """Log message to console"""
        timestamp = time.strftime('%H:%M:%S')
        print(f"[{timestamp}] {message}")
    
    def on_closing(self):
        """Cleanup when closing window"""
        self.recording = False
        self.camera_running = False
        
        if self.vid.isOpened():
            self.vid.release()
        
        # Don't cleanup the manager - it might be reused
        # if self.dot_manager:
        #     self.dot_manager.cleanup()
        
        self.root.destroy()


def main():
    """Main function for testing"""
    root = tk.Tk()
    
    # For testing without device setup
    app = LiveRecordingApp(root, dot_manager=None)
    
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()