import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
from matplotlib.animation import FuncAnimation

folder = 'datalog/'

# Print the files inside the specified folder
print(f"Files inside the folder '{folder}':")
for filename in os.listdir(folder):
    print(filename)

def smooth_data(y, window_size):
    window = np.ones(int(window_size)) / float(window_size)
    return np.convolve(y, window, 'same')

def plot_data(axs, file_list=None, column_indexes=['0'], folder='./datalog', window_size=1, dose_rate=0.32):
    if file_list is None:
        existing_files = os.listdir(folder)
        existing_files = [file for file in existing_files if file.startswith('acq') and file.endswith('.csv')]
        existing_numbers = [int(file[3:-4]) for file in existing_files]
        if existing_numbers:
            max_number = max(existing_numbers)
        else:
            max_number = 0

        # Create a new file with an incremental name
        file_list = [f'acq{max_number:04d}.csv']
        # print(file_list)

    for file in file_list:
        try:
            file_path = os.path.join(folder, file)
            # print(f"Trying to read file: {file_path}")  # Debug print statement
            df = pd.read_csv(file_path, comment='#')
            for index in column_indexes:
                time_col = 'Time' + str(index)
                voltage_col = 'Voltage' + str(index)
                if time_col in df.columns and voltage_col in df.columns:
                    axs[0].plot(df[time_col] * dose_rate, df[voltage_col], label=file + ": Sensor " + str(index),marker='')

                    # Smooth the voltage data
                    smoothed_voltage = smooth_data(df[voltage_col], window_size)
                    # smoothed_voltage = df[voltage_col]

                    # Calculate the derivative of the smoothed voltage with respect to time
                    voltage_derivative = np.gradient(smoothed_voltage, df[time_col] * dose_rate) * 1000

                    axs[1].plot(df[time_col] * dose_rate, voltage_derivative, label=file + ": Derivative of sensor " + str(index),marker='')
                else:
                    print(f"Columns {time_col} and/or {voltage_col} not found in file {file}")
        except FileNotFoundError:
            print(f"File {file} not found at path {file_path}")
        except Exception as e:
            print(f"An error occurred while reading {file_path}: {e}")

    axs[0].set_xlabel('Time (s)' if dose_rate == 1 else 'Dose (Gy)')
    axs[0].set_ylabel('Voltage (V)')
    axs[0].legend()
    axs[0].grid()

    axs[1].set_xlabel('Time (s)' if dose_rate == 1 else 'Dose (Gy)')
    axs[1].set_ylabel('Derivative of Voltage (mV/s)' if dose_rate == 1 else 'Sensitivity (mV/Gy)')
    axs[1].legend()
    axs[1].grid()

    # Maximize the plot window
    manager = plt.get_current_fig_manager()
    manager.window.resize(720, 820)


## Beam Sweep from 15 mA to 40 mA:
# files = ['inl_s16_45kv15ma_0vms_0_cleaned.csv','inl_s16_45kv20ma_0vms_0_cleaned.csv','inl_s16_45kv25ma_0vms_0_cleaned.csv','inl_s16_45kv30ma_0vms_0_cleaned.csv','inl_s16_45kv35ma_0vms_0_cleaned.csv','inl_s16_45kv40ma_0vms_0_cleaned.csv' ]
# columns = ['0']

# Feedback Enabled
# files = ['inl_s12_linear_1.csv']
# columns = ['1']

## Comparison between samples (First Measurement)
# files = ['inl_s02_45kv20ma_0vms_1_cleaned.csv','inl_s03_45kv20ma_0vms_1_cleaned.csv','inl_s12_45kv20ma_0vms_1_cleaned.csv','inl_s16_45kv20ma_0vms_1_cleaned.csv','inl_s18_45kv20ma_0vms_1_cleaned.csv']
# columns = ['0']

## Sample without Globtop
# files = ['inl_s14_45kv20ma_0vms_2.csv']
# columns = ['0']

# files = ['cepon_s03_06mv_-9vms_cleaned.csv','cepon_s03_06mv_0vms_cleaned.csv','cepon_s03_06mv_9vms_cleaned.csv']
# columns = ['0']

# columns = ['0','1','2','3','4','5','6']
# columns = ['0','1','2','3','6']
# files = ['inl_s03_45kv20ma_0vms_1_cleaned.csv','inl_s02_45kv20ma_0vms_2_cleaned.csv']
# columns = ['0']

# plot_data(files, columns,window_size=1,dose_rate=0.32)
# columns = ['0']
# plot_data(None,columns)

# files = [
    # 'acq0001.csv',
    #         'acq0002.csv',
    #         'acq0003.csv',
    #         'acq0004.csv',
            #   'acq0005.csv',
            #   'acq0006.csv',
            #   'acq0007.csv',
            #   'acq0008.csv',
            #   'acq0009.csv',
            #   'acq0010.csv',
            #   'acq0011.csv',
            #   'acq0012.csv',
            #   'acq0013.csv',
            #   'acq0014.csv',
            #   'acq0015.csv',
            #   'acq0016.csv',

    #         ]

# files = [
            # 'acq0001_clipped.csv',
            #   'acq0002_clipped.csv',
            #   'acq0003_clipped.csv',
            #   'acq0004_clipped.csv',
            #   'acq0005_clipped.csv',
#             'acq0006_clipped.csv',
#             'acq0007_clipped.csv',
#             'acq0008_clipped.csv',
#             'acq0009_clipped.csv',
#             'acq0010_clipped.csv',
#             'acq0011_clipped.csv',
#             'acq0012_clipped.csv',
#             'acq0013_clipped.csv',
#             'acq0014_clipped.csv',
#             'acq0015_clipped.csv',
#             'acq0016_clipped.csv',
#             'acq0017_clipped.csv',
#             'acq0018_clipped.csv',
# ]
# files = [
            # 'session_1.csv',
            # 'session_13.csv',
            # 'session_14_anneal.csv',
            # 'session_15_anneal.csv',
            # 'session_16_anneal.csv',
            # 'session_17_anneal.csv'
# ]

# files = [
#             'acq0002.csv',
#             'acq0003.csv',
#             'acq0004.csv',
#             'acq0005.csv',
#             'acq0006.csv',
#             'acq0007.csv',
#             'acq0008.csv',
#             'acq0009.csv',
#             'acq0010.csv'
# ]

# files = ['svfg0001.csv',
#             'svfg0002.csv',
#             'svfg0003.csv',
#             'svfg0004.csv',
#             'svfg0005.csv',
#             'svfg0006.csv',
#             'svfg0007.csv',
#             'svfg0008.csv',
#             'svfg0009.csv',
#             'svfg0010.csv',
#             'svfg0011.csv',
#             'svfg0012.csv',
#             'svfg0013.csv'
# ]
# files = [
    # 'vref1v6_corrected_clipped.csv',
    # 'vref1v8_corrected_clipped.csv',
    # 'vref2v0_corrected_clipped.csv',
    # 'vref2v2_corrected_clipped.csv',
    # 'vref2v4_corrected_clipped.csv',
    # 'vref2v6_corrected_clipped.csv',
    # 'vref2v8_corrected_clipped.csv',
    # 'vref3v0_corrected_clipped.csv',
# ]
# files = [
    # 'vref1v6_corrected_clipped.csv',
    # 'undersampled_vref1v8_corrected_clipped.csv',
    # 'undersampled_vref2v0_corrected_clipped.csv',
    # 'undersampled_vref2v2_corrected_clipped.csv',
    # 'undersampled_vref2v4_corrected_clipped.csv',
    # 'undersampled_vref2v6_corrected_clipped.csv',
    # 'vref2v8_corrected_clipped.csv',
    # 'vref3v0_corrected_clipped.csv',
# ]
# files = [
#             '200sps_saturated.csv']
# files = [
#             'cepon_1_cleaned.csv',
            #   'cepon_2_cleaned.csv',
            #   'cepon_3_cleaned.csv',
#             #   'cepon_4_cleaned.csv',
#             # 'cepon_2_normalized.csv',
#             # 'cepon_3_normalized.csv',
#             # 'cepon_s03_06mv_0vms_cleaned.csv',
#             # 'cepon_s03_06mv_9vms_cleaned.csv',
#             # 'cepon_s03_06mv_-9vms_cleaned.csv',
#             # 'cepon_s03_06mv_9vms_normalized.csv',
#             'cepon_s03_06mv_-9vms_normalized.csv',
            #   ]

# files = [
#             'acq0002.csv',
#             'acq0003.csv',
#             'acq0004.csv',
#             'acq0005.csv',
#             'acq0006.csv',
#             'acq0007.csv',
#             'acq0008.csv',
#             'acq0009.csv',
#             'acq0010.csv']

# files = ['acq0001.csv',
#             'acq0002.csv',
#             'acq0003.csv',
#             'acq0004.csv',]

# files = None
# columns = ['0']
# columns = ['1']
columns = ['1']
# columns = ['6']
window_size = 1
# dose_rate = 0.06667 ## dose rate cepon
# dose_rate = 0.32 ## estimated dose rate XRD 20 mA
dose_rate = 0.32 ## estimated dose rate XRD 40 mA
# dose_rate = 1 ## time

fig, axs = plt.subplots(2)  # Create a figure and a set of subplots

def refresh(event=None):
    for ax in axs:
        ax.clear()
    plot_data(axs, None, columns, folder, window_size, dose_rate)
    plt.draw()  # Redraw the figure to update the plots

# Set up the animation to refresh every 2 seconds
ani = FuncAnimation(fig, refresh, interval=500)

plot_data(axs, None, columns, folder, window_size, dose_rate)
plt.show()