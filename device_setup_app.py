import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import time
from typing import List, Dict, Optional

import movelladot_pc_sdk
from movella_dot_manager import MovellaDotManager

class DeviceSetupApp:
    def __init__(self, root, on_complete=None, on_cancel=None):
        self.root = root
        self.root.title("Movella DOT Setup")
        self.root.geometry("900x750")
        self.root.configure(bg='#2c3e50')
        
        # Initialize Movella DOT manager
        self.dot_manager = MovellaDotManager()
        
        # State variables
        self.detected_devices = []
        self.connected_devices = []  # Store connected device objects
        self.assigned_devices = []
        self.setup_complete = False
        self.current_step = 0
        self.identification_active = False
        
        # Color scheme
        self.colors = {
            'bg': '#2c3e50',
            'fg': 'white',
            'button': '#3498db',
            'button_hover': '#2980b9',
            'success': '#27ae60',
            'error': '#e74c3c',
            'warning': '#f39c12',
            'card_bg': '#34495e',
            'highlight': '#e67e22'
        }
        
        self.setup_ui()
        self.on_complete = on_complete
        self.on_cancel = on_cancel
    def setup_ui(self):
        """Setup the main UI components"""
        # Main container
        main_container = tk.Frame(self.root, bg=self.colors['bg'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_frame = tk.Frame(main_container, bg=self.colors['bg'])
        title_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_label = tk.Label(title_frame, 
                              text="🎯 Movella DOT Setup",
                              font=('Arial', 28, 'bold'),
                              bg=self.colors['bg'],
                              fg=self.colors['fg'])
        title_label.pack()
        
        subtitle_label = tk.Label(title_frame,
                                 text="Sensor Identification & Body Position Assignment",
                                 font=('Arial', 12),
                                 bg=self.colors['bg'],
                                 fg='#95a5a6')
        subtitle_label.pack()
        
        # Progress bar
        self.progress_frame = tk.Frame(main_container, bg=self.colors['bg'])
        self.progress_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.setup_progress_bar()
        
        # Content area
        self.content_frame = tk.Frame(main_container, bg=self.colors['bg'])
        self.content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Status/Log area
        self.log_frame = tk.Frame(main_container, bg=self.colors['card_bg'], relief=tk.SUNKEN, bd=2)
        self.log_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        log_title = tk.Label(self.log_frame,
                            text="📋 Status Log",
                            font=('Arial', 12, 'bold'),
                            bg=self.colors['card_bg'],
                            fg=self.colors['fg'])
        log_title.pack(anchor=tk.W, padx=10, pady=(5, 0))
        
        self.log_text = scrolledtext.ScrolledText(self.log_frame,
                                                  height=8,
                                                  font=('Courier', 9),
                                                  bg='#1c2833',
                                                  fg='#ecf0f1',
                                                  relief=tk.FLAT)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Show initial screen
        self.show_welcome_screen()
        
    def setup_progress_bar(self):
        """Create progress bar showing setup steps"""
        steps = ["Initialize", "Scan", "Connect", "Identify", "Assign", "Calibrate", "Complete"]
        
        for i, step in enumerate(steps):
            step_frame = tk.Frame(self.progress_frame, bg=self.colors['bg'])
            step_frame.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=1)
            
            # Circle indicator
            canvas = tk.Canvas(step_frame, width=25, height=25, 
                             bg=self.colors['bg'], highlightthickness=0)
            canvas.pack()
            
            # Draw circle
            color = self.colors['success'] if i < self.current_step else '#95a5a6'
            canvas.create_oval(3, 3, 22, 22, fill=color, outline=color)
            canvas.create_text(12.5, 12.5, text=str(i+1), fill='white', font=('Arial', 9, 'bold'))
            
            # Step label
            label = tk.Label(step_frame, text=step, font=('Arial', 7),
                           bg=self.colors['bg'], fg=self.colors['fg'])
            label.pack()
            
            # Store for later updates
            setattr(self, f'progress_canvas_{i}', canvas)
    
    def update_progress(self, step: int):
        """Update progress bar"""
        self.current_step = step
        for i in range(7):
            canvas = getattr(self, f'progress_canvas_{i}')
            color = self.colors['success'] if i < step else '#95a5a6'
            canvas.delete('all')
            canvas.create_oval(3, 3, 22, 22, fill=color, outline=color)
            canvas.create_text(12.5, 12.5, text=str(i+1), fill='white', font=('Arial', 9, 'bold'))
    
    def log(self, message: str, level: str = 'info'):
        """Add message to log"""
        timestamp = time.strftime('%H:%M:%S')
        prefix = {
            'info': 'ℹ️',
            'success': '✅',
            'error': '❌',
            'warning': '⚠️'
        }.get(level, 'ℹ️')
        
        self.log_text.insert(tk.END, f"[{timestamp}] {prefix} {message}\n")
        self.log_text.see(tk.END)
        self.root.update()
    
    def clear_content(self):
        """Clear the content frame"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def show_welcome_screen(self):
        """Show welcome screen"""
        self.clear_content()
        self.log("Welcome to Movella DOT Setup", "info")
        
        welcome_frame = tk.Frame(self.content_frame, bg=self.colors['bg'])
        welcome_frame.pack(expand=True)
        
        # Welcome message
        welcome_text = """
        Welcome to the Movella DOT Setup Wizard!
        
        This wizard will guide you through:
        
        1️⃣ Scanning for active sensors
        2️⃣ Connecting to sensors
        3️⃣ Identifying which sensor is which (LED blinking)
        4️⃣ Assigning sensors to body positions
        5️⃣ Calibrating the sensors
        6️⃣ Starting measurement mode
        
        Make sure all your sensors are:
        • Powered ON (LED blinking slowly)
        • Within Bluetooth range
        • Not connected to other devices
        """
        
        welcome_label = tk.Label(welcome_frame,
                                text=welcome_text,
                                font=('Arial', 12),
                                bg=self.colors['bg'],
                                fg=self.colors['fg'],
                                justify=tk.LEFT)
        welcome_label.pack(pady=20)
        
        # Start button
        start_btn = tk.Button(welcome_frame,
                             text="🚀 Start Setup",
                             font=('Arial', 16, 'bold'),
                             bg=self.colors['button'],
                             fg='white',
                             padx=30,
                             pady=15,
                             command=self.start_setup,
                             cursor='hand2',
                             relief=tk.RAISED,
                             bd=3)
        start_btn.pack(pady=20)
        
    def start_setup(self):
        """Start the setup process"""
        self.log("Starting setup process...", "info")
        self.update_progress(1)
        
        # Run initialization in background thread
        thread = threading.Thread(target=self.initialize_sdk)
        thread.daemon = True
        thread.start()
    
    def initialize_sdk(self):
        """Initialize the Movella SDK"""
        self.log("Initializing Movella DOT SDK...", "info")
        
        try:
            if self.dot_manager.initialize():
                self.log("SDK initialized successfully!", "success")
                self.root.after(100, self.scan_for_sensors)
            else:
                self.log("Failed to initialize SDK", "error")
                self.root.after(100, lambda: messagebox.showerror("Error", "Failed to initialize SDK"))
        except Exception as e:
            self.log(f"Error during initialization: {e}", "error")
            self.root.after(100, lambda: messagebox.showerror("Error", str(e)))
    
    def scan_for_sensors(self):
        """Scan for sensors"""
        self.update_progress(2)
        self.log("Scanning for active sensors...", "info")
        
        # Show scanning screen
        self.show_scanning_screen()
        
        # Run scan in background thread
        thread = threading.Thread(target=self.perform_scan)
        thread.daemon = True
        thread.start()
    
    def show_scanning_screen(self):
        """Show scanning animation"""
        self.clear_content()
        
        scan_frame = tk.Frame(self.content_frame, bg=self.colors['bg'])
        scan_frame.pack(expand=True)
        
        scan_label = tk.Label(scan_frame,
                             text="🔍 Scanning for sensors...",
                             font=('Arial', 18, 'bold'),
                             bg=self.colors['bg'],
                             fg=self.colors['fg'])
        scan_label.pack(pady=20)
        
        # Animated dots
        self.scan_dots_label = tk.Label(scan_frame,
                                        text="",
                                        font=('Arial', 24),
                                        bg=self.colors['bg'],
                                        fg=self.colors['button'])
        self.scan_dots_label.pack()
        
        self.animate_scanning()
    
    def animate_scanning(self, dots=0):
        """Animate scanning dots"""
        if hasattr(self, 'scan_dots_label') and self.scan_dots_label.winfo_exists():
            dot_text = "●" * (dots % 4)
            self.scan_dots_label.config(text=dot_text)
            self.root.after(300, lambda: self.animate_scanning(dots + 1))
    
    def perform_scan(self):
        """Perform the actual scan"""
        try:
            self.detected_devices = self.dot_manager.scan_and_identify_active_sensors()
            
            if self.detected_devices:
                self.log(f"Found {len(self.detected_devices)} sensor(s)!", "success")
                for i, device in enumerate(self.detected_devices):
                    self.log(f"  Sensor {i+1}: {device.bluetoothAddress()}", "info")
                
                # Connect to sensors before identification
                self.root.after(500, self.connect_for_identification)
            else:
                self.log("No sensors found", "warning")
                self.root.after(100, lambda: messagebox.showwarning(
                    "No Sensors Found",
                    "No sensors were detected. Please ensure they are:\n"
                    "• Powered on\n"
                    "• Within range\n"
                    "• Not connected elsewhere"
                ))
                self.root.after(100, self.show_welcome_screen)
        except Exception as e:
            self.log(f"Error during scan: {e}", "error")
            self.root.after(100, lambda: messagebox.showerror("Scan Error", str(e)))
    
    def connect_for_identification(self):
        """Connect to sensors for identification"""
        self.update_progress(3)
        self.log("Connecting to sensors for identification...", "info")
        self.show_connecting_screen()
        
        # Run connection in background
        thread = threading.Thread(target=self.perform_initial_connection)
        thread.daemon = True
        thread.start()
    
    def show_connecting_screen(self):
        """Show connecting screen"""
        self.clear_content()
        
        connect_frame = tk.Frame(self.content_frame, bg=self.colors['bg'])
        connect_frame.pack(expand=True)
        
        connect_label = tk.Label(connect_frame,
                                text="🔗 Connecting to sensors...",
                                font=('Arial', 18, 'bold'),
                                bg=self.colors['bg'],
                                fg=self.colors['fg'])
        connect_label.pack(pady=20)
        
        info_label = tk.Label(connect_frame,
                             text="This allows us to identify each sensor individually",
                             font=('Arial', 11),
                             bg=self.colors['bg'],
                             fg='#95a5a6')
        info_label.pack()
    
    def perform_initial_connection(self):
        """Connect to all detected sensors"""
        try:
            self.log("Connecting to all sensors...", "info")
            
            # Use the handler to connect to all detected devices
            self.dot_manager.handler.connectDots()
            connected = self.dot_manager.handler.connectedDots()
            
            if not connected:
                self.log("Failed to connect to sensors", "error")
                self.root.after(100, lambda: messagebox.showerror(
                    "Connection Error",
                    "Could not connect to sensors. Please try again."
                ))
                return
            
            self.log(f"Connected to {len(connected)} sensor(s)", "success")
            
            # Store connected devices
            self.connected_devices = {}
            for device in connected:
                address = device.bluetoothAddress()
                self.connected_devices[address] = device
                
            self.root.after(500, self.show_identification_screen)
            
        except Exception as e:
            self.log(f"Connection error: {e}", "error")
            self.root.after(100, lambda: messagebox.showerror("Error", str(e)))
    
    def show_identification_screen(self):
        """Show sensor identification screen"""
        self.clear_content()
        self.update_progress(4)
        self.log("Ready to identify sensors", "info")
        self.identification_active = True
        
        id_frame = tk.Frame(self.content_frame, bg=self.colors['bg'])
        id_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Title
        title = tk.Label(id_frame,
                        text="💡 Identify Your Sensors",
                        font=('Arial', 18, 'bold'),
                        bg=self.colors['bg'],
                        fg=self.colors['fg'])
        title.pack(pady=(0, 5))
        
        # Instructions
        instructions = tk.Label(id_frame,
                               text="Click on a sensor below to make ONLY its LED blink rapidly.\n"
                                    "Watch your physical sensors to see which one is blinking.\n"
                                    "Label each sensor so you remember which is which!",
                               font=('Arial', 11),
                               bg=self.colors['bg'],
                               fg=self.colors['fg'],
                               justify=tk.CENTER)
        instructions.pack(pady=5)
        
        # Sensor cards frame with scrollbar
        canvas_frame = tk.Frame(id_frame, bg=self.colors['bg'])
        canvas_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Canvas for scrolling
        canvas = tk.Canvas(canvas_frame, bg=self.colors['bg'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors['bg'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Create cards for each sensor
        self.sensor_label_vars = {}
        self.identify_buttons = {}
        
        for i, device_info in enumerate(self.detected_devices):
            address = device_info.bluetoothAddress()
            card = self.create_identification_card(scrollable_frame, device_info, i)
            card.pack(fill=tk.X, pady=5, padx=5)
        
        # Buttons
        button_frame = tk.Frame(id_frame, bg=self.colors['bg'])
        button_frame.pack(pady=15)
        
        continue_btn = tk.Button(button_frame,
                                text="✓ Continue to Assignment",
                                font=('Arial', 12, 'bold'),
                                bg=self.colors['success'],
                                fg='white',
                                padx=20,
                                pady=10,
                                command=self.show_assignment_screen,
                                cursor='hand2')
        continue_btn.pack(side=tk.LEFT, padx=5)
        
        back_btn = tk.Button(button_frame,
                            text="← Rescan",
                            font=('Arial', 12),
                            bg=self.colors['card_bg'],
                            fg='white',
                            padx=20,
                            pady=10,
                            command=self.scan_for_sensors,
                            cursor='hand2')
        back_btn.pack(side=tk.LEFT, padx=5)
    
    def create_identification_card(self, parent, device_info, index: int):
        """Create a card for sensor identification"""
        address = device_info.bluetoothAddress()
        
        card = tk.Frame(parent, bg=self.colors['card_bg'], relief=tk.RAISED, bd=2)
        
        # Left side - Sensor info
        info_frame = tk.Frame(card, bg=self.colors['card_bg'])
        info_frame.pack(side=tk.LEFT, padx=15, pady=10, fill=tk.X, expand=True)
        
        # Sensor number and address
        sensor_label = tk.Label(info_frame,
                               text=f"Sensor {index + 1}",
                               font=('Arial', 12, 'bold'),
                               bg=self.colors['card_bg'],
                               fg=self.colors['highlight'])
        sensor_label.pack(anchor=tk.W)
        
        address_label = tk.Label(info_frame,
                                text=f"MAC: {address}",
                                font=('Arial', 9),
                                bg=self.colors['card_bg'],
                                fg='#95a5a6')
        address_label.pack(anchor=tk.W)
        
        # Label entry
        label_frame = tk.Frame(info_frame, bg=self.colors['card_bg'])
        label_frame.pack(anchor=tk.W, pady=(5, 0))
        
        label_prompt = tk.Label(label_frame,
                               text="Your label:",
                               font=('Arial', 9),
                               bg=self.colors['card_bg'],
                               fg=self.colors['fg'])
        label_prompt.pack(side=tk.LEFT)
        
        label_var = tk.StringVar(value=f"Sensor_{index + 1}")
        self.sensor_label_vars[address] = label_var
        
        label_entry = tk.Entry(label_frame,
                              textvariable=label_var,
                              font=('Arial', 10),
                              width=20)
        label_entry.pack(side=tk.LEFT, padx=5)
        
        # Right side - Identify button
        button_frame = tk.Frame(card, bg=self.colors['card_bg'])
        button_frame.pack(side=tk.RIGHT, padx=15, pady=10)
        
        identify_btn = tk.Button(button_frame,
                                text="💡 Identify This Sensor",
                                font=('Arial', 10, 'bold'),
                                bg=self.colors['button'],
                                fg='white',
                                padx=15,
                                pady=8,
                                command=lambda: self.identify_sensor(address, index),
                                cursor='hand2')
        identify_btn.pack()
        
        self.identify_buttons[address] = identify_btn
        
        return card
    
    def identify_sensor(self, address: str, index: int):
        """Make a specific sensor's LED blink for identification"""
        self.log(f"Identifying Sensor {index + 1} ({address})...", "info")
        
        if address not in self.connected_devices:
            messagebox.showerror("Error", "Sensor not connected!")
            return
        
        device = self.connected_devices[address]
        
        try:
            # Disable all buttons during identification
            for btn in self.identify_buttons.values():
                btn.config(state='disabled', text="⏳ Wait...")
            
            # Start identification in background
            thread = threading.Thread(target=self._perform_identification, args=(device, address, index))
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            self.log(f"Error identifying sensor: {e}", "error")
            messagebox.showerror("Error", f"Could not identify sensor: {e}")
            self._reset_identify_buttons()
    
    def _perform_identification(self, device, address: str, index: int):
        """Perform the actual LED identification"""
        try:
            # Method 1: Try startMeasurement briefly (makes LED change pattern)
            self.log(f"Making Sensor {index + 1} LED blink...", "info")
            
            # Start and stop measurement quickly - this changes LED pattern
            for _ in range(3):  # Blink 3 times
                device.startMeasurement(movelladot_pc_sdk.XsPayloadMode_OrientationQuaternion)
                time.sleep(0.5)
                device.stopMeasurement()
                time.sleep(0.5)
            
            self.log(f"Sensor {index + 1} identification complete", "success")
            
        except Exception as e:
            self.log(f"Identification method failed: {e}", "warning")
            # If that doesn't work, just log it
            self.root.after(0, lambda: messagebox.showinfo(
                f"Sensor {index + 1}",
                f"Please look for the sensor with MAC address:\n{address}\n\n"
                f"Note: LED control may not be available on all SDK versions."
            ))
        
        finally:
            # Re-enable buttons
            self.root.after(0, self._reset_identify_buttons)
    
    def _reset_identify_buttons(self):
        """Reset all identify buttons"""
        for btn in self.identify_buttons.values():
            btn.config(state='normal', text="💡 Identify This Sensor")
    
    def show_assignment_screen(self):
        """Show body position assignment screen"""
        self.clear_content()
        self.update_progress(5)
        self.log("Ready to assign body positions", "info")
        self.identification_active = False
        
        # Main assignment frame
        assign_frame = tk.Frame(self.content_frame, bg=self.colors['bg'])
        assign_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Title
        title = tk.Label(assign_frame,
                        text="🎯 Assign Sensors to Body Positions",
                        font=('Arial', 16, 'bold'),
                        bg=self.colors['bg'],
                        fg=self.colors['fg'])
        title.pack(pady=(0, 10))
        
        # Body positions
        self.positions = {
            'upper_right_arm': 'Upper Right Arm',
            'lower_right_arm': 'Lower Right Arm (Forearm)',
            'upper_left_arm': 'Upper Left Arm',
            'lower_left_arm': 'Lower Left Arm (Forearm)'
        }
        
        self.position_vars = {}
        self.assigned_sensors = set()
        
        # Create assignment cards
        cards_frame = tk.Frame(assign_frame, bg=self.colors['bg'])
        cards_frame.pack(fill=tk.BOTH, expand=True)
        
        for i, (pos_key, pos_label) in enumerate(self.positions.items()):
            card = self.create_assignment_card(cards_frame, pos_key, pos_label, i)
            card.pack(fill=tk.X, pady=5)
        
        # Buttons
        button_frame = tk.Frame(assign_frame, bg=self.colors['bg'])
        button_frame.pack(pady=20)
        
        confirm_btn = tk.Button(button_frame,
                               text="✓ Confirm Assignments",
                               font=('Arial', 12, 'bold'),
                               bg=self.colors['success'],
                               fg='white',
                               padx=20,
                               pady=10,
                               command=self.confirm_assignments,
                               cursor='hand2')
        confirm_btn.pack(side=tk.LEFT, padx=5)
        
        back_btn = tk.Button(button_frame,
                            text="← Back to Identification",
                            font=('Arial', 12),
                            bg=self.colors['card_bg'],
                            fg='white',
                            padx=20,
                            pady=10,
                            command=self.show_identification_screen,
                            cursor='hand2')
        back_btn.pack(side=tk.LEFT, padx=5)
    
    def create_assignment_card(self, parent, pos_key: str, pos_label: str, index: int):
        """Create an assignment card for a body position"""
        card = tk.Frame(parent, bg=self.colors['card_bg'], relief=tk.RAISED, bd=2)
        
        # Position label
        label_frame = tk.Frame(card, bg=self.colors['card_bg'])
        label_frame.pack(side=tk.LEFT, padx=15, pady=10)
        
        position_label = tk.Label(label_frame,
                                 text=pos_label,
                                 font=('Arial', 11, 'bold'),
                                 bg=self.colors['card_bg'],
                                 fg=self.colors['fg'])
        position_label.pack(anchor=tk.W)
        
        # Dropdown for sensor selection
        sensor_frame = tk.Frame(card, bg=self.colors['card_bg'])
        sensor_frame.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.X, expand=True)
        
        # Use custom labels if provided
        sensor_options = ['-- Select Sensor --']
        for i, device in enumerate(self.detected_devices):
            address = device.bluetoothAddress()
            custom_label = self.sensor_label_vars.get(address, tk.StringVar(value=f"Sensor_{i+1}")).get()
            sensor_options.append(f"{custom_label} ({address})")
        
        var = tk.StringVar(value=sensor_options[0])
        self.position_vars[pos_key] = var
        
        dropdown = ttk.Combobox(sensor_frame,
                               textvariable=var,
                               values=sensor_options,
                               state='readonly',
                               font=('Arial', 10),
                               width=40)
        dropdown.pack()
        dropdown.bind('<<ComboboxSelected>>', lambda e: self.on_sensor_selected(pos_key))
        
        return card
    
    def on_sensor_selected(self, pos_key: str):
        """Handle sensor selection"""
        selected = self.position_vars[pos_key].get()
        
        if selected != '-- Select Sensor --':
            # Extract sensor address
            address = selected.split('(')[1].split(')')[0]
            
            # Find sensor index
            sensor_idx = None
            for i, device in enumerate(self.detected_devices):
                if device.bluetoothAddress() == address:
                    sensor_idx = i
                    break
            
            if sensor_idx is None:
                return
            
            # Check if already assigned
            if sensor_idx in self.assigned_sensors:
                messagebox.showwarning("Already Assigned",
                                      "This sensor has already been assigned to another position.")
                self.position_vars[pos_key].set('-- Select Sensor --')
                return
            
            self.assigned_sensors.add(sensor_idx)
            self.log(f"Assigned {selected.split(' (')[0]} to {self.positions[pos_key]}", "info")
    
    def confirm_assignments(self):
        """Confirm sensor assignments and proceed"""
        # Check if at least one assignment is made
        assigned_positions = []
        
        for pos_key, var in self.position_vars.items():
            selected = var.get()
            if selected != '-- Select Sensor --':
                # Extract address
                address = selected.split('(')[1].split(')')[0]
                
                # Find device
                device = None
                for d in self.detected_devices:
                    if d.bluetoothAddress() == address:
                        device = d
                        break
                
                if device:
                    pos_label = self.positions[pos_key]
                    assigned_positions.append((device, pos_key, pos_label))
        
        if not assigned_positions:
            messagebox.showwarning("No Assignments",
                                  "Please assign at least one sensor to a body position.")
            return
        
        self.assigned_devices = assigned_positions
        self.log(f"Confirmed {len(assigned_positions)} assignment(s)", "success")
        
        # Store assignments in manager
        self.apply_assignments()
    
    def apply_assignments(self):
        """Apply assignments to manager"""
        try:
            # Use the already connected devices
            if self.dot_manager.connect_to_assigned_devices(self.assigned_devices):
                self.log("Assignments applied successfully!", "success")
                self.root.after(500, self.start_calibration)
            else:
                self.log("Failed to apply assignments", "error")
                messagebox.showerror("Error", "Failed to apply sensor assignments")
        except Exception as e:
            self.log(f"Assignment error: {e}", "error")
            messagebox.showerror("Error", str(e))
    
    def start_calibration(self):
        """Start calibration process"""
        self.update_progress(6)
        self.show_calibration_screen()
        
        # Run calibration in background
        thread = threading.Thread(target=self.perform_calibration)
        thread.daemon = True
        thread.start()
    
    def show_calibration_screen(self):
        """Show calibration screen"""
        self.clear_content()
        
        cal_frame = tk.Frame(self.content_frame, bg=self.colors['bg'])
        cal_frame.pack(expand=True)
        
        title = tk.Label(cal_frame,
                        text="📐 Sensor Calibration",
                        font=('Arial', 18, 'bold'),
                        bg=self.colors['bg'],
                        fg=self.colors['fg'])
        title.pack(pady=10)
        
        instructions = tk.Label(cal_frame,
                               text="Please place all sensors on a flat, stable surface.\n"
                                    "Keep them completely still during calibration.",
                               font=('Arial', 12),
                               bg=self.colors['bg'],
                               fg=self.colors['fg'],
                               justify=tk.CENTER)
        instructions.pack(pady=10)
        
        # Calibration progress
        self.cal_progress_label = tk.Label(cal_frame,
                                          text="Calibrating...",
                                          font=('Arial', 14),
                                          bg=self.colors['bg'],
                                          fg=self.colors['warning'])
        self.cal_progress_label.pack(pady=20)
    
    def perform_calibration(self):
        """Perform calibration"""
        self.log("Starting calibration...", "info")
        
        try:
            if self.dot_manager.calibrate_devices():
                self.log("Calibration successful!", "success")
                
                # Start measurement mode
                if self.dot_manager.start_measurement_mode():
                    self.log("Measurement mode started", "success")
                    self.root.after(500, self.show_completion_screen)
                else:
                    self.log("Failed to start measurement mode", "error")
            else:
                self.log("Calibration failed", "error")
                self.root.after(100, lambda: messagebox.showerror(
                    "Calibration Error",
                    "Calibration failed. Please try again."
                ))
        except Exception as e:
            self.log(f"Calibration error: {e}", "error")
            self.root.after(100, lambda: messagebox.showerror("Error", str(e)))
    
    def show_completion_screen(self):
        """Show setup completion screen"""
        self.clear_content()
        self.update_progress(7)
        self.setup_complete = True
        
        complete_frame = tk.Frame(self.content_frame, bg=self.colors['bg'])
        complete_frame.pack(expand=True)
        
        # Success icon and message
        success_label = tk.Label(complete_frame,
                                text="✅",
                                font=('Arial', 72),
                                bg=self.colors['bg'])
        success_label.pack(pady=10)
        
        title = tk.Label(complete_frame,
                        text="Setup Complete!",
                        font=('Arial', 24, 'bold'),
                        bg=self.colors['bg'],
                        fg=self.colors['success'])
        title.pack(pady=10)
        
        message = tk.Label(complete_frame,
                          text="All sensors are connected, calibrated,\nand ready for use!",
                          font=('Arial', 12),
                          bg=self.colors['bg'],
                          fg=self.colors['fg'],
                          justify=tk.CENTER)
        message.pack(pady=10)
        
        # Show assignments
        assignments_frame = tk.Frame(complete_frame, bg=self.colors['card_bg'], relief=tk.SUNKEN, bd=2)
        assignments_frame.pack(pady=20, padx=20, fill=tk.BOTH)
        
        assignments_title = tk.Label(assignments_frame,
                                     text="Body Position Assignments:",
                                     font=('Arial', 12, 'bold'),
                                     bg=self.colors['card_bg'],
                                     fg=self.colors['fg'])
        assignments_title.pack(pady=5)
        
        for pos_key, info in self.dot_manager.get_body_position_mapping().items():
            assignment_text = f"• {info['label']}: {info['address']}"
            assignment_label = tk.Label(assignments_frame,
                                       text=assignment_text,
                                       font=('Arial', 10),
                                       bg=self.colors['card_bg'],
                                       fg=self.colors['fg'])
            assignment_label.pack(anchor=tk.W, padx=20)
        
        assignments_frame.pack_configure(pady=5)
        
        # Close button
        close_btn = tk.Button(complete_frame,
                             text="✓ Done",
                             font=('Arial', 14, 'bold'),
                             bg=self.colors['success'],
                             fg='white',
                             padx=30,
                             pady=12,
                             command=self.close_window,
                             cursor='hand2')
        close_btn.pack(pady=20)
    
    def close_window(self):
        """Close the setup window"""
        if self.setup_complete:
            # Setup complete - just close window, DON'T cleanup manager
            if callable(self.on_complete):
                self.on_complete(self.dot_manager)
            self.root.destroy()
        else:
            if messagebox.askyesno("Exit Setup", "Are you sure you want to exit the setup?"):
                if self.dot_manager:
                    try:
                        self.dot_manager.cleanup()
                        self.dot_manager = None
                    except Exception as e:
                        self.log(f"Error during cleanup: {e}", "error")

                if callable(self.on_cancel):
                    self.on_cancel()
                self.root.destroy()
    def get_manager(self):
        """Get the configured manager (for external use)"""
        return self.dot_manager if self.setup_complete else None


def main():
    """Main function to run the setup GUI"""
    root = tk.Tk()
    app = DeviceSetupApp(root)
    
    # Handle window close
    root.protocol("WM_DELETE_WINDOW", app.close_window)
    
    root.mainloop()
    
    # Return manager if setup was completed
    return app.get_manager()


if __name__ == "__main__":
    manager = main()
    
    if manager:
        print("\n" + "="*60)
        print("Setup completed successfully!")
        print("Manager object is available for use.")
        print("="*60)
    else:
        print("\nSetup was cancelled or failed.")