import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import time
import csv
from datetime import datetime
from movella_dot_manager import MovellaDotManager
from visualize_bicep_curl import visualize_bicep_curl
from realtime_visualizer import RealtimeArmVisualizer


class MovellaDOTGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Movella DOT Tracker Manager")
        self.root.geometry("800x600")
        
        self.manager = None
        self.is_recording = False
        self.recording_thread = None
        self.keyboard_listener = None
        self.realtime_visualizer = None
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the main UI components"""
        # Title
        title_label = tk.Label(
            self.root, 
            text="Movella DOT Tracker Manager", 
            font=("Arial", 16, "bold"),
            pady=10
        )
        title_label.pack()
        
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Status Section
        status_frame = ttk.LabelFrame(main_frame, text="Status", padding="10")
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.status_text = tk.Text(status_frame, height=8, wrap=tk.WORD, state=tk.DISABLED)
        self.status_text.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(status_frame, command=self.status_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.status_text.config(yscrollcommand=scrollbar.set)
        
        # Device Setup Section
        setup_frame = ttk.LabelFrame(main_frame, text="Device Setup", padding="10")
        setup_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(setup_frame, text="Number of trackers:").grid(row=0, column=0, padx=5, sticky=tk.W)
        self.tracker_count_var = tk.StringVar(value="2")
        tracker_spinbox = ttk.Spinbox(
            setup_frame, 
            from_=1, 
            to=10, 
            textvariable=self.tracker_count_var,
            width=10
        )
        tracker_spinbox.grid(row=0, column=1, padx=5)
        
        self.setup_button = ttk.Button(
            setup_frame, 
            text="Setup Devices", 
            command=self.setup_devices
        )
        self.setup_button.grid(row=0, column=2, padx=5)
        
        self.device_status_label = ttk.Label(setup_frame, text="Status: Not Connected", foreground="red")
        self.device_status_label.grid(row=0, column=3, padx=10)
        
        # Device Info Section (shows connected devices)
        self.device_info_frame = ttk.LabelFrame(setup_frame, text="Connected Devices", padding="5")
        self.device_info_frame.grid(row=1, column=0, columnspan=4, sticky=tk.EW, pady=(10, 0))
        
        self.device_info_labels = []
        
        # Recording Section
        recording_frame = ttk.LabelFrame(main_frame, text="Recording Controls", padding="10")
        recording_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(recording_frame, text="Recording Duration (seconds):").grid(row=0, column=0, padx=5, sticky=tk.W)
        self.duration_var = tk.StringVar(value="10")
        duration_spinbox = ttk.Spinbox(
            recording_frame,
            from_=1,
            to=300,
            textvariable=self.duration_var,
            width=10
        )
        duration_spinbox.grid(row=0, column=1, padx=5)
        
        self.record_button = ttk.Button(
            recording_frame,
            text="Start Recording",
            command=self.toggle_recording,
            state=tk.DISABLED
        )
        self.record_button.grid(row=0, column=2, padx=5)
        
        self.live_record_button = ttk.Button(
            recording_frame,
            text="Live Recording",
            command=self.toggle_live_recording,
            state=tk.DISABLED
        )
        self.live_record_button.grid(row=0, column=3, padx=5)
        
        self.recording_status_label = ttk.Label(recording_frame, text="Status: Idle", foreground="gray")
        self.recording_status_label.grid(row=0, column=4, padx=10)
        
        ttk.Label(recording_frame, text="Output file:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.filename_var = tk.StringVar(value=f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_output.csv")
        filename_entry = ttk.Entry(recording_frame, textvariable=self.filename_var, width=40)
        filename_entry.grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky=tk.W)
        
        # Visualization Section
        viz_frame = ttk.LabelFrame(main_frame, text="Visualization", padding="10")
        viz_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.viz_file_var = tk.StringVar()
        ttk.Label(viz_frame, text="CSV File:").grid(row=0, column=0, padx=5, sticky=tk.W)
        viz_file_entry = ttk.Entry(viz_frame, textvariable=self.viz_file_var, width=40)
        viz_file_entry.grid(row=0, column=1, padx=5)
        
        browse_button = ttk.Button(viz_frame, text="Browse...", command=self.browse_csv)
        browse_button.grid(row=0, column=2, padx=5)
        
        self.visualize_button = ttk.Button(
            viz_frame,
            text="Visualize",
            command=self.visualize_data
        )
        self.visualize_button.grid(row=0, column=3, padx=5)
        
        # Bottom buttons
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.cleanup_button = ttk.Button(
            bottom_frame,
            text="Disconnect Devices",
            command=self.cleanup_devices,
            state=tk.DISABLED
        )
        self.cleanup_button.pack(side=tk.LEFT, padx=5)
        
        quit_button = ttk.Button(
            bottom_frame,
            text="Quit",
            command=self.quit_application
        )
        quit_button.pack(side=tk.RIGHT, padx=5)
        
    def log_status(self, message):
        """Add a message to the status text area"""
        self.status_text.config(state=tk.NORMAL)
        self.status_text.insert(tk.END, f"{message}\n")
        self.status_text.see(tk.END)
        self.status_text.config(state=tk.DISABLED)
        self.root.update()
        
    def setup_devices(self):
        """Setup Movella DOT devices"""
        self.setup_button.config(state=tk.DISABLED)
        self.log_status("="*60)
        self.log_status("Starting device setup...")
        
        def setup_thread():
            try:
                num_trackers = int(self.tracker_count_var.get())
                self.manager = MovellaDotManager()
                
                # Initialize
                self.log_status("Initializing Movella DOT SDK...")
                if not self.manager.initialize():
                    self.log_status("Failed to initialize SDK!")
                    self.setup_button.config(state=tk.NORMAL)
                    return
                
                # Scan for devices
                self.log_status(f"\nScanning for {num_trackers} device(s)...")
                self.log_status("Make sure your devices are powered on and discoverable.")
                self.manager.handler.scanForDots()
                detected_devices = self.manager.handler.detectedDots()
                
                if len(detected_devices) < num_trackers:
                    self.log_status(f"Error: Found only {len(detected_devices)} device(s), need {num_trackers}")
                    self.setup_button.config(state=tk.NORMAL)
                    return
                
                self.log_status(f"Found {len(detected_devices)} device(s)")
                for i, device_info in enumerate(detected_devices):
                    self.log_status(f"  [{i}] {device_info.bluetoothAddress()}")
                
                # Auto-select first N devices
                selected_devices = []
                for i in range(num_trackers):
                    label = f"tracker_{i+1}"
                    selected_devices.append((detected_devices[i], label))
                    self.log_status(f"Auto-selected: {detected_devices[i].bluetoothAddress()} as '{label}'")
                
                # Connect
                self.log_status("\nConnecting to devices...")
                if not self.manager.connect_to_devices(selected_devices):
                    self.log_status("Connection failed!")
                    self.setup_button.config(state=tk.NORMAL)
                    return
                
                # Calibrate
                self.log_status("\nStarting calibration...")
                self.log_status("Position all devices in their reference orientations")
                time.sleep(2)  # Give user time to position devices
                
                if not self.manager.calibrate_devices():
                    self.log_status("Calibration failed!")
                    self.setup_button.config(state=tk.NORMAL)
                    return
                
                # Start measurement
                if not self.manager.start_measurement_mode():
                    self.log_status("Failed to start measurement mode!")
                    self.setup_button.config(state=tk.NORMAL)
                    return
                
                self.log_status("\n✓ Setup complete! Devices ready for recording.")
                self.device_status_label.config(text="Status: Connected", foreground="green")
                self.record_button.config(state=tk.NORMAL)
                self.live_record_button.config(state=tk.NORMAL)
                self.cleanup_button.config(state=tk.NORMAL)
                
                # Display device information
                self.display_device_info()
                
            except Exception as e:
                self.log_status(f"Error during setup: {e}")
                self.setup_button.config(state=tk.NORMAL)
        
        thread = threading.Thread(target=setup_thread, daemon=True)
        thread.start()
        
    def toggle_recording(self):
        """Start or stop recording"""
        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()
            
    def start_recording(self):
        """Start recording quaternion data"""
        if not self.manager:
            messagebox.showerror("Error", "Please setup devices first!")
            return
            
        devices = self.manager.get_connected_devices()
        if len(devices) != 2:
            messagebox.showerror("Error", "Recording requires exactly 2 devices!")
            return
        
        self.is_recording = True
        self.record_button.config(text="Stop Recording")
        self.recording_status_label.config(text="Status: Recording...", foreground="red")
        self.setup_button.config(state=tk.DISABLED)
        
        filename = self.filename_var.get()
        duration = int(self.duration_var.get())
        
        def record_thread():
            try:
                addr1 = devices[0][0].bluetoothAddress()
                addr2 = devices[1][0].bluetoothAddress()
                
                self.log_status(f"\n Recording to {filename}...")
                self.log_status(f"Duration: {duration} seconds")
                
                with open(filename, "w", newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(["tracker_1_WXYZ", "tracker_2_WXYZ"])
                    
                    start = time.time()
                    last_log = start
                    
                    while self.is_recording and (time.time() - start) < duration:
                        # Get packet data
                        packets = self.manager.handler.getDataPackets(devices[0][0])
                        if packets:
                            quat1 = packets[-1].orientationQuaternion()
                            q1_str = f"{quat1.w()},{quat1.x()},{quat1.y()},{quat1.z()}"
                        else:
                            q1_str = "0,0,0,0"
                        
                        packets = self.manager.handler.getDataPackets(devices[1][0])
                        if packets:
                            quat2 = packets[-1].orientationQuaternion()
                            q2_str = f"{quat2.w()},{quat2.x()},{quat2.y()},{quat2.z()}"
                        else:
                            q2_str = "0,0,0,0"
                        
                        writer.writerow([q1_str, q2_str])
                        
                        # Update status every second
                        if time.time() - last_log >= 1.0:
                            elapsed = int(time.time() - start)
                            self.log_status(f"Recording... {elapsed}/{duration} seconds")
                            last_log = time.time()
                        
                        time.sleep(0.01)  # ~100Hz sampling
                
                self.log_status(f"✓ Recording saved to {filename}")
                self.viz_file_var.set(filename)  # Auto-fill visualization field
                
            except Exception as e:
                self.log_status(f"Error during recording: {e}")
            finally:
                self.is_recording = False
                self.record_button.config(text="Start Recording")
                self.recording_status_label.config(text="Status: Idle", foreground="gray")
                self.setup_button.config(state=tk.NORMAL)
        
        self.recording_thread = threading.Thread(target=record_thread, daemon=True)
        self.recording_thread.start()
        
    def stop_recording(self):
        """Stop the current recording"""
        self.is_recording = False
        self.log_status("Stopping recording...")
    
    def display_device_info(self):
        """Display information about connected devices with identify buttons"""
        # Clear existing labels
        for widget in self.device_info_frame.winfo_children():
            widget.destroy()
        
        if not self.manager:
            return
        
        devices = self.manager.get_connected_devices()
        
        # Create header
        ttk.Label(self.device_info_frame, text="Label", font=("Arial", 9, "bold")).grid(row=0, column=0, padx=5, pady=2)
        ttk.Label(self.device_info_frame, text="Address", font=("Arial", 9, "bold")).grid(row=0, column=1, padx=5, pady=2)
        ttk.Label(self.device_info_frame, text="Battery", font=("Arial", 9, "bold")).grid(row=0, column=2, padx=5, pady=2)
        ttk.Label(self.device_info_frame, text="Action", font=("Arial", 9, "bold")).grid(row=0, column=3, padx=5, pady=2)
        
        # Add each device
        for i, (device, info) in enumerate(devices):
            row = i + 1
            label = info['label']
            address = device.bluetoothAddress()
            
            # Get battery level
            try:
                battery = device.batteryLevel()
                battery_text = f"{battery}%"
                battery_color = "green" if battery > 50 else ("orange" if battery > 20 else "red")
            except:
                battery_text = "N/A"
                battery_color = "gray"
            
            # Label
            ttk.Label(self.device_info_frame, text=label, font=("Arial", 9, "bold")).grid(row=row, column=0, padx=5, pady=2)
            
            # Address (last 4 characters for readability)
            short_addr = f"...{address[-8:]}" if len(address) > 8 else address
            ttk.Label(self.device_info_frame, text=short_addr).grid(row=row, column=1, padx=5, pady=2)
            
            # Battery
            battery_label = ttk.Label(self.device_info_frame, text=battery_text, foreground=battery_color)
            battery_label.grid(row=row, column=2, padx=5, pady=2)
            
            # Identify button
            identify_btn = ttk.Button(
                self.device_info_frame,
                text="Blink LED",
                command=lambda d=device, l=label: self.identify_device(d, l),
                width=12
            )
            identify_btn.grid(row=row, column=3, padx=5, pady=2)
        
        # Add swap button if exactly 2 devices
        if len(devices) == 2:
            swap_btn = ttk.Button(
                self.device_info_frame,
                text="⇄ Swap Tracker 1 ↔ Tracker 2",
                command=self.swap_device_assignments,
                style="Accent.TButton"
            )
            swap_btn.grid(row=len(devices)+1, column=0, columnspan=4, pady=(10, 5))
        
        # Add helper text
        helper_label = ttk.Label(
            self.device_info_frame, 
            text="💡 Click 'Blink LED' to identify which physical tracker is which. Use 'Swap' if assignments are reversed.",
            font=("Arial", 8),
            foreground="blue"
        )
        helper_label.grid(row=len(devices)+2, column=0, columnspan=4, pady=(5, 0))
    
    def identify_device(self, device, label):
        """Make a device blink its LED for identification"""
        def blink_thread():
            try:
                self.log_status(f"\n🔦 Blinking LED on {label}...")
                self.log_status(f"   Address: {device.bluetoothAddress()}")
                self.log_status(f"   Watch for the blinking light!")
                
                # Call the identify function - this makes the LED blink
                device.identify()
                
                self.log_status(f"✓ LED blink command sent to {label}")
                
            except Exception as e:
                self.log_status(f"Error identifying device: {e}")
        
        thread = threading.Thread(target=blink_thread, daemon=True)
        thread.start()
    
    def swap_device_assignments(self):
        """Swap the assignments of tracker_1 and tracker_2"""
        if not self.manager:
            return
        
        devices = self.manager.get_connected_devices()
        if len(devices) != 2:
            messagebox.showwarning("Swap Error", "Swap only works with exactly 2 devices!")
            return
        
        # Get the two devices
        device1, info1 = devices[0]
        device2, info2 = devices[1]
        
        addr1 = device1.bluetoothAddress()
        addr2 = device2.bluetoothAddress()
        
        # Swap the labels in the manager's device_info
        self.manager.device_info[addr1]['label'], self.manager.device_info[addr2]['label'] = \
            self.manager.device_info[addr2]['label'], self.manager.device_info[addr1]['label']
        
        # Swap the order in connected_devices list
        self.manager.connected_devices[0], self.manager.connected_devices[1] = \
            self.manager.connected_devices[1], self.manager.connected_devices[0]
        
        self.log_status("\n🔄 Swapped device assignments:")
        self.log_status(f"   {addr1[-8:]} is now {self.manager.device_info[addr1]['label']}")
        self.log_status(f"   {addr2[-8:]} is now {self.manager.device_info[addr2]['label']}")
        
        # Refresh the display
        self.display_device_info()
        
        messagebox.showinfo("Swap Complete", "Tracker assignments have been swapped!\n\ntracker_1 ↔ tracker_2")
    
    def toggle_live_recording(self):
        """Start or stop live recording with real-time visualization"""
        if not self.is_recording:
            self.start_live_recording()
        else:
            self.stop_live_recording()
    
    def start_live_recording(self):
        """Start recording with real-time 3D visualization"""
        if not self.manager:
            messagebox.showerror("Error", "Please setup devices first!")
            return
            
        devices = self.manager.get_connected_devices()
        if len(devices) != 2:
            messagebox.showerror("Error", "Recording requires exactly 2 devices!")
            return
        
        self.is_recording = True
        self.live_record_button.config(text="Stop Live Recording")
        self.record_button.config(state=tk.DISABLED)
        self.recording_status_label.config(text="Status: Live Recording...", foreground="red")
        self.setup_button.config(state=tk.DISABLED)
        
        filename = self.filename_var.get()
        duration = int(self.duration_var.get())
        
        # Create visualizer
        self.realtime_visualizer = RealtimeArmVisualizer()
        
        def record_thread():
            try:
                addr1 = devices[0][0].bluetoothAddress()
                addr2 = devices[1][0].bluetoothAddress()
                
                self.log_status(f"\n🔴 Live recording to {filename}...")
                self.log_status(f"Duration: {duration} seconds")
                self.log_status("Opening visualization window...")
                
                # Calibrate visualizer with first reading
                time.sleep(0.5)  # Wait for stable data
                
                packets = self.manager.handler.getDataPackets(devices[0][0])
                if packets:
                    quat1 = packets[-1].orientationQuaternion()
                    q1 = [quat1.w(), quat1.x(), quat1.y(), quat1.z()]
                else:
                    q1 = [1, 0, 0, 0]
                
                packets = self.manager.handler.getDataPackets(devices[1][0])
                if packets:
                    quat2 = packets[-1].orientationQuaternion()
                    q2 = [quat2.w(), quat2.x(), quat2.y(), quat2.z()]
                else:
                    q2 = [1, 0, 0, 0]
                
                self.realtime_visualizer.calibrate(q1, q2)
                
                # Start visualization in separate thread
                viz_thread = threading.Thread(
                    target=self.realtime_visualizer.start,
                    daemon=True
                )
                viz_thread.start()
                
                # Give visualization time to start
                time.sleep(1)
                
                # Start recording with live updates
                with open(filename, "w", newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(["tracker_1_WXYZ", "tracker_2_WXYZ"])
                    
                    start = time.time()
                    last_log = start
                    
                    while self.is_recording and (time.time() - start) < duration:
                        # Get packet data
                        packets = self.manager.handler.getDataPackets(devices[0][0])
                        if packets:
                            quat1 = packets[-1].orientationQuaternion()
                            q1_str = f"{quat1.w()},{quat1.x()},{quat1.y()},{quat1.z()}"
                            q1 = [quat1.w(), quat1.x(), quat1.y(), quat1.z()]
                        else:
                            q1_str = "0,0,0,0"
                            q1 = [1, 0, 0, 0]
                        
                        packets = self.manager.handler.getDataPackets(devices[1][0])
                        if packets:
                            quat2 = packets[-1].orientationQuaternion()
                            q2_str = f"{quat2.w()},{quat2.x()},{quat2.y()},{quat2.z()}"
                            q2 = [quat2.w(), quat2.x(), quat2.y(), quat2.z()]
                        else:
                            q2_str = "0,0,0,0"
                            q2 = [1, 0, 0, 0]
                        
                        # Update visualizer
                        self.realtime_visualizer.update_quaternions(q1, q2)
                        
                        # Write to file
                        writer.writerow([q1_str, q2_str])
                        
                        # Update status every second
                        if time.time() - last_log >= 1.0:
                            elapsed = int(time.time() - start)
                            self.log_status(f"Recording... {elapsed}/{duration} seconds")
                            last_log = time.time()
                        
                        time.sleep(0.01)  # ~100Hz sampling
                
                self.log_status(f"✓ Recording saved to {filename}")
                self.viz_file_var.set(filename)  # Auto-fill visualization field
                
            except Exception as e:
                self.log_status(f"Error during live recording: {e}")
                import traceback
                traceback.print_exc()
            finally:
                self.is_recording = False
                if self.realtime_visualizer:
                    self.realtime_visualizer.stop()
                self.live_record_button.config(text="Live Recording")
                self.record_button.config(state=tk.NORMAL)
                self.recording_status_label.config(text="Status: Idle", foreground="gray")
                self.setup_button.config(state=tk.NORMAL)
        
        self.recording_thread = threading.Thread(target=record_thread, daemon=True)
        self.recording_thread.start()
    
    def stop_live_recording(self):
        """Stop the current live recording"""
        self.is_recording = False
        self.log_status("Stopping live recording...")
        if self.realtime_visualizer:
            self.realtime_visualizer.stop()
        
    def browse_csv(self):
        """Browse for a CSV file"""
        filename = filedialog.askopenfilename(
            title="Select CSV file",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            self.viz_file_var.set(filename)
            
    def visualize_data(self):
        """Visualize the recorded data"""
        csv_file = self.viz_file_var.get()
        if not csv_file:
            messagebox.showerror("Error", "Please select a CSV file!")
            return
        
        self.log_status(f"\nStarting visualization of {csv_file}...")
        
        def viz_thread():
            try:
                visualize_bicep_curl(csv_file)
            except Exception as e:
                self.log_status(f"Error during visualization: {e}")
                messagebox.showerror("Visualization Error", str(e))
        
        thread = threading.Thread(target=viz_thread, daemon=True)
        thread.start()
        
    def cleanup_devices(self):
        """Cleanup and disconnect devices"""
        if self.manager:
            self.log_status("\nDisconnecting devices...")
            self.manager.cleanup()
            self.manager = None
            self.device_status_label.config(text="Status: Not Connected", foreground="red")
            self.record_button.config(state=tk.DISABLED)
            self.live_record_button.config(state=tk.DISABLED)
            self.cleanup_button.config(state=tk.DISABLED)
            self.setup_button.config(state=tk.NORMAL)
            self.log_status("✓ Devices disconnected")
            
    def quit_application(self):
        """Quit the application"""
        if self.is_recording:
            if not messagebox.askyesno("Recording in Progress", "Recording is in progress. Do you want to quit?"):
                return
        
        if self.manager:
            self.cleanup_devices()
        
        self.root.quit()


def main():
    root = tk.Tk()
    app = MovellaDOTGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.quit_application)
    root.mainloop()


if __name__ == "__main__":
    main()
