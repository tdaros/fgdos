import os
import csv
import datetime
import smuProcedure as smu
import analogDiscoveryProcedure as adp
from PyQt5.QtCore import QTimer, QThread, pyqtSignal
import time
from picod import tick_diff

class Worker(QThread):
    dataReady = pyqtSignal(list, list)

    def __init__(self, datalogger, mode, sensors_to_log = None, fgdos=None): 
        super().__init__()
        self.datalogger = datalogger
        self.sensors_to_log = sensors_to_log
        self.mode = mode
        self.fgdos = fgdos
        if not self.mode == 'adc':
            self.smu = smu.smuProcedure(self.mode=='sim')
        if self.mode == 'smu':
            self.smu.setup_smu()
        elif self.mode == 'sim':
            self.time_measurement_offset = time.time()
        elif self.mode == 'adc':
            self.time_measurement_offset = self.datalogger.fgdos.pico.tick()[1]
        elif self.mode == 'adp':
            print("Selected Analog Discovery as Datalogger!")
            self.smu = adp.analogDiscoveryProcedure()
            self.smu.setup_smu()

    def run(self):
        self.datalogger.measurement_running = True
        voltage_measurement = {}
        time_measurement = {}
        if self.mode == 'sim':
            for i in self.sensors_to_log:
                voltage_measurement[i], time_measurement[i] = self.smu.simulate_measurement()
        elif self.mode == 'smu': 
            for i in self.sensors_to_log:
                self.datalogger.fgdos.output_channel_select(i)
                try:
                    voltage_measurement[i], time_measurement[i] = self.smu.measure_voltage()
                except:	
                    print("Error in measurement. Returning 0.")
                    voltage_measurement[i], time_measurement[i] = None, None
        elif self.mode == 'adc':
            for i in self.sensors_to_log:
                _, voltage_measurement[i] = self.datalogger.fgdos.get_measurement_voltage()
                tick = self.datalogger.fgdos.pico.tick()
                time_measurement[i] = tick_diff(self.time_measurement_offset, tick[1])
        elif self.mode == 'adp': 
            for i in self.sensors_to_log:
                self.datalogger.fgdos.output_channel_select(i)
                try:
                    voltage_measurement[i], time_measurement[i] = self.smu.measure_voltage()
                except:	
                    print("Error in measurement. Returning 0.")
                    voltage_measurement[i], time_measurement[i] = None, None
        self.dataReady.emit([voltage_measurement], [time_measurement])

    def close_smu(self):
        self.smu.close_smu()

class dataLogger:
    def __init__(self, mode='smu', pauseButton=None,progressBarDatalog=None, fgdos = None, sensor_list = None, filename_prefix = None):
        self.sensor_list = sensor_list
        
        self.mode = mode
        self.pauseButton = pauseButton
        self.voltage_measurement = []
        self.time_measurement = []
        if self.mode == 'sim':
            self.time_measurement_offset = self.fgdos.pico.tick()[1]
        elif self.mode == 'sim':
            self.time_measurement_offset = time.time()
        elif self.mode == 'smu':
            self.time_measurement_offset = 0
        elif self.mode == 'adp':
            self.time_measurement_offset = 0
        self.time_measurement_pause = 0
        self.measurement_running = False
        self.filename = None
        self.filename_prefix = filename_prefix
        self.timerDatalog = QTimer()
        self.timerDatalog.timeout.connect(self.start_measurement)
        self.progressBarDatalog = progressBarDatalog
        self.fgdos = fgdos

    def start_log_data(self):
        self.sensors_to_log = []
        for i in range(self.sensor_list.count()):
            if self.sensor_list.item(i).isSelected():
                self.sensors_to_log.append(int(self.sensor_list.item(i).text()))

        # Create a new Worker instance
        self.worker = Worker(self, self.mode, self.sensors_to_log)
        self.worker.dataReady.connect(self.handle_data_ready)
        # Create the datalog directory if it doesn't exist
        if not os.path.exists('./datalog'):
            os.makedirs('./datalog')

        # Find the highest existing file number
        filename_prefix_text = self.filename_prefix.text()
        existing_files = os.listdir('./datalog')
        print('Filename Prefix:' + filename_prefix_text)
        matching_files = [file for file in existing_files if file.startswith(filename_prefix_text) and file.endswith('.csv')]

        existing_numbers = []
        for file in matching_files:
            try:
                number_part = file[len(filename_prefix_text):-4]
                existing_numbers.append(int(number_part))
            except ValueError:
                print(f"Warning: Skipping file with non-numeric component: {file}")
        if existing_numbers:
            max_number = max(existing_numbers)
        else:
            max_number = 0

        # Create a new file with an incremental name
        self.filename = f'./datalog/'+filename_prefix_text+f'{max_number + 1:04d}.csv'

        # Write the header and data to the file
        with open(self.filename, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['#'+datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')])  # Date and time from the OS
            headers = []
            for i in self.sensors_to_log:
                headers.extend(['Time' + str(i), 'Voltage' + str(i)])
            writer.writerow(headers)  # Column headers

        # Start the timer with a delay of 100 ms
            
        self.timerDatalog.start(400)
        self.progressBarDatalog.setValue(100)

    def start_measurement(self):
        if not self.measurement_running:
            self.worker.start()

    def handle_data_ready(self, voltage_measurement, time_measurement):
        #print("Handling data...")
        if self.filename is None:
            return
        self.voltage_measurement = voltage_measurement[0]  # Get the dictionary from the list
        self.time_measurement = time_measurement[0]  # Assuming time_measurement has the same structure
        with open(self.filename, 'a', newline='') as file:
            writer = csv.writer(file)
            row = []
            for i in self.sensors_to_log:
                row.extend([self.time_measurement[i], self.voltage_measurement[i]])
            writer.writerow(row)
        #print("Done.")
        self.measurement_running = False


    def stop_log_data(self):
        self.timerDatalog.stop()
        self.worker.wait()
        if self.mode == 'smu':
            self.worker.close_smu()
        self.filename = None
        self.voltage_measurement = []
        self.time_measurement = []
        self.measurement_running = False
        self.progressBarDatalog.setValue(0)
        self.time_measurement_pause_offset = 0 
        self.time_measurement_pause = 0
        del self.worker


    def toggle_log_data(self):
        if self.worker.isRunning():
            print("Pausing")
            self.pause_log_data()
        else:
            print("Resuming")
            self.resume_log_data()

    def pause_log_data(self):
        self.timerDatalog.stop()
        self.worker.wait()
        if self.mode == 'smu':
            self.time_measurement_pause_offset = 0
        elif self.mode == 'sim':
            self.time_measurement_pause_offset = time.time()
        elif self.mode == 'adc':
            self.time_measurement_pause_offset = self.fgdos.pico.tick()[1]
        self.measurement_running = False
        self.progressBarDatalog.setValue(20)
        self.pauseButton.setText('Resume')

    def resume_log_data(self):
        resume_time = 0
        if self.mode == 'smu':
            self.time_measurement_pause_offset = 0
        elif self.mode == 'sim':
            resume_time = time.time()
        elif self.mode == 'adc':
            resume_time = self.fgdos.pico.tick()[1]

        self.time_measurement_pause += resume_time - self.time_measurement_pause_offset
        self.timerDatalog.start(100)
        self.measurement_running = True
        self.progressBarDatalog.setValue(100)
        self.pauseButton.setText('Pause')