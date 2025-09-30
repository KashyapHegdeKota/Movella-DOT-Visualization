from xdpchandler import *
import os
import time
import threading
from typing import List, Tuple, Dict
import csv
import keyboard

class MovellaDotManager:
    def __init__(self):
        self.handler = XdpcHandler()
        self.connected_devices = []
        self.device_info = {}  # Store device type and info
        
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
    
    def get_tracker_count(self):
        """Get user choice for number of trackers"""
        print("\n" + "="*60)
        print("MOVELLA DOT MULTI-TRACKER SETUP")
        print("="*60)
        print("How many DOT trackers do you want to connect?")
        print("  1. Single tracker")
        print("  2. Two trackers")
        print("  3. Three trackers")
        print("  4. Four trackers")
        print("  5. Five trackers")
        print("  6. Custom number (up to 10)")
        print("="*60)
        
        while True:
            choice = input("Enter your choice (1-6): ").strip()
            if choice in ['1', '2', '3', '4', '5']:
                return int(choice)
            elif choice == '6':
                while True:
                    try:
                        custom_num = int(input("Enter number of trackers (1-10): "))
                        if 1 <= custom_num <= 10:
                            return custom_num
                        print("Please enter a number between 1 and 10.")
                    except ValueError:
                        print("Please enter a valid number.")
            else:
                print("Invalid choice. Please enter a number 1-6.")
    
    def scan_for_devices(self):
        """Scan for available DOT devices"""
        print("\nScanning for Movella DOT devices...")
        print("Make sure your devices are powered on and discoverable.")
        
        # Scan for devices
        self.handler.scanForDots()
        detected = self.handler.detectedDots()
        
        print(f"Found {len(detected)} DOT device(s):")
        for i, device_info in enumerate(detected):
            print(f"  [{i}] Address: {device_info.bluetoothAddress()}")
        
        return detected
    
    def select_devices(self, detected_devices: List, num_trackers: int):
        """Allow user to select and label devices"""
        if len(detected_devices) < num_trackers:
            print(f"\nError: Found only {len(detected_devices)} device(s), but need {num_trackers}")
            return None
        
        selected_devices = []
        used_indices = set()
        
        print(f"\nSelect {num_trackers} device(s) and assign labels:")
        
        for i in range(num_trackers):
            print(f"\nDevice {i+1} of {num_trackers}:")
            
            # Show available devices
            print("Available devices:")
            for j, device_info in enumerate(detected_devices):
                if j not in used_indices:
                    print(f"  [{j}] {device_info.bluetoothAddress()}")
            
            # Get device selection
            while True:
                try:
                    choice = int(input("Enter device number: "))
                    if choice in used_indices:
                        print("Device already selected. Choose a different one.")
                        continue
                    if 0 <= choice < len(detected_devices):
                        break
                    else:
                        print(f"Invalid choice. Enter number between 0 and {len(detected_devices)-1}")
                except ValueError:
                    print("Please enter a valid number.")
            
            # Get device label
            default_label = f"tracker_{i+1}"
            label = input(f"Enter label for this device (default: {default_label}): ").strip()
            if not label:
                label = default_label
            
            selected_devices.append((detected_devices[choice], label))
            used_indices.add(choice)
            print(f"Selected: {detected_devices[choice].bluetoothAddress()} as '{label}'")
        
        return selected_devices
    
    def connect_to_devices(self, selected_devices: List[Tuple]):
        """Connect to selected devices"""
        print("\nConnecting to selected devices...")
        
        # Connect to all detected devices
        self.handler.connectDots()
        connected = self.handler.connectedDots()
        
        if len(connected) == 0:
            print("Could not connect to any devices!")
            return False
        
        print(f"Connected to {len(connected)} device(s)")
        
        # Match selected devices with connected ones
        self.connected_devices = []
        self.device_info = {}
        
        for device_info, label in selected_devices:
            target_address = device_info.bluetoothAddress()
            
            # Find the connected device
            connected_device = None
            for device in connected:
                if device.bluetoothAddress() == target_address:
                    connected_device = device
                    break
            
            if connected_device is None:
                print(f"Failed to connect to device {target_address} ({label})")
                return False
            
            self.connected_devices.append(connected_device)
            self.device_info[target_address] = {
                'label': label,
                'device': connected_device
            }
            
            print(f"✓ Connected to {label}: {target_address}")
        
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
        """Calibrate a single device"""
        device = self.connected_devices[0]
        address = device.bluetoothAddress()
        label = self.device_info[address]['label']
        
        print(f"Calibrating single device: {label}")
        print("\nCalibration Instructions:")
        print("1. Hold the device steady in your desired reference orientation")
        print("2. Press ENTER when ready to calibrate")
        
        input("Press ENTER to start calibration...")
        
        # Configure device
        if not self.configure_device(device, label):
            return False
        
        # Reset orientation
        print(f"Resetting orientation for {label}...")
        if device.resetOrientation(movelladot_pc_sdk.XRM_DefaultAlignment):
            print("✓ Orientation reset successful")
        else:
            print(f"⚠ Orientation reset failed: {device.lastResultText()}")
            return False
        
        print("✓ Single device calibration complete!")
        return True
    
    def _multi_device_calibration(self):
        """Calibrate multiple devices together"""
        print(f"Calibrating {len(self.connected_devices)} devices together")
        print("\nMulti-Device Calibration Instructions:")
        print("1. Position all devices in their desired reference orientations")
        print("2. Keep all devices steady during calibration")
        print("3. Press ENTER when all devices are positioned correctly")
        
        # Show device list
        print("\nDevices to calibrate:")
        for device in self.connected_devices:
            address = device.bluetoothAddress()
            label = self.device_info[address]['label']
            print(f"  • {label}: {address}")
        
        input("\nPress ENTER to start calibration...")
        
        # Configure all devices
        print("\nConfiguring devices...")
        for i, device in enumerate(self.connected_devices):
            address = device.bluetoothAddress()
            label = self.device_info[address]['label']
            print(f"\nConfiguring device {i+1}/{len(self.connected_devices)}:")
            if not self.configure_device(device, label):
                return False
            # Small delay between device configurations
            if i < len(self.connected_devices) - 1:
                time.sleep(1)
        
        # Synchronize calibration
        print("\nPerforming synchronized calibration...")
        
        # Create threads for simultaneous calibration
        calibration_results = {}
        calibration_threads = []
        
        def calibrate_device(device, label):
            print(f"  Starting calibration for {label}...")

            # Start measurement mode first
            if not device.startMeasurement(movelladot_pc_sdk.XsPayloadMode_ExtendedQuaternion):
                print(f"  ⚠ Failed to start measurement on {label}: {device.lastResultText()}")
                calibration_results[label] = {'success': False, 'message': device.lastResultText()}
                return

            time.sleep(0.5)  # give it a moment to start

            # Now reset orientation
            success = device.resetOrientation(movelladot_pc_sdk.XRM_DefaultAlignment)
            calibration_results[label] = {
                'success': success,
                'message': device.lastResultText() if not success else 'Success'
            }

            # Optionally stop measurement after calibration
            device.stopMeasurement()

        # Start calibration threads
        for device in self.connected_devices:
            address = device.bluetoothAddress()
            label = self.device_info[address]['label']
            thread = threading.Thread(target=calibrate_device, args=(device, label))
            calibration_threads.append(thread)
            thread.start()
        
        # Wait for all calibrations to complete
        for thread in calibration_threads:
            thread.join()
        
        # Check results
        print("\nCalibration Results:")
        all_successful = True
        for device in self.connected_devices:
            address = device.bluetoothAddress()
            label = self.device_info[address]['label']
            result = calibration_results[label]
            
            if result['success']:
                print(f"  ✓ {label}: Calibration successful")
            else:
                print(f"  ✗ {label}: Calibration failed - {result['message']}")
                all_successful = False
        
        if all_successful:
            print("\n✓ All devices calibrated successfully!")
            
            # Optional: Verify calibration by checking orientation sync
            if len(self.connected_devices) > 1:
                self._verify_calibration_sync()
            
            return True
        else:
            print("\n⚠ Some devices failed calibration. Please retry.")
            return False
    
    def _verify_calibration_sync(self):
        """Verify that calibrated devices are synchronized"""
        print("\nVerifying calibration synchronization...")
        print("Move all devices together and observe if orientations stay synchronized")
        print("Press ENTER to start verification (10 seconds)...")
        
        input()
        
        # Start measurement on all devices
        measurement_started = []
        for device in self.connected_devices:
            address = device.bluetoothAddress()
            label = self.device_info[address]['label']
            
            if device.startMeasurement(movelladot_pc_sdk.XsPayloadMode_ExtendedQuaternion):
                measurement_started.append(device)
                print(f"  ✓ Started measurement on {label}")
            else:
                print(f"  ⚠ Failed to start measurement on {label}")
        
        if not measurement_started:
            print("No devices available for verification")
            return
        
        print("\nCalibration verification (10 seconds):")
        print("Move all devices together to check synchronization...")
        
        start_time = time.time()
        while time.time() - start_time < 10:
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
                # This is a simple check - you might need to adjust based on SDK
                if device.isMeasuring():
                    return True
            except:
                pass
        return False
    

def record_quaternions_to_csv(manager, filename: str):
    """
    Record quaternion data from all connected devices to a CSV file.
    The recording starts when the SPACE bar is pressed and stops when BACKSPACE is pressed.
    """
    # Get the list of connected device objects and their information
    connected_devices_info = manager.get_connected_devices()
    
    # Check if any devices are connected before proceeding
    if not connected_devices_info:
        print("Error: No devices are connected. Cannot start recording.")
        return
        
    num_devices = len(connected_devices_info)
    print(f"Found {num_devices} connected device(s).")

    # Extract the Bluetooth address and label for each device
    addresses = [dev[0].bluetoothAddress() for dev in connected_devices_info]
    labels = [dev[1]['label'] for dev in connected_devices_info]
    
    print("\nPress SPACE to start recording.")
    print("Press BACKSPACE to stop recording.")
    
    # Wait for the user to press the space bar to start
    while not keyboard.is_pressed('space'):
        time.sleep(0.01)

    print("\n▶️ Recording started... (Press BACKSPACE to stop)")

    try:
        with open(filename, "w", newline='') as f:
            writer = csv.writer(f)
            
            # Create a dynamic header row based on device labels
            # e.g., ["tracker_1_WXYZ", "tracker_2_WXYZ", "tracker_3_WXYZ"]
            header = [f"{label}_WXYZ" for label in labels]
            writer.writerow(header)
            
            # Loop until the user presses the backspace key
            while not keyboard.is_pressed('backspace'):
                # Check if there are any available data packets from the devices
                if manager.handler.packetsAvailable():
                    # Prepare a list to hold data for one row (one sample from each device)
                    row_data = [None] * num_devices
                    
                    # Try to get the next packet for each connected device
                    for i, addr in enumerate(addresses):
                        packet = manager.handler.getNextPacket(addr)
                        
                        # If a valid packet with orientation data is found, process it
                        if packet and packet.containsOrientation():
                            quat = packet.orientationQuaternion()
                            # Format the quaternion data as a "W,X,Y,Z" string
                            row_data[i] = f"{quat[0]:.4f},{quat[1]:.4f},{quat[2]:.4f},{quat[3]:.4f}"
                    
                    # Write the row to the CSV only if we received data from ALL devices
                    # This ensures that each row in the CSV is a complete, synchronized sample
                    if all(cell is not None for cell in row_data):
                        writer.writerow(row_data)
                
                # A small delay to prevent the loop from using 100% CPU
                time.sleep(0.01)
                
    except Exception as e:
        print(f"\nAn error occurred during recording: {e}")
    finally:
        print(f"\n⏹️ Recording stopped. Data saved to {filename}")


def setup_movella_dots():
    """
    Complete setup function for Movella DOT trackers.
    Returns MovellaDotManager instance if successful, None if failed.
    """
    manager = MovellaDotManager()
    
    try:
        # Initialize
        if not manager.initialize():
            print("Failed to initialize. Exiting.")
            return None
        
        # Get number of trackers
        num_trackers = manager.get_tracker_count()
        print(f"\nConfiguring for {num_trackers} tracker(s)")
        
        # Scan for devices
        detected_devices = manager.scan_for_devices()
        if not detected_devices:
            print("No devices found. Make sure devices are powered on and discoverable.")
            return None
        
        # Select devices
        selected_devices = manager.select_devices(detected_devices, num_trackers)
        if not selected_devices:
            print("Device selection failed.")
            return None
        
        # Connect to devices
        if not manager.connect_to_devices(selected_devices):
            print("Failed to connect to devices.")
            return None
        
        # Calibrate devices
        if not manager.calibrate_devices():
            print("Calibration failed.")
            return None
        
        # Start measurement mode
        if manager.start_measurement_mode():
            print("\n" + "="*60)
            print("SETUP COMPLETE!")
            print("All devices are connected, calibrated, and ready for use.")
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
        if manager:
            manager.cleanup()
        return None 

def main():
    """Standalone main function for testing"""
    manager = setup_movella_dots()
    
    if manager:
        try:
            print("\nPress ENTER to exit...")
            input()
        except KeyboardInterrupt:
            print("\nExiting...")
        finally:
            manager.cleanup()
            print("Cleanup complete. Goodbye!")
    else:
        print("Setup failed.")

if __name__ == "__main__":
    main()