from movella_dot_manager import setup_movella_dots, record_quaternions_to_csv
from visualize_bicep_curl import visualize_bicep_curl
import time

start_time = time.time()
# This handles everything automatically
manager = setup_movella_dots()

if manager:
    # Your code here - devices are ready to use
    print("Devices ready!")
    record_quaternions_to_csv(manager, f"{start_time}_output.csv", duration=10)
    # When done:
    visualize_bicep_curl(f"{start_time}_output.csv")
    manager.cleanup()