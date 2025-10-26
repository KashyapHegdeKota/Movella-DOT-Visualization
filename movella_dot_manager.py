from xdpchandler import *
import os
import time
import threading
from typing import List, Tuple, Dict
import csv
import time
import keyboard

class MovellaDotManager:
    def __init__(self):
        self.handler = XdpcHandler()
        self.connected_devices = []
        self.device_info = {}  # Store device type and info
        self.body_positions = {}  # Map addresses to body positions
        
    def initialize(self):
        """Initialize the XdpcHandler"""
        print("Initializing Movella DOT SDK...")
        if not self.handler.initialize():
            print("Failed to initialize XdpcHandler")
            return False
        print("SDK initialized successfully!")
        return True
    
    def cleanup(self):
        """Clean up resources"""
        print("Cleaning up...")
        
        # Stop measurement on all connected devices
        for device in self.connected_devices:
            try:
                address = device.bluetoothAddress()
                label = self.device_info.get(address, {}).get('label', 'Unknown')
                print(f"  Stopping measurement on {label}...")
                device.stopMeasurement()
            except Exception as e:
                print(f"  Warning: Error stopping device: {e}")
        
        # Cleanup handler
        self.handler.cleanup()
    
    def scan_and_identify_active_sensors(self):
        """Scan for and identify all active DOT sensors"""
        print("\n" + "="*60)
        print("SCANNING FOR ACTIVE MOVELLA DOT SENSORS")
        print("="*60)
        print("Make sure all your sensors are powered on and discoverable.")
        print("Scanning for 5 seconds...")
        
        # Scan for devices
        self.handler.scanForDots()
        time.sleep(5)  # Give it time to find all devices
        detected = self.handler.detectedDots()
        
        if not detected:
            print("\n⚠ No sensors found!")
            print("Please ensure sensors are:")
            print("  - Powered on (LED should be blinking)")
            print("  - Within Bluetooth range")
            print("  - Not connected to another device")
            return None
        
        print(f"\n✓ Found {len(detected)} active sensor(s):")
        print("-" * 60)
        for i, device_info in enumerate(detected):
            address = device_info.bluetoothAddress()
            print(f"  Sensor {i+1}: {address}")
        print("-" * 60)
        
        return detected
    
    def assign_body_positions(self, detected_devices: List):
        """Interactive menu to assign body positions to detected sensors"""
        print("\n" + "="*60)
        print("ASSIGN SENSORS TO BODY POSITIONS")
        print("="*60)
        
        # Define available body positions
        available_positions = [
            "upper_right_arm",
            "lower_right_arm", 
            "upper_left_arm",
            "lower_left_arm"
        ]
        
        position_labels = {
            "upper_right_arm": "Upper Right Arm",
            "lower_right_arm": "Lower Right Arm (Forearm)",
            "upper_left_arm": "Upper Left Arm",
            "lower_left_arm": "Lower Left Arm (Forearm)"
        }
        
        num_sensors = len(detected_devices)
        num_positions = min(num_sensors, len(available_positions))
        
        print(f"\nYou have {num_sensors} sensor(s) to assign.")
        print(f"Available body positions:")
        for i, pos in enumerate(available_positions[:num_positions]):
            print(f"  {i+1}. {position_labels[pos]}")
        
        assigned_devices = []
        used_sensor_indices = set()
        used_positions = set()
        
        # Assignment loop
        for assignment_num in range(num_positions):
            print(f"\n--- Assignment {assignment_num + 1} of {num_positions} ---")
            
            # Show available sensors
            print("\nAvailable sensors:")
            for i, device_info in enumerate(detected_devices):
                if i not in used_sensor_indices:
                    print(f"  [{i+1}] {device_info.bluetoothAddress()}")
            
            # Get sensor selection
            while True:
                try:
                    sensor_choice = input(f"\nSelect sensor number (1-{num_sensors}): ").strip()
                    sensor_idx = int(sensor_choice) - 1
                    
                    if sensor_idx < 0 or sensor_idx >= num_sensors:
                        print(f"Invalid choice. Enter a number between 1 and {num_sensors}.")
                        continue
                    
                    if sensor_idx in used_sensor_indices:
                        print("That sensor has already been assigned. Choose another.")
                        continue
                    
                    break
                except ValueError:
                    print("Please enter a valid number.")
            
            # Show available body positions
            print("\nAvailable body positions:")
            for i, pos in enumerate(available_positions):
                if pos not in used_positions:
                    print(f"  [{i+1}] {position_labels[pos]}")
            
            # Get position selection
            while True:
                try:
                    pos_choice = input(f"Assign to position (1-{len(available_positions)}): ").strip()
                    pos_idx = int(pos_choice) - 1
                    
                    if pos_idx < 0 or pos_idx >= len(available_positions):
                        print(f"Invalid choice. Enter a number between 1 and {len(available_positions)}.")
                        continue
                    
                    selected_position = available_positions[pos_idx]
                    
                    if selected_position in used_positions:
                        print("That position has already been assigned. Choose another.")
                        continue
                    
                    break
                except ValueError:
                    print("Please enter a valid number.")
            
            # Confirm assignment
            device = detected_devices[sensor_idx]
            address = device.bluetoothAddress()
            position_label = position_labels[selected_position]
            
            print(f"\n✓ Assigned: {address}")
            print(f"  → {position_label}")
            
            assigned_devices.append((device, selected_position, position_label))
            used_sensor_indices.add(sensor_idx)
            used_positions.add(selected_position)
        
        # Summary
        print("\n" + "="*60)
        print("ASSIGNMENT SUMMARY")
        print("="*60)
        for device_info, position_key, position_label in assigned_devices:
            print(f"  {position_label}: {device_info.bluetoothAddress()}")
        print("="*60)
        
        return assigned_devices
    
    def connect_to_assigned_devices(self, assigned_devices: List[Tuple]):
        """Connect to the assigned devices"""
        print("\n" + "="*60)
        print("CONNECTING TO SENSORS")
        print("="*60)
        
        # Connect to all detected devices
        self.handler.connectDots()
        connected = self.handler.connectedDots()
        
        if len(connected) == 0:
            print("⚠ Could not connect to any devices!")
            return False
        
        print(f"✓ Connected to {len(connected)} device(s)")
        
        # Match assigned devices with connected ones
        self.connected_devices = []
        self.device_info = {}
        self.body_positions = {}
        
        for device_info, position_key, position_label in assigned_devices:
            target_address = device_info.bluetoothAddress()
            
            # Find the connected device
            connected_device = None
            for device in connected:
                if device.bluetoothAddress() == target_address:
                    connected_device = device
                    break
            
            if connected_device is None:
                print(f"⚠ Failed to connect to {position_label} ({target_address})")
                return False
            
            self.connected_devices.append(connected_device)
            self.device_info[target_address] = {
                'label': position_label,
                'position_key': position_key,
                'device': connected_device
            }
            self.body_positions[position_key] = connected_device
            
            print(f"  ✓ {position_label}: {target_address}")
        
        print("="*60)
        return True
    
    def configure_device(self, device, label: str):
        """Configure a single device for calibration"""
        print(f"\nConfiguring {label}...")
        
        # Set filter profile
        try:
            current_profile = device.onboardFilterProfile().label()
            if current_profile != "General":
                print(f"  Setting filter profile to General...")
                if device.setOnboardFilterProfile("General"):
                    print(f"  ✓ Filter profile set to General")
                else:
                    print(f"  ⚠ Failed to set filter profile, using: {current_profile}")
            else:
                print(f"  ✓ Filter profile already set to General")
        except Exception as e:
            print(f"  ⚠ Error with filter profile: {e}")
        
        time.sleep(0.5)
        
        # Configure for quaternion output
        print(f"  Setting quaternion output mode...")
        device.setLogOptions(movelladot_pc_sdk.XsLogOptions_Quaternion)
        
        return True
    
    def calibrate_devices(self):
        """Perform calibration on all connected devices"""
        print("\n" + "="*60)
        print("DEVICE CALIBRATION")
        print("="*60)
        
        if len(self.connected_devices) == 1:
            return self._single_device_calibration()
        else:
            return self._multi_device_calibration()
    
    def _single_device_calibration(self):
        """Calibration for single device"""
        device = self.connected_devices[0]
        address = device.bluetoothAddress()
        label = self.device_info[address]['label']
        
        print(f"\n📱 Calibrating {label}...")
        print("\nCalibration Instructions:")
        print("1. Place the sensor on a flat, stable surface")
        print("2. Keep it completely still for 5 seconds")
        print("3. Calibration will start automatically")
        
        input("\nPress ENTER when the sensor is ready on a flat surface...")
        
        if not self.configure_device(device, label):
            return False
        
        print("\n⏱ Calibrating... Keep sensor still!")
        time.sleep(5)
        
        print(f"✓ Calibration complete for {label}!")
        return True
    
    def _multi_device_calibration(self):
        """Calibration for multiple devices"""
        print("\n📱 Multi-Device Calibration")
        print("\nYou can calibrate devices in two ways:")
        print("  1. Sequential (one at a time) - more accurate")
        print("  2. Simultaneous (all at once) - faster")
        
        while True:
            choice = input("\nChoose calibration method (1 or 2): ").strip()
            if choice in ['1', '2']:
                break
            print("Please enter 1 or 2")
        
        if choice == '1':
            return self._sequential_calibration()
        else:
            return self._simultaneous_calibration()
    
    def _sequential_calibration(self):
        """Calibrate devices one by one"""
        print("\n--- Sequential Calibration ---")
        
        for device in self.connected_devices:
            address = device.bluetoothAddress()
            label = self.device_info[address]['label']
            
            print(f"\n📱 Calibrating {label}")
            print("Instructions:")
            print("  1. Place this sensor on a flat, stable surface")
            print("  2. Keep it completely still")
            
            input(f"\nPress ENTER when {label} is ready...")
            
            if not self.configure_device(device, label):
                return False
            
            print(f"⏱ Calibrating {label}... Keep still!")
            time.sleep(5)
            
            print(f"✓ {label} calibrated!")
        
        print("\n✓ All devices calibrated!")
        return True
    
    def _simultaneous_calibration(self):
        """Calibrate all devices at once"""
        print("\n--- Simultaneous Calibration ---")
        print("\nInstructions:")
        print("  1. Place ALL sensors on a flat, stable surface")
        print("  2. Keep them all completely still")
        print("\nSensor positions:")
        
        for device in self.connected_devices:
            address = device.bluetoothAddress()
            label = self.device_info[address]['label']
            print(f"  • {label}: {address}")
        
        input("\nPress ENTER when ALL sensors are ready on flat surfaces...")
        
        # Configure all devices
        for device in self.connected_devices:
            address = device.bluetoothAddress()
            label = self.device_info[address]['label']
            if not self.configure_device(device, label):
                return False
        
        print("\n⏱ Calibrating ALL sensors... Keep still!")
        time.sleep(5)
        
        print("✓ All sensors calibrated!")
        return True
    
    def verify_calibration(self):
        """Verify calibration by showing orientation data"""
        print("\n" + "="*60)
        print("CALIBRATION VERIFICATION")
        print("="*60)
        print("Starting brief measurement to verify calibration...")
        print("(This will run for 5 seconds)")
        
        measurement_started = []
        
        for device in self.connected_devices:
            address = device.bluetoothAddress()
            label = self.device_info[address]['label']
            
            if device.startMeasurement(movelladot_pc_sdk.XsPayloadMode_ExtendedQuaternion):
                measurement_started.append(device)
            else:
                print(f"⚠ Could not start measurement on {label}")
        
        if not measurement_started:
            print("Could not start measurement on any devices for verification")
            return
        
        print("\nOrientation data (W, X, Y, Z quaternions):")
        print("-" * 60)
        
        start_time = time.time()
        while time.time() - start_time < 5:
            if self.handler.packetsAvailable():
                line = f"Time: {time.time() - start_time:5.1f}s | "
                
                for device in measurement_started:
                    address = device.bluetoothAddress()
                    label = self.device_info[address]['label']
                    
                    packet = self.handler.getNextPacket(address)
                    if packet and packet.containsOrientation():
                        quat = packet.orientationQuaternion()
                        line += f"{label}: W:{quat[0]:5.2f} X:{quat[1]:5.2f} Y:{quat[2]:5.2f} Z:{quat[3]:5.2f} | "
                
                print(f"\r{line}", end="", flush=True)
            time.sleep(0.1)
        
        print("\n")
        
        # Stop measurements
        for device in measurement_started:
            device.stopMeasurement()
        
        print("✓ Calibration verification complete!")
    
    def start_measurement_mode(self):
        """Start measurement mode on all devices"""
        print("\n" + "="*60)
        print("STARTING MEASUREMENT MODE")
        print("="*60)
        
        active_devices = []
        
        for device in self.connected_devices:
            address = device.bluetoothAddress()
            label = self.device_info[address]['label']
            
            print(f"Starting measurement on {label}...")
            
            # Try different payload modes
            success = False
            payload_modes = [
                (movelladot_pc_sdk.XsPayloadMode_ExtendedQuaternion, "ExtendedQuaternion"),
                (movelladot_pc_sdk.XsPayloadMode_CompleteQuaternion, "CompleteQuaternion"),
                (movelladot_pc_sdk.XsPayloadMode_OrientationQuaternion, "OrientationQuaternion")
            ]
            
            for mode, mode_name in payload_modes:
                if device.startMeasurement(mode):
                    print(f"  ✓ Started with {mode_name} mode")
                    active_devices.append(device)
                    success = True
                    break
                else:
                    print(f"  ⚠ Failed with {mode_name}: {device.lastResultText()}")
            
            if not success:
                print(f"  ✗ Could not start measurement on {label}")
        
        if not active_devices:
            print("No devices in measurement mode!")
            return False
        
        print(f"\n✓ {len(active_devices)} device(s) in measurement mode")
        return True

    def get_connected_devices(self):
        """Get list of connected devices with their info"""
        return [(device, self.device_info[device.bluetoothAddress()]) 
                for device in self.connected_devices]
    
    def get_device_by_position(self, position_key: str):
        """Get device by body position key (e.g., 'upper_right_arm')"""
        return self.body_positions.get(position_key)
    
    def get_device_by_label(self, label: str):
        """Get device by its label"""
        for address, info in self.device_info.items():
            if info['label'] == label:
                return info['device']
        return None
    
    def is_measurement_active(self):
        """Check if any devices are in measurement mode"""
        for device in self.connected_devices:
            try:
                if device.isMeasuring():
                    return True
            except:
                pass
        return False
    
    def get_body_position_mapping(self):
        """Return dictionary mapping body positions to device addresses"""
        mapping = {}
        for address, info in self.device_info.items():
            position_key = info['position_key']
            mapping[position_key] = {
                'address': address,
                'label': info['label'],
                'device': info['device']
            }
        return mapping


def record_arm_quaternions_to_csv(manager, filename: str):
    """
    Record quaternion data from arm sensors to CSV file.
    Works with any number of assigned arm positions (1-4).
    Press SPACE to start, BACKSPACE to stop.
    """
    position_mapping = manager.get_body_position_mapping()
    
    if not position_mapping:
        print("No sensors assigned!")
        return
    
    print("\n" + "="*60)
    print("RECORDING ARM SENSOR DATA")
    print("="*60)
    print(f"Recording data from {len(position_mapping)} sensor(s):")
    for pos_key, info in position_mapping.items():
        print(f"  • {info['label']}: {info['address']}")
    
    print("\nControls:")
    print("  SPACE     - Start recording")
    print("  BACKSPACE - Stop recording")
    print("="*60)
    
    # Wait for start
    print("\nPress SPACE to start recording...")
    while True:
        if keyboard.is_pressed('space'):
            break
        time.sleep(0.1)
    
    print("🔴 Recording started... Press BACKSPACE to stop.\n")
    
    # Prepare CSV header
    header = []
    position_keys = sorted(position_mapping.keys())  # Consistent ordering
    for pos_key in position_keys:
        label = position_mapping[pos_key]['label'].replace(' ', '_')
        header.append(f"{label}_W")
        header.append(f"{label}_X")
        header.append(f"{label}_Y")
        header.append(f"{label}_Z")
    
    with open(filename, "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        
        start_time = time.time()
        samples_written = 0
        
        while True:
            if keyboard.is_pressed('backspace'):
                print("\n⏹ Recording stopped.")
                break
            
            if manager.handler.packetsAvailable():
                row = []
                all_data_available = True
                
                for pos_key in position_keys:
                    address = position_mapping[pos_key]['address']
                    packet = manager.handler.getNextPacket(address)
                    
                    if packet and packet.containsOrientation():
                        quat = packet.orientationQuaternion()
                        row.extend([quat[0], quat[1], quat[2], quat[3]])
                    else:
                        all_data_available = False
                        break
                
                # Only write if we have data from all sensors
                if all_data_available:
                    writer.writerow(row)
                    samples_written += 1
                    
                    # Print status every 100 samples
                    if samples_written % 100 == 0:
                        elapsed = time.time() - start_time
                        print(f"\rSamples: {samples_written} | Time: {elapsed:.1f}s | Rate: {samples_written/elapsed:.1f} Hz", end="", flush=True)
            
            time.sleep(0.01)  # Small delay to avoid busy waiting
    
    elapsed = time.time() - start_time
    print(f"\n\n✓ Recording complete!")
    print(f"  Samples: {samples_written}")
    print(f"  Duration: {elapsed:.1f}s")
    print(f"  Average rate: {samples_written/elapsed:.1f} Hz")
    print(f"  File: {filename}")


def setup_movella_dots_with_positions():
    """
    Complete setup function for Movella DOT trackers with body position assignment.
    Returns MovellaDotManager instance if successful, None if failed.
    """
    manager = MovellaDotManager()
    
    try:
        # Initialize
        if not manager.initialize():
            print("Failed to initialize. Exiting.")
            return None
        
        # Scan and identify all active sensors
        detected_devices = manager.scan_and_identify_active_sensors()
        if not detected_devices:
            print("No active sensors found.")
            return None
        
        # Assign body positions
        assigned_devices = manager.assign_body_positions(detected_devices)
        if not assigned_devices:
            print("Position assignment failed.")
            return None
        
        # Connect to assigned devices
        if not manager.connect_to_assigned_devices(assigned_devices):
            print("Failed to connect to devices.")
            return None
        
        # Calibrate devices
        if not manager.calibrate_devices():
            print("Calibration failed.")
            return None
        
        # Start measurement mode
        if manager.start_measurement_mode():
            print("\n" + "="*60)
            print("✓ SETUP COMPLETE!")
            print("="*60)
            print("All sensors are connected, calibrated, and ready for use.")
            print("\nBody position assignments:")
            for pos_key, info in manager.get_body_position_mapping().items():
                print(f"  • {info['label']}: {info['address']}")
            print("="*60)
            return manager
        else:
            print("Failed to start measurement mode.")
            return None
        
    except KeyboardInterrupt:
        print("\n\nOperation interrupted by user.")
        if manager:
            manager.cleanup()
        return None
    
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        import traceback
        traceback.print_exc()
        if manager:
            manager.cleanup()
        return None


def main():
    """Main function with example usage"""
    print("="*60)
    print("MOVELLA DOT ARM TRACKING SETUP")
    print("="*60)
    
    # Setup sensors with position assignment
    manager = setup_movella_dots_with_positions()
    
    if manager:
        try:
            # Show menu
            print("\n" + "="*60)
            print("MAIN MENU")
            print("="*60)
            print("1. Record data to CSV")
            print("2. Show live data (5 seconds)")
            print("3. Exit")
            print("="*60)
            
            while True:
                choice = input("\nEnter choice (1-3): ").strip()
                
                if choice == '1':
                    filename = input("Enter filename (e.g., arm_data.csv): ").strip()
                    if not filename:
                        filename = f"arm_data_{int(time.time())}.csv"
                    record_arm_quaternions_to_csv(manager, filename)
                    
                elif choice == '2':
                    print("\nShowing live data for 5 seconds...")
                    start = time.time()
                    while time.time() - start < 5:
                        if manager.handler.packetsAvailable():
                            line = f"Time: {time.time() - start:5.1f}s | "
                            for device in manager.connected_devices:
                                addr = device.bluetoothAddress()
                                label = manager.device_info[addr]['label']
                                packet = manager.handler.getNextPacket(addr)
                                if packet and packet.containsOrientation():
                                    quat = packet.orientationQuaternion()
                                    line += f"{label}: W:{quat[0]:5.2f} X:{quat[1]:5.2f} Y:{quat[2]:5.2f} Z:{quat[3]:5.2f} | "
                            print(f"\r{line}", end="", flush=True)
                        time.sleep(0.1)
                    print("\n")
                    
                elif choice == '3':
                    print("\nExiting...")
                    break
                else:
                    print("Invalid choice. Please enter 1, 2, or 3.")
            
        except KeyboardInterrupt:
            print("\n\nExiting...")
        finally:
            manager.cleanup()
            print("Cleanup complete. Goodbye!")
    else:
        print("Setup failed.")


if __name__ == "__main__":
    main()