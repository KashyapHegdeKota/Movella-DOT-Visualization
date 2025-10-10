# Movella DOT Real-Time Visualization System

## 🎯 Overview

This project provides a complete GUI application for recording and visualizing arm movements in real-time using Movella DOT sensors. Perfect for biomechanics research, movement analysis, and exercise tracking.

## ✨ Key Features

- **🔴 Real-Time 3D Visualization**: See your arm movement as it happens
- **📊 Data Recording**: Save quaternion data to CSV for later analysis
- **🎬 Playback Mode**: Review recorded movements with 3D animation
- **🖥️ User-Friendly GUI**: No coding required - everything is point-and-click
- **⚡ Live Feedback**: Monitor your form and movement patterns in real-time

## 📋 Requirements

- Python 3.9
- Movella DOT sensors (2 required for arm tracking)
- Windows OS (for Movella SDK compatibility)

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/KashyapHegdeKota/Movella-DOT-Visualization.git
cd Movella-DOT-Visualization
```

### 2. Activate Virtual Environment

```powershell
.\venv39\Scripts\Activate.ps1
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## 🎮 Usage

### Quick Start

```bash
python gui_app.py
```

### Step-by-Step Workflow

1. **Setup Devices**
   - Enter number of trackers (2 for arm tracking)
   - Click "Setup Devices"
   - Wait for automatic scanning, connection, and calibration
   - Position devices in reference pose (arm straight down) during calibration

2. **Live Recording** ⭐ Recommended
   - Set recording duration (e.g., 15 seconds)
   - Click "Live Recording"
   - 3D visualization window opens
   - Perform your movement (bicep curls, arm raises, etc.)
   - Watch real-time feedback on screen
   - Data automatically saved to CSV

3. **Review & Analysis**
   - Use "Visualize" to replay recordings
   - Compare different sessions
   - Analyze movement patterns

## 📁 File Structure

```
├── gui_app.py                  # Main GUI application
├── realtime_visualizer.py      # Real-time 3D visualization engine
├── movella_dot_manager.py      # Device connection & management
├── visualize_bicep_curl.py     # Playback visualization
├── xdpchandler.py              # Movella SDK handler
├── test_realtime_viz.py        # Test script (no hardware needed)
├── requirements.txt            # Python dependencies
└── GUI_USAGE.md               # Detailed user guide
```

## 🧪 Testing Without Hardware

Test the visualization system without Movella DOT devices:

```bash
python test_realtime_viz.py
```

This runs a simulated bicep curl animation to verify your installation.

## 🎨 Visualization Details

- **Upper Arm**: Red cylinder
- **Forearm**: Green cylinder
- **Joints**: Blue spheres (shoulder, elbow, wrist)
- **Frame Rate**: ~30 FPS for smooth animation
- **Sampling Rate**: ~100 Hz for data recording

## 📊 Data Format

CSV files contain quaternion data (W, X, Y, Z format):

```csv
tracker_1_WXYZ,tracker_2_WXYZ
0.999,0.001,-0.002,0.003,0.998,0.002,0.001,-0.004
...
```

## 🔧 Troubleshooting

### NumPy Version Error

If you get `ABI version` errors:
```bash
pip uninstall numpy
pip install "numpy<2.0.0"
```

### Devices Not Found

- Ensure DOT devices are powered on
- Check Bluetooth is enabled
- Devices should be in pairing mode (blinking)

### Visualization Window Not Opening

- Check matplotlib is installed: `pip install matplotlib`
- Ensure no other application is blocking the display

## 🎓 Use Cases

- **Physical Therapy**: Monitor patient movement patterns
- **Sports Training**: Analyze athletic form in real-time
- **Biomechanics Research**: Collect and analyze movement data
- **Exercise Form**: Get immediate feedback on workout technique
- **Motion Capture**: Low-cost alternative for simple movements

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Additional body segment configurations
- Export to other formats (BVH, C3D)
- Multi-session comparison tools
- Movement quality metrics

## 📝 License

See the license headers in individual files for Movella SDK components.

## 👥 Authors

- Kashyap Hegde Kota

## 🙏 Acknowledgments

- Movella Technologies for the DOT SDK
- Matplotlib for visualization capabilities

## 📞 Support

For issues or questions:
- Open an issue on GitHub
- Check `GUI_USAGE.md` for detailed instructions
- Review `test_realtime_viz.py` for troubleshooting

---

**Happy Motion Tracking! 🎯**
