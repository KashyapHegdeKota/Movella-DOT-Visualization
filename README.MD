# Movella DOT Visualization

This repository provides a Python-based workflow for setting up Movella DOT motion trackers, recording quaternion data, and visualizing bicep curl movements. It is ideal for biomechanics research, sports science, or any scenario where you want to capture and analyze motion data from wearable sensors.

---

## Features

- **Automatic Device Setup**: Connect multiple Movella DOT trackers via Bluetooth or USB.
- **Quaternion Recording**: Collect synchronized quaternion data and save it in CSV format.
- **Bicep Curl Visualization**: Visualize movement using built-in tools and sample data.
- **Simple Workflow**: One script handles device setup, recording, and visualization.

---

## Requirements

- **Python 3.9.13** (recommended via pyenv)
- **Movella DOT PC SDK** (2023.6) installed on your system
- **Movella DOTs** (at least 2 recommended)
- **Bluetooth** or **USB** connectivity for your devices
- Windows OS (SDK wheel provided for win_amd64)

### Python Dependencies

All required Python packages are listed in `requirements.txt`.

---

## Installation

### 1. Set up Python 3.9.13 using pyenv

Ensure [pyenv](https://github.com/pyenv/pyenv) is installed on your machine. Then, install and activate Python 3.9.13:

```bash
pyenv install 3.9.13
pyenv local 3.9.13
# Or, if you're on Windows and use pyenv-win:
pyenv install 3.9.13
pyenv global 3.9.13
```

### 2. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 3. Install Movella DOT PC SDK Python wheel

Replace the path below if your SDK is installed elsewhere, then run:

```bash
pip install "C:\Program Files\Movella\DOT PC SDK 2023.6\SDK Files\Python\x64\movelladot_pc_sdk-2023.6.0-cp39-none-win_amd64.whl"
```

> **Note:** You must have the Movella DOT PC SDK installed on your system. The wheel file is typically provided by the installer.

### 4. Connect Your Devices

- Power on your Movella DOT trackers.
- Make them discoverable via Bluetooth or connect via USB.

---

## Usage

### Quick Start

Run the main script to perform all steps automatically:

```bash
python main.py
```

This will:

- Scan and connect to available Movella DOT trackers
- Record quaternion data for 10 seconds into a CSV file (named with the current timestamp)
- Visualize the recorded bicep curl data

### Step-by-Step Usage

#### 1. Device Setup

The script will prompt you for the number of devices to connect and guide you through the selection and labeling process.

#### 2. Recording Quaternions

Quaternion data from two trackers is recorded and saved as `<timestamp>_output.csv`. Example CSV format:

```csv
tracker_1_WXYZ,tracker_2_WXYZ
"0.4708,-0.2056,-0.1471,0.8452","0.2843,-0.7993,0.1256,0.5144"
...
```

#### 3. Visualization

After recording, the script will automatically generate a visualization (e.g., for bicep curls) using the recorded data.

---

## Customization

- **Recording Duration:** Change the `duration` argument in `main.py` when calling `record_quaternions_to_csv`.
- **Visualization:** Modify or extend `visualize_bicep_curl.py` for custom analysis.

---

## Troubleshooting

- **No Devices Found:** Make sure DOTs are powered on and discoverable. Check Bluetooth/USB connections.
- **SDK Not Found:** Ensure the Movella DOT PC SDK is installed and in your PATH.
- **Permission Issues:** Run the script with administrator/root privileges if needed.
- **Python Version Issues:** Ensure you're using Python 3.9.13 as required by the SDK wheel.

---

## Example Output

- **CSV Data:** See sample files such as `1757800606.4119213_output.csv`
- **GIF Visualization:** Example `bicep_curl_final.gif` generated after running the script.
- ![Demo Animation](./Figure 1 2025-09-14 00-12-22.gif)
---

## License

MIT License

---

## Contact

For questions or contributions, open an issue or reach out via GitHub.
