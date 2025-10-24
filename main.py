from movella_dot_manager import setup_movella_dots, record_quaternions_to_csv
import time

start_time = time.time()
# This handles everything automatically
manager = setup_movella_dots()

if manager:
    # Your code here - devices are ready to use
    print("Devices ready!")
    record_quaternions_to_csv(manager, "quaternion_data.csv")
    # When done:
    manager.cleanup()