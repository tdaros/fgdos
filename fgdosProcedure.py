from fgdosInterface import fgdosInterface
import time
import collections
import numpy as np
from analogDiscoveryProcedure import analogDiscoveryProcedure # Import AD2 class
MAX_VINJ = 12
MIN_VINJ = -12

MAX_VREF = 3.3
MIN_VREF = 0

VMS_CHANNEL = 15

DEFAULT_MEDIAN_FILTER_WINDOW_SIZE = 3
MAX_MEDIAN_FILTER_WINDOW_SIZE = 11 # Maxlen for the raw_adc_buffer

class fgdosProcedure(fgdosInterface):
    # Add new parameter use_analog_discovery_for_measurement
    def __init__(self, debug_mode=False, device='COM5', spinbox_sensor=None, spinbox_metalshield=None, update_plot=None, update_gui=None, use_analog_discovery_for_measurement=False):
        super().__init__(debug_mode, device)
        # Check if pico is connected before accessing it
        if self.pico and self.pico.connected: # Assuming pico has a 'connected' attribute or similar check
             self.offset_time = self.pico.tick()[1]
        else:
             self.offset_time = 0 # Or handle appropriately if pico is not connected
        self.spinbox_sensor = spinbox_sensor
        self.spinbox_metalshield = spinbox_metalshield
        self.median_filter_enabled = False
        self.median_filter_window_size = DEFAULT_MEDIAN_FILTER_WINDOW_SIZE
        # Buffer to store raw ADC readings for median filtering
        self.raw_adc_buffer = collections.deque(maxlen=MAX_MEDIAN_FILTER_WINDOW_SIZE) # Original line 29
        self.update_plot = update_plot
        self.update_gui = update_gui   # Moved here from after the if block

        # Add Analog Discovery instance and flag
        self.use_analog_discovery = use_analog_discovery_for_measurement # Original line 33
        self.adp = None # Initialize AD2 instance to None # Original line 34

        # Initialize AD2 if needed
        if self.use_analog_discovery: # Original line 37
            try: # Original line 38
                self.adp = analogDiscoveryProcedure() # Original line 39
                self.adp.setup_smu() # setup_smu is called here # Original line 40
                print("Analog Discovery initialized for measurement.")
            except Exception as e: # Added except block to handle initialization errors
                print(f"Failed to initialize Analog Discovery during __init__: {e}")
                self.adp = None
                # Optionally, you might want to set self.use_analog_discovery to False
                # if initialization is critical for its use:
                # self.use_analog_discovery = False

    def set_voltage(self, voltage: float, pin: str) -> None:
        assert pin in ["vinj", "vref"], "Invalid pin"
        if pin == "vinj":
            assert MIN_VINJ <= voltage <= MAX_VINJ, "Invalid voltage"
            duty = float(0.0016 * voltage**3 - 0.0199 * voltage**2 + 3.9165 * voltage + 52.419)
            status = self.set_pwm_output("vinj", duty)
        elif pin == "vref":
            assert MIN_VREF <= voltage <= MAX_VREF, "Invalid voltage"
            # duty = float((voltage - MIN_VREF) / (MAX_VREF - MIN_VREF) * 100)
            # duty = float(0.0272 * voltage**2 + 0.9223 * voltage - 0.0236)
            duty = float(voltage/0.0336 + 2.79167)
            status = self.set_pwm_output("vref", duty)
        return status

    def setup_charge(self, sensor: int, direction: str, voltage: float) -> None:
        assert sensor in range(7), "Invalid sensor number"
        assert direction in ["in", "out"], "Invalid direction"
        self.set_enable_input(0)
        self.set_voltage(voltage, "vinj")
        if direction == "in":
            assert 0 <= voltage <= 12, "Invalid voltage"
            self.input_channel_select(sensor)
        elif direction == "out":
            assert -6 <= voltage <= 0, "Invalid voltage"
            self.input_channel_select(sensor + 7)
        

    def setup_shield_bias(self, voltage: float) -> None:
        self.set_enable_input(0)
        assert -12 <= voltage <= 12, "Invalid voltage"
        self.set_voltage(voltage, "vinj")
        self.input_channel_select(VMS_CHANNEL) # VMS_CHANNEL is 15
        self.set_enable_input(1)
        
    def set_median_filter_enabled(self, enabled: bool):
        self.median_filter_enabled = enabled
        if not enabled:
            self.raw_adc_buffer.clear() # Clear buffer when disabling
        # print(f"Median filter {'enabled' if enabled else 'disabled'}")

    def set_median_filter_window_size(self, size: int):
        if 3 <= size <= MAX_MEDIAN_FILTER_WINDOW_SIZE and size % 2 == 1: # Ensure odd and within bounds
            self.median_filter_window_size = size
            # self.raw_adc_buffer = collections.deque(maxlen=size) # Re-create buffer if window size changes maxlen
            # print(f"Median filter window size set to: {size}")
        else:
            print(f"Invalid median filter window size: {size}. Must be odd and between 3 and {MAX_MEDIAN_FILTER_WINDOW_SIZE}.")

    # Add method to toggle AD2 usage
    def set_use_analog_discovery(self, enabled: bool):
        self.use_analog_discovery = enabled
        if enabled and self.adp is None:
            try:
                self.adp = analogDiscoveryProcedure()
                self.adp.setup_smu()
                print("Analog Discovery initialized for measurement.")
            except Exception as e:
                print(f"Failed to initialize Analog Discovery: {e}")
                self.adp = None
                self.use_analog_discovery = False # Disable if initialization fails
                # Provide feedback to GUI? Or GUI handles message? GUI handles message.
        elif not enabled and self.adp is not None:
             try:
                 self.adp.close_smu()
                 self.adp = None
                 print("Analog Discovery closed.")
             except Exception as e:
                 print(f"Error closing Analog Discovery: {e}")
                 # Keep adp instance? Or set to None anyway? Set to None.
                 self.adp = None

    # Modify get_measurement_voltage to use AD2 or internal ADC
    def get_measurement_voltage(self): # Removed n_samples_mean as it's not used in the current logic
        if self.use_analog_discovery and self.adp is not None:
            # Use Analog Discovery
            try:
                # AD2 measure_voltage returns (voltage, time)
                voltage_scaled, timestamp_s = self.adp.measure_voltage()
                if voltage_scaled is not None:
                    # AD2 returns scaled voltage directly
                    # No median filter needed here as AD2 handles averaging/sampling
                    return False, voltage_scaled, timestamp_s # status=False (success), data=voltage, timestamp
                else:
                    # AD2 measurement failed
                    print("[DEBUG fgdosProc] Analog Discovery measurement failed.")
                    return True, None, None # status=True (error), data=None, timestamp=None
            except Exception as e:
                print(f"[DEBUG fgdosProc] Error during Analog Discovery measurement: {e}")
                return True, None, None # status=True (error), data=None, timestamp=None

        else:
            # Use internal ADC (original logic)
            # pico.adc_read returns (status, value, reading_raw)
            # where status=0 is success.
            # Check if pico is connected before calling tick()
            timestamp_us = self.pico.tick()[1] if (self.pico and self.pico.connected) else 0 # Get timestamp *before* ADC read
            adc_status, _, reading_raw = self.get_measurement() # ADC_IN is 28, so this reads ADC 2
            timestamp_s = (timestamp_us - self.offset_time) / 1e6 # Timestamp relative to offset

            if adc_status == 0: # Success from ADC
                self.raw_adc_buffer.append(reading_raw)
                if self.median_filter_enabled and len(self.raw_adc_buffer) >= self.median_filter_window_size:
                    # Apply median filter
                    window_data = list(self.raw_adc_buffer)[-self.median_filter_window_size:]
                    filtered_raw_value = np.median(window_data)
                    # print(f"[DEBUG fgdosProc] TS={timestamp_s:.3f}s, Raw ADC: {reading_raw}, Filtered Raw: {filtered_raw_value:.0f} (Window: {self.median_filter_window_size})")
                    value_scaled = filtered_raw_value * 3.3 / 4095
                else:
                    # No filter or buffer not full enough
                    # print(f"[DEBUG fgdosProc] TS={timestamp_s:.3f}s, Raw ADC: status={adc_status}, reading_raw={reading_raw} (No filter)")
                    value_scaled = reading_raw * 3.3 / 4095
                return False, value_scaled, timestamp_s # Overall status is False (no error from this func), data is value_scaled, timestamp
            else:
                # print(f"[DEBUG fgdosProc] ADC Error: status={adc_status}")
                return True, None, None # Overall status is True (error from this func), data is None, timestamp=None

    def check_integrity(self) -> bool:
        measurements_0 = [0] * 7
        measurements_pos_1 = [0] * 7
        measurements_neg_1 = [0] * 7

        for sensor in range(7):
            self.setup_charge(sensor, "in", 0)
            time.sleep(0.5)
            measurements_0[sensor] = self.get_measurement_voltage()

            self.setup_charge(sensor, "in", 1)
            time.sleep(0.5)
            measurements_pos_1[sensor] = self.get_measurement_voltage()

            self.setup_charge(sensor, "out", -1)
            time.sleep(0.5)
            measurements_neg_1[sensor] = self.get_measurement_voltage()
    
    def reset_sensor(self,sensor):
        print("Resetting sensor:", sensor)
        self.setup_charge(sensor, "in", 11.0)
        self.set_enable_input(1)
        time.sleep(0.1)
        self.setup_charge(sensor, "out", -3.0)
        self.set_enable_input(1)
        time.sleep(0.05)
        self.set_enable_input(0)

    def positive_pulse(self,sensor,voltage):
        self.setup_charge(sensor, "in", voltage)
        self.set_enable_input(1)
        self.set_enable_input(0)
    
    def negative_pulse(self,sensor,voltage):
        self.setup_charge(sensor, "out", voltage)
        self.set_enable_input(1)
        self.set_enable_input(0)

    def auto_charge(self, sensor: int, target_voltage: float = 2.8, n_samples_mean: int = 8) -> float:
        measurement = self.get_average_measurement(n_samples_mean)
        discharge_voltage = target_voltage - 6
        charge_voltage = target_voltage + 8
        pulses = 0
        tolerance = 0.0001
        current_shield_bias_voltage = None
        if self.spinbox_metalshield:
            current_shield_bias_voltage = self.spinbox_metalshield.value()
        if current_shield_bias_voltage is not None:
            self.setup_shield_bias(current_shield_bias_voltage)
            time.sleep(0.001) # Optional: delay for shield bias to settle

        while measurement > target_voltage + tolerance:
            self.setup_charge(sensor, "out", discharge_voltage)
            self.set_enable_input(1)
            self.set_enable_input(0)
            pulses = pulses + 1
            if current_shield_bias_voltage is not None:
                self.setup_shield_bias(current_shield_bias_voltage)
                time.sleep(0.01) # Optional: delay for shield bias to settle
            measurement = self.get_average_measurement(n_samples_mean)
            print("Measurement: {:.4f}".format(round(measurement, 4)), "Discharge Voltage:", discharge_voltage, "Pulses:", pulses)
            if pulses > 4:
                discharge_voltage = discharge_voltage - 0.025
                pulses = 0
            if discharge_voltage < discharge_voltage - 0.5:
                break
        while measurement < target_voltage - tolerance:
            self.setup_charge(sensor, "in", charge_voltage)
            self.set_enable_input(1)
            self.set_enable_input(0)
            pulses = pulses + 1
            if current_shield_bias_voltage is not None:
                self.setup_shield_bias(current_shield_bias_voltage)
                time.sleep(0.01) # Optional: delay for shield bias to settle
            measurement = self.get_average_measurement(n_samples_mean)
            print("Measurement: {:.4f}".format(round(measurement, 4)), "Charge Voltage:", charge_voltage, "Pulses:", pulses)
            if pulses > 4:
                charge_voltage = charge_voltage + 0.025
                pulses = 0
            if charge_voltage > charge_voltage + 0.5:
                break
            
    # def charge(self):
    
    # def discharge(self):

    def get_delta(self, sensor: int):
        initial_voltage = self.get_average_measurement(50)
        self.setup_charge(sensor, "out", -1)
        self.set_enable_input(1)
        time.sleep(0.1)
        final_voltage = self.get_average_measurement(50)
        self.set_enable_input(0)
        return initial_voltage - final_voltage

    def get_average_measurement(self, n_samples: int) -> float:
        measurements = [0] * n_samples
        measurements = [] # Use a list to store valid measurements
        for i in range(n_samples):
            # status, measurement = self.get_measurement_voltage() # Old call
            status, measurement, _ = self.get_measurement_voltage() # New call (ignore timestamp)
            if not status and measurement is not None: # Check status and if measurement is not None
                measurements.append(measurement)
            # Optional: Add a small delay between samples if needed for AD2 or ADC
            time.sleep(0.005) # 5ms delay between samples
        if not measurements: # Handle case where no valid measurements were collected
            return 0.0 # Return 0 or raise an error? Returning 0 might prevent crashes.
        return sum(measurements) / n_samples

    def get_timestamp(self) -> float:
        return self.pico.tick()[1] - self.offset_time
    
    def reset_timestamp_offset(self) -> None:
        self.offset_time = self.pico.tick()[1]

    def auto_charge_all(self, target_voltage: float = 2.8, n_samples_mean: int = 4, cycles = 4) -> None:
        for cycle in range(cycles):
            print("Cycle: " + str(cycle))
            for sensor in range(7):
                print("Sensor:", sensor)
                self.spinbox_sensor.setValue(sensor)
                #self.reset_sensor(sensor)
                self.auto_charge(sensor, target_voltage, n_samples_mean)

    def enable_feedback(self,voltage):
        self.set_voltage(voltage, "vref")
        self.set_output_feedback(1)
        self.feedback_channel_select(7)
        self.set_enable_feedback_channel(1)
        self.set_enable_feedback_buffer(1)

    def disable_feedback(self):
        self.set_output_feedback(0)
        self.set_enable_feedback_channel(0)

    # Add a close method to clean up AD2 if it was initialized
    def close(self):
        super().close() # Call the close method of the parent class (fgdosInterface)
        if self.adp is not None:
            try:
                self.adp.close_smu()
                self.adp = None
            except Exception as e:
                print(f"Error during Analog Discovery cleanup: {e}")
        self.set_enable_feedback_buffer(0)