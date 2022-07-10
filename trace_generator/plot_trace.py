import matplotlib.pyplot as plt
import numpy as np
import json
import os
import sys
import math


with open('traces.list', 'r') as input:
        data = input.read()
        data = json.loads(data)
        for idx, trace in data.items():
            tracename = trace["trace_name"]
            traces = trace["traces"]
            #normaltrace = 'normal_'+ tracename
            #realtrace = normaltrace + '_real'
            columns = 2
            rows = math.ceil(len(traces) / columns)
            fig, axs = plt.subplots(rows, columns, figsize=(12, 8), squeeze=False)
            #print(f"rows: {rows}, columns: {columns}")
            r, c = 0, 0
            for t in traces:
                with open(t, 'r') as tf:
                    #print("opening file:", t)
                    nfx = []
                    nfy = []
                    for line in tf:
                        parsed = line.split()
                        nfx.append(float(parsed[0]))
                        nfy.append(float(parsed[1]))
                    #print(nfx, nfy)
                    #print(f"r: {r}, c: {c}")
                    axs[r, c].plot(nfx, nfy, 'r-')
                    axs[r, c].set_title(t)
                    
                c += 1
                if c == columns:
                    c = 0
                    r += 1
                        
            for ax in axs.flat:
                ax.set(xlabel="time (sec)", ylabel="throughput (Mbps)")
            fig.tight_layout()
            fig.savefig(tracename+'-plot.png')

