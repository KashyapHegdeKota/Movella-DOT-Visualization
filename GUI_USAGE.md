# Movella DOT GUI Application

## Quick Start

Run the GUI application:
```bash
python gui_app.py
```

## Features

### 1. Device Setup
- **Number of trackers**: Select how many DOT trackers you want to use (1-10)
- **Setup Devices**: Click to automatically:
  - Initialize the SDK
  - Scan for available devices
  - Auto-select and connect to devices
  - Calibrate all devices
  - Start measurement mode
  - Display device information panel

The status window will show real-time progress of each step.

#### Device Information Panel 🆕
After setup, you'll see a panel showing:
- **Label**: tracker_1, tracker_2, etc.
- **Address**: Last 8 characters of MAC address
- **Battery**: Current battery level (color-coded)
- **Blink LED**: Click to make that tracker's LED blink for identification
- **Swap Button**: Swap tracker_1 ↔ tracker_2 assignments if needed

**How to identify trackers:**
1. Click "Blink LED" next to tracker_1
2. Watch your physical trackers - one will blink
3. That's your tracker_1! Note which body part it's on
4. If it's backwards, click "⇄ Swap Tracker 1 ↔ Tracker 2"

### 2. Recording Controls
- **Recording Duration**: Set how long you want to record (in seconds)
- **Output file**: Specify the CSV filename for saving data
- **Start Recording**: Record data without visualization
  - Requires exactly 2 devices for bicep curl recording
  - Data is saved in real-time
  - Progress updates shown in status window
- **Live Recording**: 🎥 **NEW!** Record with real-time 3D visualization
  - Opens a separate window showing your arm movement in real-time
  - See your bicep curls as you perform them!
  - Data is recorded simultaneously
  - Perfect for immediate feedback and movement analysis

### 3. Visualization
- **CSV File**: Browse for a previously recorded CSV file
- **Visualize**: Play back the 3D animation of the recorded movement
  - Shows arm segments (upper arm and forearm)
  - Interactive 3D view

### 4. Disconnect Devices
- Click "Disconnect Devices" to safely stop measurement and disconnect
- Automatically called when quitting the application

## Workflow

### Option A: Live Recording (Recommended!)

1. **Setup**: 
   - Enter number of trackers (2 for bicep curl)
   - Click "Setup Devices"
   - Wait for calibration (position devices in reference pose)

2. **Live Record**:
   - Set recording duration
   - Click "Live Recording"
   - A 3D visualization window opens
   - Perform your movement (e.g., bicep curls)
   - Watch your arm move in real-time on screen!
   - Recording stops automatically or click "Stop Live Recording"

3. **Review**:
   - Data is automatically saved
   - Can replay later using "Visualize" button

### Option B: Record Then Visualize

1. **Setup**: (same as above)

2. **Record**:
   - Set recording duration
   - Click "Start Recording"
   - Perform your movement
   - Recording stops automatically

3. **Visualize**:
   - CSV file is auto-filled after recording
   - Click "Visualize" to see the animation

## Status Window

The status window shows:
- SDK initialization status
- Device scanning results
- Connection progress
- Calibration status
- Recording progress (with timer for live recording)
- Any errors or warnings

## Real-Time Visualization Features

- **Live 3D Rendering**: See your arm movement in real-time
- **Smooth Animation**: Updates at ~30 FPS for fluid motion
- **Thread-Safe**: Recording and visualization run independently
- **Auto-Calibration**: Uses your starting position as reference
- **Color Coded**: Upper arm (red), Forearm (green), Joints (blue)

## Notes

- The GUI automatically handles device calibration after a 2-second delay
- Recording requires exactly 2 devices
- Live recording opens a new matplotlib window - don't close it manually during recording
- All operations run in background threads to keep the GUI responsive
- Real-time visualization requires matplotlib with animation support

## Tips for Best Results

1. **Calibration**: Hold devices steady in your reference pose (arm straight down)
2. **Live Recording**: Position yourself so you can see both the screen and your arm
3. **Smooth Movements**: Perform slow, controlled movements for best visualization
4. **Recording Duration**: Start with 10-15 seconds, increase as needed
