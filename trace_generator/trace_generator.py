import math
import random
import sys
import matplotlib.pyplot as plt
import numpy as np



MS_IN_S = 1000
BYTES_PER_PKT = 1500.0
BITS_IN_BYTE = 8.0
BYTES_IN_MEGABYTES = 1000.0
MEGABITS_PER_SECOND_TO_BYTES_PER_MS = 125.0
END_DURATION = 30 # seconds

class Trace_Generator():

    def __init__(self, min_thr, max_thr, padding = 2, jitter_freq = 500):
        self.min_thr = min_thr
        self.max_thr = max_thr
        self.padding = padding  # max, min - padding to allow for jitter
        self.jitter_freq = jitter_freq

    def _clamp(self, val):
        max_val = self.max_thr - self.padding
        min_val = self.min_thr + self.padding

        #print(f'clamp: min_val = {min_val}, max_val = {max_val}, val = {val}')
        return max(min(max_val, val), min_val)

    def _get_new_thr(self, prev_thr, change_type):
        #print(f"change_type: {change_type}")
        if change_type == 'random-big':
            change = random.uniform(10, 15)
            sign = random.randint(0, 10)
            return self._clamp(prev_thr + math.pow(-1, sign) * change)
        elif change_type == 'random-small':
            change = random.uniform(1, 3)
            sign = random.randint(0, 10)
            return self._clamp(prev_thr + math.pow(-1, sign) * change)
        elif change_type == 'random-increase-small':
            change = random.uniform(2, 5)
            return self._clamp(prev_thr + change)
        elif change_type == 'random-increase-big':
            change = random.uniform(10, 15)
            #print(f"change to be added: {change}")
            val = self._clamp(prev_thr + change)
            #print(f'val: {val}')
            return val    
        elif change_type == 'random-decrease-small':
            change = random.uniform(0, 5)            
            val = self._clamp(prev_thr - change)
            return val
        elif change_type == 'random-decrease-big':
            change = random.uniform(10, 15)
            return self._clamp(prev_thr - change)
        else:
            change_type = change_type.split()
            if change_type[0] == 'increase':
                return self._clamp(prev_thr + float(change_type[1]))
            elif change_type[0] == 'decrease':
                return self._clamp(prev_thr - float(change_type[1]))



    def generate_trace(self, start_thr, duration, change_times, change_type, jitter, variants = 1, trace_name = None, end_thr = None):
        """
        starts at `start_thr` generates gaussian noise with jitter range 
        till first change_time and changes the thr based on change_type
        """
        all_time_ms = []
        all_thr = []
        for variant in range(variants):
            print(f"generate_trace called with args: start_thr:{start_thr} duration={duration} change_times={change_times} change_type={change_type} jitter={jitter} trace_name={trace_name} end_thr={end_thr}")
            if jitter > self.padding:
                jitter = 1.5
            time_ms = []
            thr = []
            #print(f"change_times = {change_times}")
            #sys.exit()
            # split duration to ms
            prev_thr = start_thr
            curr_thr = start_thr + random.uniform(-jitter, jitter)
            #print(f"start_thr = {start_thr}")
            for s in range(duration):
                if s == duration - 1 and end_thr is not None:
                    prev_thr = curr_thr
                    curr_thr = end_thr
                elif s in change_times:
                    #print(f"s is : {s}, change_times: {change_times}")
                    index = change_times.index(s)
                    prev_thr = curr_thr
                    #print(f"initial thr was: {curr_thr}")
                    curr_thr = self._get_new_thr(curr_thr, change_type[index])
                    #print(f"new thr is: {curr_thr}")
                for ms in range(MS_IN_S):
                    if ms % self.jitter_freq == 0:
                        #print(f"adding jitter to {curr_thr}")
                        jitter_thr = curr_thr + random.uniform(-jitter, jitter)
                        thr.append(jitter_thr)
                    else:
                        thr.append(curr_thr)
                    time_ms.append(s * MS_IN_S + ms)
                prev_thr = curr_thr
                self.printProgress(s, duration+1, f"{trace_name}{variant}")
            print()

            if trace_name is not None:
                self.save_trace(time_ms, thr, f"{trace_name}{variant}-ms")
            all_time_ms.append(time_ms)
            all_thr.append(thr)
            self.printProgress(variant, variants, f"{trace_name}")
        print()
        return all_time_ms, all_thr

    def convert_trace_to_seconds(self, time_ms, thr):
        time_sec = []
        thr_sec = []
        for i in range(len(time_ms)):
            if i % MS_IN_S == 0:
                time_sec.append(time_ms[i] / MS_IN_S)
                thr_sec.append(thr[i])
        return time_sec, thr_sec

    def save_trace(self, times, thrs, trace_name):
        with open(trace_name, 'w') as tf:
            for i in range(len(times)):
                    tf.write(f"{times[i]} {thrs[i]}\n")
        return

    def load_trace(self, trace_name):
        times = []
        thrs = []
        try:
            with open(trace_name, "r") as tf:
                for line in tf:
                    line = line.split()
                    times.append(line[0])
                    thrs.append(line[1])
        except:
            print("file doesn't exist")
            return None, None
        return times, thrs

    def printProgress(self, curr, total, desc=None):
        bar = '#'
        space = '-'
        period = '.'
        num_periods = 3
        progress_bar_length = 50
        done = math.ceil((curr / total) * progress_bar_length)
        pc = math.ceil((curr / total) * 100)
        remaining = progress_bar_length - done
        print(f"\r {desc} Progress: | {bar * done}{space * remaining } | {pc} % complete{period * (curr % num_periods)}", end = "\r")

    def convert_to_mahimahi_format(self, time_s, throughput_all, trace_file_name):
        with open(f"{trace_file_name}-mahimahi", 'w') as mf:
            millisec_time = 0
            mf.write(str(millisec_time) + '\n')

            for i in range(len(throughput_all)):

                throughput = throughput_all[i]  # in Mbits/s
                if i == len(throughput_all) - 1:
                    duration = END_DURATION
                else:
                    duration =  time_s[i+1] - time_s[i]  # in seconds
                if duration < 0:
                    print("measurement duration is negative")
                    return

                throughput = throughput * MEGABITS_PER_SECOND_TO_BYTES_PER_MS # in bytes / ms
                duration = duration * MS_IN_S # in milliseconds

                pkt_per_millisec = throughput / BYTES_PER_PKT 
                millisec_count = 0
                pkt_count = 0
                while True:
                    millisec_count += 1
                    millisec_time += 1
                    to_send = (millisec_count * pkt_per_millisec) - pkt_count
                    to_send = np.floor(to_send)
                    for i in range(int(to_send)):
                        mf.write(str(millisec_time) + '\n')
                    pkt_count += to_send
                    if millisec_count >= duration:
                        break
                #self.printProgress(i, len(throughput_all), trace_file_name)
            #print()

if __name__ == "__main__":
    start_thr = float(sys.argv[1])
    duration = int(sys.argv[2])
    change_times = sys.argv[3]
    change_times = [int(i) for i in list(change_times.split())]
    change_type = sys.argv[4]
    change_type = list(change_type.split())
    #print(f"change_type is: {change_type}")
    jitter = float(sys.argv[5])
    min_thr = float(sys.argv[6])
    max_thr = float(sys.argv[7])
    trace_name = sys.argv[8]
    variants = int(sys.argv[9])
    gen = Trace_Generator(min_thr, max_thr, padding=1, jitter_freq=100)
    
    time_ms_all, thr_all = gen.generate_trace(start_thr, duration, change_times, change_type, jitter, variants, trace_name)
    for i in range(len(time_ms_all)):
        time_ms = time_ms_all[i]
        thr = thr_all[i]
        time_sec, thr_sec = gen.convert_trace_to_seconds(time_ms, thr)
        gen.save_trace(time_sec, thr_sec, f"{trace_name}{i}-sec")
        gen.convert_to_mahimahi_format(time_sec, thr_sec, f"{trace_name}{i}-sec")

    #for i in range(len(time_ms)):
    #    print(f"{time_ms[i]} {thr[i]}")
    fig, ax = plt.subplots()
    ax.plot(time_sec, thr_sec)
    ax.set(xlabel="time (sec)", ylabel='link capacity (Mbps)', title=trace_name)
    ax.tick_params(axis='x',direction='out')
    ax.grid()
    fig.savefig(f"{trace_name}-sec.png")
    #plt.show()