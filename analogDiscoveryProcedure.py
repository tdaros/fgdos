import time
import dwf

#constants
HZ_ACQ = 1e6
N_SAMPLES = 20000
OFFSET_CORRECTION = -0.012

class analogDiscoveryProcedure:
    def __init__(self):
        #print DWF version
        self.smu = None
        #print("DWF Version: " + dwf.FDwfGetVersion())

    def connect_smu(self):
        # Create a PyVISA resource manager
        smu = dwf.DwfAnalogIn()
        return smu
    
    def setup_smu(self):

        if self.smu == None:
            self.smu = self.connect_smu()
        self.smu.channelEnableSet(0, True)
        self.smu.channelRangeSet(0, 10.0)

        self.smu.acquisitionModeSet(self.smu.ACQMODE.RECORD)
        self.smu.frequencySet(HZ_ACQ)
        self.smu.recordLengthSet(N_SAMPLES / HZ_ACQ)
        time.sleep(2) ## for offset stabilization
        self.time_measurement_offset = time.time()
        #print("AD2 Setup done.")

        
    # def refresh_smu(self):
    #     self.smu.smua.source.output = self.smu.smua.OUTPUT_OFF
    #     self.smu.smua.source.output = self.smu.smua.OUTPUT_ON

    def measure_voltage(self):
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
            #print("Recording finished")
            # if fLost:
            #     print("LOST!")
            #     raise Exception("Samples were lost! Reduce frequency")
            # if cCorrupted:
            #     print("CORRUPTED!")
            #     raise Exception("Samples could be corrupted! Reduce frequency")
            #print("Samples left: " + str(self.smu.statusSamplesLeft()))
            voltage_measurement = sum(rgdSamples) / len(rgdSamples)
            time_measurement = time.time() - self.time_measurement_offset
            return float(voltage_measurement) + OFFSET_CORRECTION, float(time_measurement)
        except:
            print("Error in measurement. Returning Nil.")
            return None, None
    
    def close_smu(self):
        self.smu.reset()
        pass
    
    def get_id(self):
        pass
    
    def get_timestamp(self):
        pass