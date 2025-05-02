from max30102 import MAX30102
import hrcalc
import time
import numpy as np

SAMPLE_INTERVAL = 0.01

def main():
    max102 = MAX30102()
    ir_data = []
    red_data = []
    bpms = []
    flag = False
    
    try:
        while True:
            # check if any data is available
            num_bytes = max102.get_data_present()
            if num_bytes > 0:
                # grab all the data and stash it into arrays
                while num_bytes > 0:
                    red, ir = max102.read_fifo()
                    num_bytes -= 1
                    ir_data.append(ir)
                    red_data.append(red)

                while len(ir_data) > 100:
                    ir_data.pop(0)
                    red_data.pop(0)

                if len(ir_data) == 100:
                    bpm, valid_bpm, spo2, valid_spo2 = hrcalc.calc_hr_and_spo2(ir_data, red_data)
                    if valid_bpm:
                        bpms.append(bpm)
                        while len(bpms) > 4:
                            bpms.pop(0)
                        bpm = np.mean(bpms)
                        if (np.mean(ir_data) < 50000 and np.mean(red_data) < 50000):
                            bpm = 0
                            if flag == False:
                                print("Finger not detected")
                                flag = True
                        else:
                            flag = False
                            temperature = max102.read_temperature()
                            print("BPM: {0}, SpO2: {1:.1f}, temp {2:.1f}".format(bpm, spo2, temperature))

            time.sleep(SAMPLE_INTERVAL)
    
    except KeyboardInterrupt:
        max102.shutdown()
        print("\nMonitoring stopped.")

if __name__ == "__main__":
    main()