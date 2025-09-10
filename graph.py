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
    """Create a 3D plot of quaternion X vs Y vs Z"""
    
    # Load the data
    df = load_movella_csv(csv_filename)
    
    print(f"Loaded {len(df)} data points")
    
    # Create the 3D plot
    fig = plt.figure(figsize=(12, 10))
    ax = fig.add_subplot(111, projection='3d')
    
    # Create color map based on time progression
    colors = plt.cm.viridis(np.linspace(0, 1, len(df)))
    
    # Plot quaternion X, Y, Z
    scatter = ax.scatter(df['Quat_X'], df['Quat_Y'], df['Quat_Z'], 
                        c=colors, s=30, alpha=0.8, edgecolors='black', linewidth=0.5)
    
    # Mark start and end points
    ax.scatter(df['Quat_X'].iloc[0], df['Quat_Y'].iloc[0], df['Quat_Z'].iloc[0], 
               color='green', s=100, marker='^', label='Start', edgecolors='darkgreen', linewidth=2)
    ax.scatter(df['Quat_X'].iloc[-1], df['Quat_Y'].iloc[-1], df['Quat_Z'].iloc[-1], 
               color='red', s=100, marker='v', label='End', edgecolors='darkred', linewidth=2)
    
    # Customize the plot
    ax.set_xlabel('Quaternion X', fontsize=12, labelpad=10)
    ax.set_ylabel('Quaternion Y', fontsize=12, labelpad=10)
    ax.set_zlabel('Quaternion Z', fontsize=12, labelpad=10)
    ax.set_title('Movella DOT: Quaternion 3D Space (X vs Y vs Z)\n(Color represents time progression)', 
                fontsize=14, fontweight='bold', pad=20)
    
    # Add colorbar
    cbar = plt.colorbar(scatter, ax=ax, shrink=0.8, aspect=20)
    cbar.set_label('Time Progression', fontsize=12)
    
    # Add legend
    ax.legend(loc='upper right', fontsize=10)
    
    # Add grid
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()
    
    # Print some statistics
    print(f"\nQuaternion Statistics:")
    print(f"Quat_X: {df['Quat_X'].min():.4f} to {df['Quat_X'].max():.4f}")
    print(f"Quat_Y: {df['Quat_Y'].min():.4f} to {df['Quat_Y'].max():.4f}")
    print(f"Quat_Z: {df['Quat_Z'].min():.4f} to {df['Quat_Z'].max():.4f}")

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