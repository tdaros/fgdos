import picod as pico

# Define pin numbers
DEBUG_PIN = 29

# Define input selection pins
IN_SEL0 = 0
IN_SEL1 = 1
IN_SEL2 = 2
IN_SEL3 = 3
IN_SEL_EN = 4

# Define output selection pins
OUT_SEL0 = 5
OUT_SEL1 = 6
OUT_SEL2 = 7
OUT_SEL_EN = 8

# Define feedback selection pins
FB_SEL0 = 9
FB_SEL1 = 10
FB_SEL2 = 11
FB_SEL_EN = 12

# Define output feedback selection pin
OUT_FB_SEL = 13
# Define enable feedback pin
EN_FB_BUFFER = 27

# Define PWM output pins
PWM_OUT_VINJ = 14
PWM_OUT_VREF = 15

PWM_FREQ = 125e3 # 125 kHz PWM frequency

# Define charge pump shutdown pin
CP_SHUTDOWN = 26

# Define ADC input pin
ADC_IN = 28

class fgdosInterface():
    def __init__(self, debug_mode=False, device='COM5'):
        self.pico = None  # Initialize pico to None
        try:
            self.pico = pico.pico(device)
        except Exception as e:
            print(f'Interface not connected: {e}')
            raise  # Re-raise the exception to be caught by the GUI

        if debug_mode:
            pico.GPIO_set_input(DEBUG_PIN)
        self._input_gpio = 1 << IN_SEL0 | 1 << IN_SEL1 | 1 << IN_SEL2 | 1 << IN_SEL3
        self._output_gpio = 1 << OUT_SEL0 | 1 << OUT_SEL1 | 1 << OUT_SEL2
        self._feedback_gpio = 1 << FB_SEL0 | 1 << FB_SEL1 | 1 << FB_SEL2
        self._out_channel_gpio = 1 << OUT_FB_SEL
        self._enable_gpio = 1 << IN_SEL_EN | 1 << OUT_SEL_EN | 1 << FB_SEL_EN | 1 << EN_FB_BUFFER
        #print(self._input_gpio | self._output_gpio | self._feedback_gpio | self._out_channel_gpio | self._enable_gpio)
        # Set the GPIO pins
        self.pico.GPIO_set_dir(
            self._input_gpio | self._output_gpio | self._feedback_gpio | self._out_channel_gpio | self._enable_gpio,
            self._input_gpio | self._output_gpio | self._feedback_gpio | self._out_channel_gpio | self._enable_gpio,
            0)
        self.pico.gpio_set_output(CP_SHUTDOWN, 0)
        #self.pico.gpio_set_output(PWM_OUT_VINJ, 0)
        #self.pico.gpio_set_output(PWM_OUT_VREF, 0)


        # Initialize the PWM outputs
        statusPWM = self.pico.tx_pwm(PWM_OUT_VINJ, PWM_FREQ, 52)
        if statusPWM > 0:
            print('PWM VINJ output failed to initialize')
            print('PWM status:', statusPWM)
        statusPWM = self.pico.tx_pwm(PWM_OUT_VREF, PWM_FREQ, 52)
        if statusPWM > 0:
            print('PWM VREF output failed to initialize')
            print('PWM status:', statusPWM)


    def input_channel_select(self, channel):
        # Set the input selection pins
        channel = channel << IN_SEL0
        self.pico.GPIO_write(self._input_gpio, channel)

    def set_enable_input(self, state):
        # Set the enable input pin
        state = state << IN_SEL_EN
        self.pico.GPIO_write(1 << IN_SEL_EN, state)

    def output_channel_select(self, channel):
        # Set the output selection pins
        channel = channel << OUT_SEL0  
        self.pico.GPIO_write(self._output_gpio, channel  )

    def set_enable_output(self, state):
        # Set the enable output pin
        state = state << OUT_SEL_EN
        self.pico.GPIO_write(1 << OUT_SEL_EN, state)

    def feedback_channel_select(self, channel):
        # Set the feedback selection pins
        channel = channel << FB_SEL0
        self.pico.GPIO_write(self._feedback_gpio, channel)

    def set_enable_feedback_channel(self, state):
        # Set the enable feedback pin
        state = state << FB_SEL_EN
        self.pico.GPIO_write(1 << FB_SEL_EN, state)
    
    def set_enable_feedback_buffer(self, state):
        # Set the enable feedback buffer pin
        state = not state
        state = state << EN_FB_BUFFER
        self.pico.GPIO_write(1 << EN_FB_BUFFER, state)

    

    def set_output_feedback(self, state):
        # Set the output feedback selection pin
        state = state << OUT_FB_SEL
        self.pico.GPIO_write(1 << OUT_FB_SEL, state)

    def get_measurement(self):
        # Read the ADC input pin
        return self.pico.adc_read(ADC_IN - 26)
    
    def set_pwm_output(self, channel, duty_cycle):
        # Set the PWM output pins
        status = None
        if channel == 'vinj':
            status = self.pico.tx_pwm(PWM_OUT_VINJ, PWM_FREQ, duty_cycle)
        elif channel == 'vref':
            status = self.pico.tx_pwm(PWM_OUT_VREF, PWM_FREQ, duty_cycle)
        return status

    def get_debug_pin(self):
        # Read the debug pin
        return self.pico.gpio_read(DEBUG_PIN)
    
    def set_charge_pump_shutdown(self, state):
        # Set the charge pump shutdown pin
        self.pico.gpio_write(CP_SHUTDOWN, state)

    def get_status(self):
        # Get the status of the Pico by performing a real I/O operation
        if self.pico is None:
            return False
        try:
            self.pico.tick()  # This will fail if the device is disconnected
            return True
        except Exception:
            return False

    def close(self):
        """Safely close the connection to the pico device."""
        if self.pico:
            try:
                self.pico.close()
                print("Pico interface closed.")
            except Exception as e:
                print(f"Error closing pico interface: {e}")