import os
import numpy as np

import logging
import math
import json
import sys

FILE_PATH = '../cooked_test_traces/'
OUTPUT_PATH = './mahimahi_test_traces/'
BYTES_PER_PKT = 1500.0
MILLISEC_IN_SEC = 1000.0
BITS_IN_BYTE = 8.0
BYTES_IN_MEGABYTES = 1000.0
MEGABITS_PER_SECOND_TO_BYTES_PER_MS = 125.0

logging.basicConfig()
logging.basicConfig(filename='logs/generate_trace.log', level=logging.DEBUG)
LOG = logging.getLogger(__name__)


def printProgress(curr, total):
	bar = '#'
	space = '-'
	period = '.'
	num_periods = 3
	progress_bar_length = 50
	done = math.ceil((curr / total) * progress_bar_length)
	pc = math.ceil((curr / total) * 100)
	remaining = progress_bar_length - done
	print(f"\r Progress: | {bar * done}{space * remaining } | {pc} % complete{period * (curr % num_periods)}", end = "\r")

def convert_to_mahimahi(tp, duration, millisec_time, mf):
    if duration < 0:
        LOG.error("measurement duration is negative")
        sys.exit()
                    
    tp = tp * MEGABITS_PER_SECOND_TO_BYTES_PER_MS
    duration = duration * MILLISEC_IN_SEC

    pkt_per_millisec = tp / BYTES_PER_PKT
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
    return millisec_time



def main():
    with open('trace.input', 'r') as input:
        data = input.read()
        data = json.loads(data)
        for idx, trace in data.items():
            print(trace)
            tracename = trace["trace_name"]
            with open(trace["trace_name"], "w") as mf, open('normal_'+tracename, 'w') as nf:
                time_sec = np.array(trace["time_sec"])
                throughput_all = np.array(trace["throughput"])

                millisec_time = 0
                mf.write(str(millisec_time) + '\n')

                for i in range(len(throughput_all) - 1):

                    throughput = throughput_all[i]  # in Mbits/s
                    duration =  time_sec[i+1] - time_sec[i]  # in seconds
                    millisec_time = convert_to_mahimahi(throughput,duration,millisec_time,mf)

                    for t in range(time_sec[i], time_sec[i+1]):
                        nf.write(str(t) + " " + str(throughput_all[i]) + "\n")

                    printProgress(i, len(throughput_all) - 1)
                tp = throughput_all[-1]
                duration = time_sec[-1] - time_sec[-2]
                millisec_time = convert_to_mahimahi(tp, duration, millisec_time, mf)
                nf.write(str(time_sec[-1]) + " " + str(throughput_all[-1]) + "\n")
                LOG.debug(f'converted {trace["trace_name"]}')
                print(f'converted {trace["trace_name"]}')

if __name__ == '__main__':
	main()
