import time
import dwf

#constants
HZ_ACQ = 1e6
N_SAMPLES = 20000
OFFSET_CORRECTION = -0.012

class analogDiscoveryProcedure:
    def __init__(self):
        """
        Initializes the procedure.
        'total_samples_processed' will track the number of samples (ticks) for precise timing.
        'acquisition_frequency' will store the actual frequency set on the device.
        """
        #print DWF version
        self.smu = None
        self.total_samples_processed = 0
        self.acquisition_frequency = 0
        #print("DWF Version: " + dwf.FDwfGetVersion())

    def connect_smu(self):
        """Creates and returns a DwfAnalogIn object."""
        # Create a PyVISA resource manager
        smu = dwf.DwfAnalogIn()
        return smu
    
    def setup_smu(self):
        """
        Connects and configures the Analog Discovery for record-mode acquisition.
        The actual sampling frequency is retrieved and stored for precise time calculations.
        """
        if self.smu == None:
            self.smu = self.connect_smu()
        self.smu.channelEnableSet(0, True)
        self.smu.channelRangeSet(0, 10.0)

        self.smu.acquisitionModeSet(self.smu.ACQMODE.RECORD)
        self.smu.frequencySet(HZ_ACQ)
        
        # Get the actual frequency from the device for accurate timing
        self.acquisition_frequency = self.smu.frequencyGet()
        
        self.smu.recordLengthSet(N_SAMPLES / self.acquisition_frequency)
        
        # Reset the sample counter at the beginning of a new setup
        self.total_samples_processed = 0
        
        time.sleep(2) ## for offset stabilization
        #print("AD2 Setup done.")

        
    # def refresh_smu(self):
    #     self.smu.smua.source.output = self.smu.smua.OUTPUT_OFF
    #     self.smu.smua.source.output = self.smu.smua.OUTPUT_ON

    def measure_voltage(self):
        """
        Performs a voltage measurement, acquiring a block of samples.
        The timestamp is now calculated precisely using the sample count (ticks) and the device's internal clock frequency,
        representing the time at the center of the acquired data block.
        """
        try:
            rgdSamples = []
            cSamples = 0
            fLost = False
            fCorrupted = False
            self.smu.configure(False, True)
            while cSamples < N_SAMPLES:
                sts = self.smu.status(True)
                if cSamples == 0 and sts in (self.smu.STATE.CONFIG,
                                            self.smu.STATE.PREFILL,
                                            self.smu.STATE.ARMED):
                    # Acquisition not yet started.
                    continue

                cAvailable, cLost, cCorrupted = self.smu.statusRecord()
                if cSamples < N_SAMPLES and sts == self.smu.STATE.DONE and cAvailable == 0:
                    print("DING!")
                    #self.smu.configure(False, True)
                    break
                cSamples += cLost
                    
                if cLost > 0:
                    fLost = True
                if cCorrupted > 0:
                    fCorrupted = True
                if cAvailable == 0:
                    continue
                if cSamples + cAvailable > N_SAMPLES:
                    cAvailable = N_SAMPLES - cSamples
                
                # get samples
                rgdSamples.extend(self.smu.statusData(0, cAvailable))
                cSamples += cAvailable

            if not rgdSamples:
                print("Measurement failed: No samples were acquired.")
                return None, None
                
            #print("Recording finished")
            # if fLost:
            #     print("LOST!")
            #     raise Exception("Samples were lost! Reduce frequency")
            # if cCorrupted:
            #     print("CORRUPTED!")
            #     raise Exception("Samples could be corrupted! Reduce frequency")
            #print("Samples left: " + str(self.smu.statusSamplesLeft()))
            
            voltage_measurement = sum(rgdSamples) / len(rgdSamples)

            # --- Precise Time Calculation using Ticks ---
            # Calculate a timestamp for the center of the current data block.
            block_center_sample_index = self.total_samples_processed + (len(rgdSamples) / 2.0)
            time_measurement = block_center_sample_index / self.acquisition_frequency

            # Update the total number of processed samples for the next measurement.
            self.total_samples_processed += len(rgdSamples)
            
            return float(voltage_measurement) + OFFSET_CORRECTION, float(time_measurement)
        except dwf.DWFError as e:
            print(f"Error in measurement: {e}. Returning Nil.")
            return None, None
        except Exception as e:
            print(f"An unexpected error occurred in measurement: {e}. Returning Nil.")
            return None, None

    def close_smu(self):
        self.smu.reset()
        pass
    
    def get_id(self):
        pass
    
    def get_timestamp(self):
        pass