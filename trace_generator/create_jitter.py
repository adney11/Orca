import sys
import os
import random



def make_variants(lines, tracefile, variant, scalar_mutation_factor):
    for v in range(variant):
        mutated_file_name=f"{tracefile}_real_{v}"
        with open(mutated_file_name, 'w') as mf:
            for data in lines:
                mutated = float(data[1]) + random.uniform(-scalar_mutation_factor, scalar_mutation_factor)
                if float(data[1]) == 0:
                    mutated = float(data[1])
                print(f"Initial: {data[1]} -> mutated: {mutated}")
                mf.write(f"{data[0]} {mutated}\n")

def main():
    # take normal trace file (secoonds, throughput)
    tracefile=sys.argv[1] # normal trace file - <sec mbps> format


    scalar_mutation_factor = float(sys.argv[2])  # change value x to (x-this, x+this)
    num_variants = int(sys.argv[3]) # how many mutations

    
    with open(tracefile, 'r') as tf:
        data = []
        for line in tf:
            print(line)
            linedata=line.split()
            print(linedata)
            data.append(linedata)
        make_variants(data, tracefile, num_variants, scalar_mutation_factor)

if __name__ == "__main__":
    main()