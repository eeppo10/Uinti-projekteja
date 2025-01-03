"""
Author: Eerikki Laitala
Email: eerikki.laitala@gmail.com

This program reads the binary file and simply visualizes the output in some nice graphs
"""
import struct
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def main():

    # Each record consists of 7 floats (3 for accelerometer, 3 for gyroscope, 1 for Time)

    record_format = '7h'  # 7 floats
    record_size = struct.calcsize(record_format)
    # Open the binary file and read the data
    with open('FILE_PATH', 'rb') as f:
        binary_data = f.read()

    # Unpack the binary data into a list of tuples
    records = []
    for i in range(0, len(binary_data), record_size):
        record = struct.unpack(record_format, binary_data[i:i + record_size])
        records.append(record)

    # Convert the data into a Pandas DataFrame
    df = pd.DataFrame(records,
                      columns=['acc_x', 'acc_y', 'acc_z', 'gyro_x', 'gyro_y',
                               'gyro_z', 'time'])
    
    # Uncompress acceleration data
    df[['acc_x', 'acc_y', 'acc_z']] = df[[
        'acc_x', 'acc_y', 'acc_z']] / 1000

    # Display the first few rows of the DataFrame
    print(df.head())

    # Plot accelerometer data
    plt.figure(figsize=(12, 6))
    plt.subplot(3, 1, 1)
    plt.plot(df.index, df['acc_x'], label='Acceleration X', color='blue')
    plt.title('Accelerometer Data')
    plt.xlabel('Sample Index')
    plt.ylabel('G')
    plt.legend()
    plt.subplot(3, 1, 2)
    plt.plot(df.index, df['acc_y'], label='Acceleration Y', color='orange')
    plt.xlabel('Sample Index')
    plt.ylabel('G')
    plt.legend()
    plt.subplot(3, 1, 3)
    plt.plot(df.index, df['acc_z'], label='Acceleration Z', color='green')
    plt.xlabel('Sample Index')
    plt.ylabel('G')
    plt.legend()

    # Plot gyroscope data
    plt.subplot(3, 1, 2)
    plt.plot(df.index, df['gyro_x'], label='Gyro X')
    plt.plot(df.index, df['gyro_y'], label='Gyro Y')
    plt.plot(df.index, df['gyro_z'], label='Gyro Z')
    plt.title('Gyroscope Data')
    plt.xlabel('Sample Index')
    plt.ylabel('Angular Velocity (deg/s)')
    plt.legend()

    plt.show()

if __name__ == "__main__":
    main()
