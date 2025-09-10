from xdpchandler import *
import os
if __name__ == "__main__":
    XdpcHandler = XdpcHandler()

    if not XdpcHandler.initialize():
        XdpcHandler.cleanup()
        exit(-1)
    
    print("Scanning for Movella DOT devices...")
    XdpcHandler.scanForDots()
    
    if len(XdpcHandler.detectedDots()) == 0:
        print("No Movella DOT device(s) found. Aborting.")
        XdpcHandler.cleanup()
        exit(-1)
    
    # Display detected devices
    detected = XdpcHandler.detectedDots()
    print(f"Found {len(detected)} device(s):")
    for i, portInfo in enumerate(detected):
        print(f"  {i}: {portInfo.bluetoothAddress()}")
    
    # Select which device to connect to (first one by default)
    device_index = 0  # Change this to select different device
    target_address = detected[device_index].bluetoothAddress()
    print(f"Attempting to connect to: {target_address}")
    
    # Connect to all devices first (as the original code does)
    XdpcHandler.connectDots()
    
    # Check if any devices connected
    if len(XdpcHandler.connectedDots()) == 0:
        print("Could not connect to any Movella DOT device(s). Aborting.")
        XdpcHandler.cleanup()
        exit(-1)
    
    # Find our target device among the connected ones
    device = None
    for connected_device in XdpcHandler.connectedDots():
        if connected_device.bluetoothAddress() == target_address:
            device = connected_device
            break
    
    if device is None:
        print(f"Target device {target_address} was not connected successfully. Aborting.")
        XdpcHandler.cleanup()
        exit(-1)
    
    print(f"Successfully connected to: {device.bluetoothAddress()}")
    
    # Disconnect all other devices to work with just one
    for connected_device in XdpcHandler.connectedDots():
        if connected_device.bluetoothAddress() != target_address:
            print(f"Disconnecting device: {connected_device.bluetoothAddress()}")
            connected_device.stopMeasurement()
            # Note: The XdpcHandler might not have a direct disconnect method
            # so we'll just stop measurement on other devices
    
    # Wait a moment for the device to be ready
    import time
    time.sleep(1)
    
    # Configure the target device
    filterProfiles = device.getAvailableFilterProfiles()
    print("Available filter profiles:")
    for f in filterProfiles:
        print(f"  {f.label()}")
    print(f"Current profile: {device.onboardFilterProfile().label()}")
    
    # Skip setting filter profile if it's already "General"
    current_profile = device.onboardFilterProfile().label()
    if current_profile != "General":
        print("Setting filter profile to General...")
        if device.setOnboardFilterProfile("General"):
            print("Successfully set profile to General")
            time.sleep(0.5)  # Wait after profile change
        else:
            print(f"Setting filter profile failed! Continuing with current profile: {current_profile}")
    else:
        print("Filter profile is already set to General")
    
    print("Setting quaternion CSV output")
    device.setLogOptions(movelladot_pc_sdk.XsLogOptions_Quaternion)
    time.sleep(0.5)
    
    logFileName = "logfile_" + device.bluetoothAddress().replace(':', '-') + ".csv"
    if(os.path.exists(logFileName)):
        os.remove(logFileName)
    print(f"Enable logging to: {logFileName}")
    if not device.enableLogging(logFileName):
        print(f"Failed to enable logging. Reason: {device.lastResultText()}")
    time.sleep(0.5)
    
    print("Putting device into measurement mode...")
    # Try multiple times with different payload modes if needed
    success = False
    payload_modes = [
        movelladot_pc_sdk.XsPayloadMode_ExtendedQuaternion,
        movelladot_pc_sdk.XsPayloadMode_CompleteQuaternion,
        movelladot_pc_sdk.XsPayloadMode_OrientationQuaternion
    ]
    
    for i, mode in enumerate(payload_modes):
        mode_name = ["ExtendedQuaternion", "CompleteQuaternion", "OrientationQuaternion"][i]
        print(f"Trying {mode_name} mode...")
        if device.startMeasurement(mode):
            print(f"Successfully started measurement with {mode_name} mode")
            success = True
            break
        else:
            print(f"Failed with {mode_name}: {device.lastResultText()}")
            time.sleep(1)  # Wait before trying next mode
    
    if not success:
        print("Could not put device into any measurement mode. Aborting.")
        XdpcHandler.cleanup()
        exit(-1)
    
    print(f"\nMain loop. Recording data for 20 seconds from device: {device.bluetoothAddress()}")
    print("-" * 80)
    print(f"{'Device Address':42} {'Quaternion Data'}")
    print(f"{device.bluetoothAddress():42}")

    orientationResetDone = False
    startTime = movelladot_pc_sdk.XsTimeStamp_nowMs()
    
    while movelladot_pc_sdk.XsTimeStamp_nowMs() - startTime <= 20000:
        if XdpcHandler.packetsAvailable():
            # Retrieve packet for our specific device
            packet = XdpcHandler.getNextPacket(device.bluetoothAddress())
            if packet.containsOrientation():
                quat = packet.orientationQuaternion()
                # quat is a numpy array with [w, x, y, z] components
                s = f"W:{quat[0]:7.4f}, X:{quat[1]:7.4f}, Y:{quat[2]:7.4f}, Z:{quat[3]:7.4f}"
                print(f"{s}\r", end="", flush=True)

    
    print("\n" + "-" * 80, end="", flush=True)

    # Reset heading to default
    print(f"\nResetting heading to default for device {device.bluetoothAddress()}: ", end="", flush=True)
    if device.resetOrientation(movelladot_pc_sdk.XRM_DefaultAlignment):
        print("OK", end="", flush=True)
    else:
        print(f"NOK: {device.lastResultText()}", end="", flush=True)
    print("\n", end="", flush=True)

    # Clean shutdown
    print("\nStopping measurement...")
    if not device.stopMeasurement():
        print("Failed to stop measurement.")
    if not device.disableLogging():
        print("Failed to disable logging.")

    XdpcHandler.cleanup()
    print("Done!")