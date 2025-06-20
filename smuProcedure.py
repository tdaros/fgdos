import pyvisa #USB0::0x05E6::0x2634::4127747::0::INSTR
import numpy as np
import time
from keithley2600 import Keithley2600
pyvisa.ResourceManager()
class smuProcedure:
    def __init__(self, debug_mode = False):
        if not debug_mode:
            self.smu = self.connect_smu()
            self.id = None

    def connect_smu(self):
        # Create a PyVISA resource manager
        smu = Keithley2600('USB0::0x05E6::0x2604::4630250::0::INSTR', visa_library='@ivi')
        return smu
    
    def setup_smu(self):
        if self.smu.connected:
            print("SMU Connected.")
        self.smu.status.reset()
        self.smu.smua.source.func = self.smu.smua.OUTPUT_DCAMPS 
        self.smu.smua.source.leveli = 0  # set the current level to 0.1A
        self.smu.smua.sense = self.smu.smua.SENSE_LOCAL 
        self.smu.set_integration_time(self.smu.smua, 0.2)  # set the integration time to 1 power line cycle
        self.smu.settime(0)
        self.smu.play_chord(('C4', 'Eb4', 'G4'), 0.1)
        self.smu.smua.source.output = self.smu.smua.OUTPUT_ON   # turn on SMUA
        print(self.smu.read_error_queue())
        
    # def refresh_smu(self):
    #     self.smu.smua.source.output = self.smu.smua.OUTPUT_OFF
    #     self.smu.smua.source.output = self.smu.smua.OUTPUT_ON

    def measure_voltage(self):
        try:
            voltage_measurement = self.smu.smua.measure.v()
            time_measurement = self.smu.os.time()
            return float(voltage_measurement), float(time_measurement)
        except:
            print("Error in measurement. Returning Nil.")
            return None, None
    
    def close_smu(self):
        self.smu.smua.source.output = self.smu.smua.OUTPUT_OFF
        print("SMU Closed.")


    def simulate_measurement(self):
        noise = np.random.uniform(-0.05, 0.05)  # Add random noise between -0.05 and 0.05
        amplitude = 5  # Amplitude of the sine wave
        frequency = 1 / 10  # Frequency of the sine wave (1 period every 10 seconds)
        phase = 0  # Phase of the sine wave
        current_time = time.time()
        voltage_measurement = amplitude * np.sin(2 * np.pi * frequency * current_time + phase) + noise
        time.sleep(0.1)
        return voltage_measurement, current_time

    
    def get_id(self):
        return self.id
    
    def get_timestamp(self):
        return self.smu.os.time()
