# You can use this file to plot the loged sensor data
# Note that you need to modify/adapt it to your own files
# Feel free to make any modifications/additions here

import matplotlib.pyplot as plt
from utilities import FileReader

def plot_errors(filename):
    
    headers, values = FileReader(filename).read_file()
    time_list = []
    first_stamp = values[0][-1]
    for val in values:
        time_list.append(val[-1])

    import os
    base_name = os.path.basename(filename)
    if "imu_content" in filename:
        # Plot acc_x and acc_y in the top subplot
        fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, figsize=(8, 6))
        ax1.plot(time_list, [lin[0] for lin in values], label="acc_x linear")
        ax1.plot(time_list, [lin[1] for lin in values], label="acc_y linear")
        ax1.set_ylabel("Acceleration (m/s^2)")
        ax1.set_title(f"{base_name}")
        ax1.legend()
        ax1.grid()

        # Plot angular_z in the bottom subplot
        ax2.plot(time_list, [lin[2] for lin in values], label="angular_z linear", color='g')
        ax2.set_xlabel("Timestamp (nanoseconds)")
        ax2.set_ylabel("Angular Velocity (rad/s)")
        ax2.legend()
        ax2.grid()

        plt.tight_layout()
        plt.show()
    elif "odom_content" in filename:
        # Plot x and y in the top subplot, th in the bottom
        fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, figsize=(8, 6))
        ax1.plot(time_list, [lin[0] for lin in values], label="x linear")
        ax1.plot(time_list, [lin[1] for lin in values], label="y linear")
        ax1.set_ylabel("Position (m)")
        ax1.set_title(f"{base_name}")
        ax1.legend()
        ax1.grid()

        # Plot th in the bottom subplot
        ax2.plot(time_list, [lin[2] for lin in values], label="th linear", color='g')
        ax2.set_xlabel("Timestamp (nanoseconds)")
        ax2.set_ylabel("Yaw (rad)")
        ax2.legend()
        ax2.grid()

        plt.tight_layout()
        plt.show()
    else:
        # Default: plot all columns except the last (timestamp)
        for i in range(0, len(headers) - 1):
            plt.plot(time_list, [lin[i] for lin in values], label=headers[i] + " linear")
        plt.legend()
        plt.grid()
        plt.show()
    
import argparse

if __name__=="__main__":

    parser = argparse.ArgumentParser(description='Process some files.')
    parser.add_argument('--files', nargs='+', required=True, help='List of files to process')
    
    args = parser.parse_args()
    
    print("plotting the files", args.files)

    filenames=args.files
    for filename in filenames:
        plot_errors(filename)
