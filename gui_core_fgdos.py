from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo


import collections
import numpy as np
from PyQt5.QtCore import QTimer, QCoreApplication
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


def populate_serial_ports(self):
    if self.serial_port.isOpen():
        self.statusbar.showMessage("Connected to " + self.serial_port.portName())
    else:
        self.statusbar.showMessage("Disconnected")

    # Clear the combo box
    self.comboBoxSerialPort.clear()

    # Get available serial ports
    serial_ports = QSerialPortInfo.availablePorts()

    # Populate combo box with serial port names
    for port in serial_ports:
        self.comboBoxSerialPort.addItem(port.portName())


def connect_to_serial_port(self):
    # Close any previously open port

    if self.serial_port.isOpen():
        self.serial_port.close()

    # Get the selected serial port name
    port_name = self.comboBoxSerialPort.currentText()

    # Attempt to open the selected serial port
    self.serial_port.setPortName(port_name)

    # Set the baud rate (for example, 9600)
    self.serial_port.setBaudRate(QSerialPort.Baud115200)
    self.data_buffer_size = int(
        int(self.bufferSize.text()) * 1000 / int(self.sampleTime.text())
    )
    self.data_buffer = collections.deque(
        maxlen=self.data_buffer_size
    )  # Buffer to store last 100 values

    if self.serial_port.open(QSerialPort.ReadWrite):
        self.serial_port.clear(QSerialPort.AllDirections)
        self.statusbar.showMessage("Connected to " + port_name)
        # self.send_message(b"\n")

        # Add further actions here, such as reading data from the port
    else:
        self.statusbar.showMessage(f"Failed to connect to " + port_name)


from PyQt5.QtCore import QTimer

def clear_message(self):
    self.statusbar.clearMessage()  # Clear the status bar message
    self.timer.stop()  # Stop the timer



# def set_plot(self):
#     cuttoff_frequency = 20  # Hz
#     normalized_cuttoff_frequency = cuttoff_frequency / (int(self.sampleTime.text())* 1000 / 2)
#     self.rt_filter = RealTimeFilter('FIR', order=6, cutoff=normalized_cuttoff_frequency)
#     self.statusbar.showMessage("Set Plot!")
#     self.data_buffer_size = int(self.bufferSize.text())
#     self.data_buffer = collections.deque(maxlen=self.data_buffer_size)  # Buffer to store last 100 values
#     sampleTime_period = int(self.sampleTime.text())
#     if self.radioADC.isChecked():
#         self.x_values = collections.deque(maxlen=self.data_buffer_size)
#     self.timerPlot.timeout.connect(self.update_plot)
#     self.fgdos.reset_timestamp_offset()
#     self.timerPlot.start(sampleTime_period)

def set_plot(self):
    self.data_buffer_size = int(self.bufferSize.text())
    self.data_buffer = collections.deque(maxlen=self.data_buffer_size) 
    self.x_values = collections.deque(maxlen=self.data_buffer_size)
    sampleTime_period = int(self.sampleTime.text())
    self.timerPlot.timeout.connect(self.update_plot)
    self.fgdos.reset_timestamp_offset()
    self.timerPlot.start(sampleTime_period)

def update_adc_measurement(self):
    if self.fgdos.get_status() and not self.measurement_running and self.progressBarDatalog.value() == 0:
        self.measurement_running = True
        status, data = self.fgdos.get_measurement_voltage()
        timestamp = self.fgdos.get_timestamp() / 1e6
        self.measurement_running = False
        return status, data, timestamp
    else:
        return True,None,None
    
def update_plot(self, status=None, data=None, timestamp=None):
    #if status is None and data is None and timestamp is None:
    # if self.progressBarDatalog.value() > 0:
    #     self.unset_plot()
        
    status, data, timestamp = self.update_adc_measurement()
    if not status:
        try:
            self.data_buffer.append(data)
            self.x_values.append(timestamp)
            self.line.set_data(self.x_values, self.data_buffer)
            self.ax.relim()
            self.ax.autoscale_view()
            ymax = max(self.data_buffer)
            ymin =  min(self.data_buffer)
            self.ax.set_ylim([ymin / 1.05 , ymax * 1.05])
            self.canvas.draw()
            self.app.processEvents()
        except ValueError:
            print("Invalid data:", data)
            print(type(data))
    # else:
    #     print("No data received.")
    
            



def unset_plot(self):
    self.timerPlot.stop()
    self.data_buffer.clear()
    if self.radioADC.isChecked():
        self.x_values_smu  = None
    self.statusbar.showMessage("Unset Plot!")
    self.measurement_running = False




# def update_plot(self):
#     # Read data from serial port and update the plot
#     if self.radioADC.isChecked():
#         if self.fgdos.get_status() and not self.measurement_running:
#             self.measurement_running = True 
#             status, data = self.fgdos.get_measurement_voltage()
#             timestamp = self.fgdos.get_timestamp() / 1e6            ## Get the timestamp in miliseconds
#             if not status:
#                 try:
#                     #data = self.rt_filter.update(data)
#                     print("Measurement: {:.3f}".format(round(data, 3)), "Timestamp: ", timestamp)
#                     self.data_buffer.append(data)
#                     self.x_values.append(timestamp)
#                     # Update plot data
#                     self.line.set_data(self.x_values, self.data_buffer)
                    
#                     # Update plot limits if necessary
#                     self.ax.relim()
#                     self.ax.autoscale_view()
#                     ymax = max(self.data_buffer)
#                     ymin =  min(self.data_buffer)
#                     self.ax.set_ylim([ymin / 1.05 , ymax * 1.05])
#                     # Redraw canvas
#                     self.canvas.draw()
#                     self.app.processEvents()

#                 except ValueError:
#                     print("Invalid data:", data)
#                     print(type(data))
#             else:
#                 print("No data received.")
#             self.measurement_running = False
#         else:
#             self.statusbar.showMessage("RP2040 Daemon not connected.")




def save_settings(self):
    with open("settings.cfg", "w") as f:
        f.write(f"sampleTime={self.sampleTime.text()}\n")
        f.write(f"chargeVoltage={round(self.spinChargeVoltage.value(),2)}\n")
        f.write(f"dischargeVoltage={round(self.spinDischargeVoltage.value(),2)}\n")
        f.write(f"sensorIndex={self.spinSensor.value()}\n")
        f.write(f"bufferSize={self.bufferSize.text()}\n")
        f.write(f"metalShieldBias={self.spinMetalShieldBias.value()}\n")
        f.write(f"datalogSensor0={self.listSensorsToDatalog.item(0).isSelected()}\n")
        f.write(f"datalogSensor1={self.listSensorsToDatalog.item(1).isSelected()}\n")
        f.write(f"datalogSensor2={self.listSensorsToDatalog.item(2).isSelected()}\n")
        f.write(f"datalogSensor3={self.listSensorsToDatalog.item(3).isSelected()}\n")
        f.write(f"datalogSensor4={self.listSensorsToDatalog.item(4).isSelected()}\n")
        f.write(f"datalogSensor5={self.listSensorsToDatalog.item(5).isSelected()}\n")
        f.write(f"datalogSensor6={self.listSensorsToDatalog.item(6).isSelected()}\n")
        f.write(f"fileName={self.lineNameToDatalog.text()}\n")
        f.write(f"medianFilterEnabled={self.checkMedianFilter.isChecked()}\n")
        f.write(f"medianFilterWindow={self.spinMedianWindow.value()}\n")
    print("Saved settings sucessfully!")


def load_settings(self):
    try:
        with open("settings.cfg", "r") as f:
            for line in f:
                key, value = line.strip().split("=")
                # if key == "SerialPort":
                #     self.comboBoxSerialPort.setCurrentIndex(int(value))
                if key == "sampleTime":
                    self.sampleTime.setText(value)
                elif key == "chargeVoltage":
                    self.spinChargeVoltage.setValue(float(value))
                elif key == "dischargeVoltage":
                    self.spinDischargeVoltage.setValue(float(value))
                elif key == "sensorIndex":
                    self.spinSensor.setValue(int(value))
                elif key == "bufferSize":
                    self.bufferSize.setText(value)
                elif key == "metalShieldBias":
                    self.spinMetalShieldBias.setValue(float(value))
                elif key == "datalogSensor0":
                    self.listSensorsToDatalog.item(0).setSelected(value == "True")
                elif key == "datalogSensor1":
                    self.listSensorsToDatalog.item(1).setSelected(value == "True")
                elif key == "datalogSensor2":
                    self.listSensorsToDatalog.item(2).setSelected(value == "True")
                elif key == "datalogSensor3":
                    self.listSensorsToDatalog.item(3).setSelected(value == "True")
                elif key == "datalogSensor4":
                    self.listSensorsToDatalog.item(4).setSelected(value == "True")
                elif key == "datalogSensor5":
                    self.listSensorsToDatalog.item(5).setSelected(value == "True")
                elif key == "datalogSensor6":
                    self.listSensorsToDatalog.item(6).setSelected(value == "True")
                elif key == "fileName":
                    self.lineNameToDatalog.setText(value)
                elif key == "medianFilterEnabled":
                    is_checked = value == "True"
                    self.checkMedianFilter.setChecked(is_checked)
                    # self.handle_median_filter_toggle(Qt.Checked if is_checked else Qt.Unchecked) # Ensure state propagates
                elif key == "medianFilterWindow":
                    self.spinMedianWindow.setValue(int(value))
        print("Loaded settings!")
    except FileNotFoundError:
        print("Settings file not found. Using default settings.")


def set_sensor(self):
    sensor_value = self.spinSensor.value()
    self.fgdos.output_channel_select(sensor_value)
    #self.fgdos.input_channel_select(sensor_value)


import pandas as pd
import matplotlib.pyplot as plt
import os

def plot_csv_data(filename):
    # Construct the full file path
    file_path = os.path.join('./datalog/', filename)

    # Read the CSV data
    data = pd.read_csv(file_path, comment='#')

    # Get the number of column pairs
    num_pairs = len(data.columns) // 2

    # Create a new plot
    plt.figure(figsize=(10, 6))

    # Plot each pair of columns
    for i in range(num_pairs):
        time_col = f'Time{i}'
        voltage_col = f'Voltage{i}'
        plt.plot(data[time_col], data[voltage_col], label=f'Pair {i+1}')

    # Add labels and title
    plt.xlabel('Time')
    plt.ylabel('Voltage')
    plt.title('Voltage vs Time')
    plt.legend()

    # Show the plot
    plt.show()

import numpy as np
from scipy.signal import lfilter, firwin, butter

class RealTimeFilter:
    def __init__(self, filter_type, order, cutoff):
        self.filter_type = filter_type
        self.order = order
        self.cutoff = cutoff / 0.5  # Normalize the frequency
        self.buffer = np.zeros(order + 1)
        if filter_type == 'FIR':
            self.coefficients = firwin(order + 1, cutoff)
        elif filter_type == 'IIR':
            self.coefficients, self.denominator = butter(order, cutoff, btype='low', analog=False, output='ba')

    def update(self, new_sample):
        self.buffer[:-1] = self.buffer[1:]
        self.buffer[-1] = new_sample
        if self.filter_type == 'FIR':
            return np.dot(self.buffer, self.coefficients)
        elif self.filter_type == 'IIR':
            return lfilter(self.coefficients, self.denominator, self.buffer)[-1]
        

    