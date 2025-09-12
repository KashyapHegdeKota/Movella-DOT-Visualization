import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def load_movella_csv(filename):
    """Load Movella DOT CSV file and extract the data properly"""
    # Read the file to find where the actual data starts
    with open(filename, 'r') as f:
        lines = f.readlines()
    
    # Find the line with column headers (contains "SampleTimeFine")
    header_line_idx = None
    for i, line in enumerate(lines):
        if 'SampleTimeFine' in line:
            header_line_idx = i
            break
    
    if header_line_idx is None:
        raise ValueError("Could not find data header in CSV file")
    
    # Read the CSV starting from the header line
    df = pd.read_csv(filename, skiprows=header_line_idx)
    return df

def plot_quaternion_3d(csv_filename):
    """Create a 3D plot of quaternion X vs Y vs Z showing bicep curl motion"""
    
    # Load the data
    df = load_movella_csv(csv_filename)
    
    print(f"Loaded {len(df)} data points from bicep curl exercise")
    
    # Create the 3D plot
    fig = plt.figure(figsize=(12, 10))
    ax = fig.add_subplot(111, projection='3d')
    
    # Plot quaternion trajectory as a connected line to show the motion
    ax.plot(df['Quat_X'], df['Quat_Y'], df['Quat_Z'], 
            color='blue', linewidth=2, alpha=0.8, label='Bicep Curl Motion')
    
    # Plot all points
    ax.scatter(df['Quat_X'], df['Quat_Y'], df['Quat_Z'], 
               c='blue', s=20, alpha=0.6)
    
    # Mark start and end positions clearly
    ax.scatter(df['Quat_X'].iloc[0], df['Quat_Y'].iloc[0], df['Quat_Z'].iloc[0], 
               color='green', s=150, marker='o', label='Starting Position', 
               edgecolors='darkgreen', linewidth=3)
    ax.scatter(df['Quat_X'].iloc[-1], df['Quat_Y'].iloc[-1], df['Quat_Z'].iloc[-1], 
               color='red', s=150, marker='s', label='Ending Position', 
               edgecolors='darkred', linewidth=3)
    
    # Customize the plot for bicep curl analysis
    ax.set_xlabel('Quaternion X', fontsize=12, labelpad=10)
    ax.set_ylabel('Quaternion Y', fontsize=12, labelpad=10)
    ax.set_zlabel('Quaternion Z', fontsize=12, labelpad=10)
    ax.set_title('Bicep Curl Exercise: Lower Arm Rotation Path\n(Quaternion Space Trajectory)', 
                fontsize=14, fontweight='bold', pad=20)
    
    # Add legend
    ax.legend(loc='upper right', fontsize=11)
    
    # Add grid for better visualization
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()
    
    # Print exercise analysis
    print(f"\nBicep Curl Analysis:")
    print(f"Total range of motion in quaternion space:")
    print(f"  X-axis: {df['Quat_X'].max() - df['Quat_X'].min():.4f}")
    print(f"  Y-axis: {df['Quat_Y'].max() - df['Quat_Y'].min():.4f}")
    print(f"  Z-axis: {df['Quat_Z'].max() - df['Quat_Z'].min():.4f}")
    print(f"Exercise duration: ~10 seconds")
    print(f"Data points captured: {len(df)}")
    
    # Check if motion returns close to starting position
    start_pos = np.array([df['Quat_X'].iloc[0], df['Quat_Y'].iloc[0], df['Quat_Z'].iloc[0]])
    end_pos = np.array([df['Quat_X'].iloc[-1], df['Quat_Y'].iloc[-1], df['Quat_Z'].iloc[-1]])
    
    # Check for NaN values
    if np.isnan(start_pos).any() or np.isnan(end_pos).any():
        print("⚠ Warning: Some quaternion values contain NaN - check data quality")
        # Filter out NaN values for analysis
        valid_data = df.dropna(subset=['Quat_X', 'Quat_Y', 'Quat_Z'])
        if len(valid_data) > 0:
            start_pos = np.array([valid_data['Quat_X'].iloc[0], valid_data['Quat_Y'].iloc[0], valid_data['Quat_Z'].iloc[0]])
            end_pos = np.array([valid_data['Quat_X'].iloc[-1], valid_data['Quat_Y'].iloc[-1], valid_data['Quat_Z'].iloc[-1]])
            distance = np.linalg.norm(end_pos - start_pos)
            print(f"Distance between start/end positions (cleaned data): {distance:.4f}")
        else:
            print("No valid data points found")
            return
    else:
        distance = np.linalg.norm(end_pos - start_pos)
        print(f"Distance between start/end positions: {distance:.4f}")
    
    if distance < 0.2:
        print("✓ Good form: Arm returned close to starting position")
    else:
        print(f"⚠ Note: Arm position differs from start by {distance:.4f} units")
        print("  This is normal for multiple reps - you did several bicep curls!")

# Example usage
if __name__ == "__main__":
    # Replace with your actual CSV filename
    csv_filename = "logfile_D4-22-CD-00-8C-B7.csv"

    try:
        plot_quaternion_3d(csv_filename)
        print("Quaternion 3D plot created successfully!")
    except FileNotFoundError:
        print(f"Error: Could not find file '{csv_filename}'")
        print("Make sure the CSV file is in the same directory as this script.")
    except Exception as e:
        print(f"Error creating plot: {e}")