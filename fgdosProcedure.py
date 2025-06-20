from fgdosInterface import fgdosInterface
import time
import collections
import numpy as np

MAX_VINJ = 12
MIN_VINJ = -12

MAX_VREF = 3.3
MIN_VREF = 0

VMS_CHANNEL = 15

DEFAULT_MEDIAN_FILTER_WINDOW_SIZE = 3
MAX_MEDIAN_FILTER_WINDOW_SIZE = 11 # Maxlen for the raw_adc_buffer

class fgdosProcedure(fgdosInterface):
    def __init__(self, debug_mode=False, device='COM5', spinbox_sensor=None, spinbox_metalshield=None, update_plot=None, update_gui=None):
        super().__init__(debug_mode, device)
        self.offset_time = self.pico.tick()[1]
        self.spinbox_sensor = spinbox_sensor
        self.spinbox_metalshield = spinbox_metalshield
        self.median_filter_enabled = False
        self.median_filter_window_size = DEFAULT_MEDIAN_FILTER_WINDOW_SIZE
        # Buffer to store raw ADC readings for median filtering
        self.raw_adc_buffer = collections.deque(maxlen=MAX_MEDIAN_FILTER_WINDOW_SIZE)
        self.update_plot = update_plot
        self.update_gui = update_gui

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

    def get_measurement_voltage(self, n_samples_mean=1):
        # pico.adc_read returns (status, value, reading_raw)
        # where status=0 is success.
        timestamp_us = self.pico.tick()[1] # Get timestamp *before* ADC read
        adc_status, _, reading_raw = self.get_measurement() # ADC_IN is 28, so this reads ADC 2
        timestamp_s = (timestamp_us - self.offset_time) / 1e6
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
            return False, value_scaled # Overall status is False (no error from this func), data is value_scaled, timestamp is handled by gui_core_fgdos
        else: # Error from ADC
            # print(f"[DEBUG fgdosProc] ADC Error: status={adc_status}")
            return True, None # Overall status is True (error from this func), data is None


        
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
        while measurement > target_voltage + tolerance:
            self.setup_charge(sensor, "out", discharge_voltage)
            self.set_enable_input(1)
            self.set_enable_input(0)
            pulses = pulses + 1
            measurement = self.get_average_measurement(n_samples_mean)
            print("Measurement: {:.3f}".format(round(measurement, 3)), "Discharge Voltage:", discharge_voltage, "Pulses:", pulses)
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
            measurement = self.get_average_measurement(n_samples_mean)
            print("Measurement: {:.3f}".format(round(measurement, 3)), "Charge Voltage:", charge_voltage, "Pulses:", pulses)
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
        for i in range(n_samples):
            status, measurement = self.get_measurement_voltage()
            if not status:
                measurements[i] = measurement
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
        self.set_enable_feedback_buffer(0)
