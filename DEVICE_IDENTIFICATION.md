# 🔦 Device Identification Feature - Complete!

## What's New

You can now easily identify which physical Movella DOT tracker corresponds to which assignment (tracker_1 or tracker_2) in the software!

## New Features

### 1. **Connected Devices Panel** 📊
After connecting devices, you'll see a detailed table showing:
- **Label**: tracker_1, tracker_2, etc.
- **Address**: Last 8 characters of Bluetooth MAC address
- **Battery**: Current battery level with color coding (green/orange/red)
- **Blink LED Button**: Click to make that specific device blink its LED

### 2. **LED Identification** 💡
- Click "Blink LED" next to any device
- The physical tracker will blink its LED light
- Watch your trackers to see which one is blinking
- Perfect for identifying which tracker is which!

### 3. **Swap Assignments** 🔄
- If you accidentally placed the trackers backwards
- Click "⇄ Swap Tracker 1 ↔ Tracker 2" button
- Instantly swaps the assignments
- No need to reconnect or recalibrate!

## How to Use

### Step 1: Setup Devices
```
1. Click "Setup Devices"
2. Wait for connection and calibration
3. Device info panel appears automatically
```

### Step 2: Identify Your Trackers

**Option A: Check which is which**
```
1. Look at the "Connected Devices" panel
2. Click "Blink LED" for tracker_1
3. Watch your trackers - one will blink
4. Note which physical tracker blinked
5. Repeat for tracker_2
```

**Option B: Swap if needed**
```
1. If tracker_1 is on your upper arm but should be on forearm
2. Click "⇄ Swap Tracker 1 ↔ Tracker 2"
3. Assignments are instantly reversed
4. Continue with recording!
```

## Visual Guide

### Device Info Panel Layout

```
┌─────────────────────────────────────────────────────┐
│ Connected Devices                                   │
├─────────────┬──────────────┬─────────┬──────────────┤
│ Label       │ Address      │ Battery │ Action       │
├─────────────┼──────────────┼─────────┼──────────────┤
│ tracker_1   │ ...A1:B2:C3 │ 85%     │ [Blink LED]  │
│ tracker_2   │ ...D4:E5:F6 │ 72%     │ [Blink LED]  │
├─────────────┴──────────────┴─────────┴──────────────┤
│         [⇄ Swap Tracker 1 ↔ Tracker 2]              │
├──────────────────────────────────────────────────────┤
│ 💡 Click 'Blink LED' to identify which physical     │
│    tracker is which. Use 'Swap' if assignments      │
│    are reversed.                                     │
└──────────────────────────────────────────────────────┘
```

## Typical Workflow

### Recommended Setup Process

1. **Initial Connection**
   - Click "Setup Devices"
   - Devices connect as tracker_1 and tracker_2 (arbitrary order)

2. **Identify Physical Trackers**
   - Click "Blink LED" for tracker_1
   - Note which physical device blinks
   - This tells you which tracker is tracker_1

3. **Place Trackers Correctly**
   - Option A: Place them according to the current assignment
     - Put the blinking tracker (tracker_1) on forearm
     - Put the other tracker (tracker_2) on upper arm
   
   - Option B: Swap the assignment if convenient
     - Click "Swap" button
     - Now tracker_1 is on the device you want

4. **Record**
   - Proceed with normal or live recording
   - You know exactly which tracker is where!

## Battery Monitoring

The device panel also shows battery levels:
- **Green** (>50%): Good to go! ✅
- **Orange** (20-50%): Consider charging soon ⚠️
- **Red** (<20%): Charge before recording! 🔋

## Technical Details

### LED Blink Function
- Uses Movella SDK's `device.identify()` method
- Causes the device LED to blink in a distinctive pattern
- Runs in background thread (non-blocking)
- Safe to call multiple times

### Swap Function
- Swaps labels in `manager.device_info` dictionary
- Swaps order in `manager.connected_devices` list
- Updates display immediately
- Does NOT require reconnection or recalibration
- Preserves all device states and calibration

### Device Information
- **Address**: Bluetooth MAC address (unique identifier)
- **Label**: Software assignment (tracker_1, tracker_2, etc.)
- **Battery**: Real-time battery level from device

## Use Cases

### Scenario 1: First-Time Setup
"I don't know which tracker is which"
→ Use "Blink LED" to identify each one

### Scenario 2: Wrong Assignment
"I put tracker_1 on my upper arm by mistake"
→ Click "Swap" button to fix instantly

### Scenario 3: Multiple Sessions
"I want to use the same tracker on the same limb every time"
→ Use "Blink LED" to verify correct placement before each session

### Scenario 4: Battery Check
"I want to make sure I have enough battery"
→ Check the battery column before recording

## Tips

1. **Label Your Physical Trackers**: Put a small sticker with "F" (forearm) or "U" (upper arm) on each tracker
2. **Consistent Placement**: Always use the same physical tracker on the same body part for consistency
3. **Check Battery First**: Verify >50% battery before important recordings
4. **Use Blink Before Each Session**: Quick verification prevents mistakes

## Benefits

✅ **No More Guessing**: Know exactly which tracker is which
✅ **Quick Fixes**: Swap assignments without reconnecting
✅ **Battery Awareness**: Avoid mid-recording power loss
✅ **Professional Setup**: Clear device management for research

## Files Modified

- `gui_app.py`: Added device info panel, blink functionality, and swap feature

## What You Get

The GUI now shows:
1. Complete device information table
2. Individual LED blink controls
3. One-click swap functionality
4. Real-time battery monitoring
5. Visual feedback for all actions

---

**Now you'll never be confused about which tracker is which! 🎯**
