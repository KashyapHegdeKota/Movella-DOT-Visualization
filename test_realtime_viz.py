"""
Test script for the real-time visualizer
This simulates bicep curl motion without needing actual Movella DOT devices
"""

from realtime_visualizer import RealtimeArmVisualizer
import threading
import time
import numpy as np

print("="*60)
print("Real-Time Visualizer Test")
print("="*60)
print("\nThis will show a simulated bicep curl animation.")
print("The forearm will swing back and forth.")
print("Close the window to stop the simulation.\n")

# Create visualizer
visualizer = RealtimeArmVisualizer()

# Calibrate with identity quaternions (neutral position)
visualizer.calibrate([1, 0, 0, 0], [1, 0, 0, 0])

# Simulate movement in a background thread
def simulate_bicep_curl():
    """Simulate realistic bicep curl motion"""
    t = 0
    print("Starting simulation thread...")
    
    while visualizer.is_running or t < 50:  # Run for a bit even after window closes
        # Simulate bicep curl: forearm rotates around elbow
        # Create smooth oscillation between 0 and ~90 degrees
        angle = np.sin(t * 0.05) * np.pi / 2  # Oscillate between 0 and 90 degrees
        
        # Forearm quaternion (rotation around X-axis)
        # Using axis-angle to quaternion conversion
        half_angle = angle / 2
        quat_forearm = [
            np.cos(half_angle),  # w
            np.sin(half_angle),  # x
            0,                    # y
            0                     # z
        ]
        
        # Upper arm stays relatively fixed
        quat_upper_arm = [1, 0, 0, 0]
        
        # Update the visualizer
        visualizer.update_quaternions(quat_forearm, quat_upper_arm)
        
        t += 1
        time.sleep(0.03)  # ~33 Hz update rate
    
    print("Simulation thread finished.")

# Start simulation thread
sim_thread = threading.Thread(target=simulate_bicep_curl, daemon=True)
sim_thread.start()

print("Opening visualization window...")
print("Close the window to exit.\n")

# Start visualization (this is blocking - runs until window is closed)
try:
    visualizer.start()
except KeyboardInterrupt:
    print("\nInterrupted by user.")

print("\n" + "="*60)
print("Test complete!")
print("="*60)
