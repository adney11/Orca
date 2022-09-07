import matplotlib.pyplot as plt
import numpy as np
import json
import os
import sys
import math


trace_dir = sys.argv[1]

r, c = 0, 0
for trace in os.listdir(trace_dir):
    with open(os.path.join(trace_dir, trace), 'r') as tf:
        #print("opening file:", t)
        nfx = []
        nfy = []
        for line in tf:
            parsed = line.split()
            nfx.append(float(parsed[0]))
            nfy.append(float(parsed[1]))
        #print(nfx, nfy)
        #print(f"r: {r}, c: {c}")
        plt.clf()
        plt.plot(nfx, nfy, 'r-')
        plt.title(trace)
        plt.xlabel("time (sec)") 
        plt.ylabel=("throughput (Mbps)")
        plt.savefig(trace_dir +"/../plots/" + trace + '-plot.png')

