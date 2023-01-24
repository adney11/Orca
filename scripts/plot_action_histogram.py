import sys
import os

import matplotlib.pyplot as plt


NUM_BINS = 500

def usage():
    print("plot_action_histogram.py <path to file with actions>")

def main():
    if len(sys.argv) < 2:
        usage()
        sys.exit(1)
    file = sys.argv[1]    
    filename = os.path.basename(file)
    with open(file, 'r') as f:
        lines = f.read().splitlines()
        try:
            data = [float(l.strip('][')) for l in lines]
        except:
            raise("Couldn't make float")
        print(f"data: {data}\nlen: {len(data)}")
    fig = plt.figure()
    ax = fig.add_subplot(111)      
    ax.hist(data, NUM_BINS)
    ax.set_title(f'{filename[:-5]} - distribution')
    ax.set_xlabel("Action value")
    ax.set_ylabel("Count")
    plt.savefig(f"/newhome/Orca/scripts/plots/{filename[:-5]}-distribution.png")
    plt.close()

if __name__ == "__main__":
    main()