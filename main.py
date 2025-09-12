from xdpchandler import *
import os
import time

def get_user_choice():
    """Get user choice for number of trackers"""
    print("\n" + "="*50)
    print("MOVELLA DOT TRACKER CONFIGURATION")
    print("="*50)
    print("Choose your setup:")
    print("1. Single tracker (forearm only)")
    print("2. Dual trackers (forearm + upper arm)")
    print("="*50)
    
    while True:
        choice = input("Enter your choice (1 or 2): ").strip()
        if choice in ['1', '2']:
            return int(choice)
        print("Invalid choice. Please enter 1 or 2.")

def select_devices(detected_devices, num_trackers):
    """Allow user to select which devices to use"""
    print(f"\nFound {len(detected_devices)} device(s):")
    for i, portInfo in enumerate(detected_devices):
        print(f"  {i}: {portInfo.bluetoothAddress()}")
    
    selected_devices = []
    
    if num_trackers == 1:
        print("\nSelect the tracker for your forearm (3 inches below elbow):")
        while True:
            try:
                choice = int(input("Enter device number: "))
                if 0 <= choice < len(detected_devices):
                    selected_devices.append((detected_devices[choice], "forearm"))
                    break
                else:
                    print(f"Invalid choice. Enter number between 0 and {len(detected_devices)-1}")
            except ValueError:
                print("Please enter a valid number.")
    
    else:  # num_trackers == 2
        print("\nSelect the tracker for your FOREARM (3 inches below elbow):")
        while True:
            try:
                choice = int(input("Enter device number: "))
                if 0 <= choice < len(detected_devices):
                    selected_devices.append((detected_devices[choice], "forearm"))
                    break
                else:
                    print(f"Invalid choice. Enter number between 0 and {len(detected_devices)-1}")
            except ValueError:
                print("Please enter a valid number.")
        
        print("\nSelect the tracker for your UPPER ARM (above elbow):")
        while True:
            try:
                choice = int(input("Enter device number: "))
                if 0 <= choice < len(detected_devices):
                    if choice != selected_devices[0][0]:
                        selected_devices.append((detected_devices[choice], "upper_arm"))
                        break
                    else:
                        print("You already selected this device. Choose a different one.")
                else:
                    print(f"Invalid choice. Enter number between 0 and {len(detected_devices)-1}")
            except ValueError:
                print("Please enter a valid number.")
    
    return selected_devices

def configure_device(device, device_type):
    """Configure a single device"""
    print(f"\nConfiguring {device_type} tracker: {device.bluetoothAddress()}")
    
    # Wait a moment for the device to be ready
    time.sleep(1)
    
    # Configure the device
    filterProfiles = device.getAvailableFilterProfiles()
    print(f"Available filter profiles for {device_type}:")
    for f in filterProfiles:
        print(f"  {f.label()}")
    print(f"Current profile: {device.onboardFilterProfile().label()}")
    
    # Set filter profile if needed
    current_profile = device.onboardFilterProfile().label()
    if current_profile != "General":
        print(f"Setting filter profile to General for {device_type}...")
        if device.setOnboardFilterProfile("General"):
            print(f"Successfully set profile to General for {device_type}")
            time.sleep(0.5)
        else:
            print(f"Setting filter profile failed for {device_type}! Continuing with current profile: {current_profile}")
    else:
        print(f"Filter profile is already set to General for {device_type}")
    
    print(f"Setting quaternion CSV output for {device_type}")
    device.setLogOptions(movelladot_pc_sdk.XsLogOptions_Quaternion)
    time.sleep(0.5)
    
    # Setup logging
    logFileName = f"logfile_{device_type}_{device.bluetoothAddress().replace(':', '-')}.csv"
    if os.path.exists(logFileName):
        os.remove(logFileName)
    print(f"Enable logging to: {logFileName}")
    if not device.enableLogging(logFileName):
        print(f"Failed to enable logging for {device_type}. Reason: {device.lastResultText()}")
    time.sleep(0.5)
    
    # Start measurement
    print(f"Putting {device_type} device into measurement mode...")
    success = False
    payload_modes = [
        movelladot_pc_sdk.XsPayloadMode_ExtendedQuaternion,
        movelladot_pc_sdk.XsPayloadMode_CompleteQuaternion,
        movelladot_pc_sdk.XsPayloadMode_OrientationQuaternion
    ]
    
    for i, mode in enumerate(payload_modes):
        mode_name = ["ExtendedQuaternion", "CompleteQuaternion", "OrientationQuaternion"][i]
        print(f"Trying {mode_name} mode for {device_type}...")
        if device.startMeasurement(mode):
            print(f"Successfully started measurement with {mode_name} mode for {device_type}")
            success = True
            break
        else:
            print(f"Failed with {mode_name} for {device_type}: {device.lastResultText()}")
            time.sleep(1)
    
    if not success:
        print(f"Could not put {device_type} device into any measurement mode.")
        return False
    
    return True

if __name__ == "__main__":
    XdpcHandler = XdpcHandler()

    if not XdpcHandler.initialize():
        XdpcHandler.cleanup()
        exit(-1)
    
    # Get user choice
    num_trackers = get_user_choice()
    
    print(f"\nScanning for Movella DOT devices...")
    XdpcHandler.scanForDots()
    
    if len(XdpcHandler.detectedDots()) == 0:
        print("No Movella DOT device(s) found. Aborting.")
        XdpcHandler.cleanup()
        exit(-1)
    
    if len(XdpcHandler.detectedDots()) < num_trackers:
        print(f"Found only {len(XdpcHandler.detectedDots())} device(s), but need {num_trackers}. Aborting.")
        XdpcHandler.cleanup()
        exit(-1)
    
    # Let user select devices
    selected_devices = select_devices(XdpcHandler.detectedDots(), num_trackers)
    
    # Connect to all devices
    XdpcHandler.connectDots()
    
    if len(XdpcHandler.connectedDots()) == 0:
        print("Could not connect to any Movella DOT device(s). Aborting.")
        XdpcHandler.cleanup()
        exit(-1)
    
    # Find and configure selected devices
    active_devices = []
    for portInfo, device_type in selected_devices:
        target_address = portInfo.bluetoothAddress()
        device = None
        
        # Find the device among connected ones
        for connected_device in XdpcHandler.connectedDots():
            if connected_device.bluetoothAddress() == target_address:
                device = connected_device
                break
        
        if device is None:
            print(f"Target device {target_address} ({device_type}) was not connected successfully.")
            XdpcHandler.cleanup()
            exit(-1)
        
        print(f"Successfully connected to {device_type} tracker: {device.bluetoothAddress()}")
        
        # Configure the device
        if configure_device(device, device_type):
            active_devices.append((device, device_type))
        else:
            print(f"Failed to configure {device_type} device. Aborting.")
            XdpcHandler.cleanup()
            exit(-1)
    
    # Stop measurement on any other connected devices
    for connected_device in XdpcHandler.connectedDots():
        is_active = any(device.bluetoothAddress() == connected_device.bluetoothAddress() 
                       for device, _ in active_devices)
        if not is_active:
            print(f"Stopping unused device: {connected_device.bluetoothAddress()}")
            connected_device.stopMeasurement()
    
    # Recording phase
    recording_time = 20  # seconds
    print(f"\n" + "="*80)
    print(f"RECORDING DATA FOR {recording_time} SECONDS")
    print("="*80)
    
    if num_trackers == 1:
        print(f"Recording from FOREARM tracker: {active_devices[0][0].bluetoothAddress()}")
        print("Position: 3 inches below elbow")
    else:
        print("Recording from DUAL trackers:")
        for device, device_type in active_devices:
            position = "3 inches below elbow" if device_type == "forearm" else "above elbow"
            print(f"  {device_type.upper()}: {device.bluetoothAddress()} ({position})")
    
    print("="*80)
    
    # Create header for real-time display
    header = ""
    for device, device_type in active_devices:
        header += f"{device_type.upper()} ({device.bluetoothAddress()[-8:]})"
        header += " " * (50 - len(header) % 50)
    print(header)
    
    startTime = movelladot_pc_sdk.XsTimeStamp_nowMs()
    
    while movelladot_pc_sdk.XsTimeStamp_nowMs() - startTime <= recording_time * 2000:
        if XdpcHandler.packetsAvailable():
            display_line = ""
            
            for device, device_type in active_devices:
                packet = XdpcHandler.getNextPacket(device.bluetoothAddress())
                if packet.containsOrientation():
                    quat = packet.orientationQuaternion()
                    quat_str = f"W:{quat[0]:6.3f} X:{quat[1]:6.3f} Y:{quat[2]:6.3f} Z:{quat[3]:6.3f}"
                    display_line += quat_str + " | "
                else:
                    display_line += " " * 40 + " | "
            
            print(f"{display_line}\r", end="", flush=True)
    
    print("\n" + "="*80)
    
    # Reset orientations and cleanup
    print("\nResetting orientations and cleaning up...")
    for device, device_type in active_devices:
        print(f"Resetting {device_type} tracker orientation: ", end="", flush=True)
        if device.resetOrientation(movelladot_pc_sdk.XRM_DefaultAlignment):
            print("OK")
        else:
            print(f"NOK: {device.lastResultText()}")
        
        print(f"Stopping {device_type} measurement: ", end="", flush=True)
        if device.stopMeasurement():
            print("OK")
        else:
            print("Failed")
            
        print(f"Disabling {device_type} logging: ", end="", flush=True)
        if device.disableLogging():
            print("OK")
        else:
            print("Failed")
    
    XdpcHandler.cleanup()
    
    print("\n" + "="*50)
    print("RECORDING COMPLETE!")
    print("="*50)
    if num_trackers == 1:
        print("Generated files:")
        print(f"  - logfile_forearm_*.csv")
    else:
        print("Generated files:")
        print(f"  - logfile_forearm_*.csv")
        print(f"  - logfile_upper_arm_*.csv")
    print("\nUse these files for motion analysis and visualization!")
    print("="*50)