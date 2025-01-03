"""
Author: Eerikki Laitala

This program reads the binary file that my sensor setup outputs
"""
import struct

def main():

    # Define the binary file path (replace with the actual path to your file)
    binary_file_path = "FILE_PATH"

    # Open the binary file for reading
    with open(binary_file_path, "rb") as file:
        data = file.read()

    # Define the format for 7 int16 values (3 for accelerometer, 3 for gyroscope, 1 for Time)
    # 'h' is the format character for 16-bit signed integers
    sample_format = "7h"
    sample_size = struct.calcsize(
        sample_format)  # 6 bytes (2 bytes per int16 * 3)

    # Iterate through the data and unpack each sample
    for i in range(0, len(data), sample_size):
        # Extract the current sample (6 bytes)
        sample = data[i:i + sample_size]

        # Unpack the 3 int16 values (X, Y, Z)
        ax, ay, az , gx, gy, gz, t = struct.unpack(sample_format, sample)

        # Print the unpacked values
        print(f"Accel X: {ax}, Y: {ay}, Z: {az}, Gyro: {gx}, {gy}, {gz} t: {t}")


if __name__ == "__main__":
    main()
