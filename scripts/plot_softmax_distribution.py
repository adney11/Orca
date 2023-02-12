import os
import sys
import re

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme()
PLOTS_DIR = "../custom_plots"

def plot_softmax_distribution(softmax_files):
    # expects a list of tuples, of filepath, name
    file_data = []
    file_names = []
    for filepath, name in softmax_files:
        with open(filepath, 'r') as f:
            values = [float(v.strip()) for v in f.readlines()]
            # print(values)
            file_data.append(values)
            file_names.append(name)
    
    fig = plt.figure(figsize=(12,8))
    ax = fig.add_subplot()
    
    kwargs = dict(alpha=0.5, bins=100)
    
    for data, name in zip(file_data, file_names):
        ax.hist(data, **kwargs, label=name)
        
    ax.set_xlabel("softmax value (confidence percentage)")
    ax.set_ylabel("frequency ")
    ax.legend()
    
    unique = input("Enter title for plot: ")
    savefilename = f"softmax_distribution - {unique}"
    ax.set_title(savefilename)
    plt.savefig(f"{PLOTS_DIR}/{savefilename}.png")
    plt.clf()
    
    
def prep_plots_dir():
    if not os.path.exists(PLOTS_DIR):
        os.mkdir(PLOTS_DIR)

def main():
    softmax_files = []
    for i, val in enumerate(sys.argv):
        if i == 0:
            continue
        path = sys.argv[i]
        name = re.findall(r'actor-\d+', path)[0]
        softmax_files.append((path, name))
    #print(softmax_files)
    prep_plots_dir()
    plot_softmax_distribution(softmax_files)

if __name__ == "__main__":
    main()