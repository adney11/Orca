import os
import sys
import random
from create_jitter import make_variants


STEPS = 5
MAX_THR = 30
MIN_THR = 6
VARIANTS = 4
DURATION = 320
MUTATION_FACTOR = 1

def main(version):
    lines = []
    lines.append([0, MIN_THR])
    x_step = DURATION/STEPS
    prev_t = 0
    for s in range(STEPS):
        thr = random.uniform(MIN_THR, MAX_THR)
        lines.append([prev_t + x_step, thr])
        prev_t = prev_t + x_step

    normal_lines = []
    print(lines)
    for i in range(len(lines) - 1):
        for t in range(int(lines[i][0]), int(lines[i+1][0])):
            normal_lines.append([t, lines[i][1]])
    normal_lines.append([lines[-1][0], lines[-1][1]])
    with open(f'normal_unstable_trace{version}', 'w') as nf:
        for line in normal_lines:
            nf.write(f"{line[0]} {line[1]}\n")
    make_variants(normal_lines, f'normal_unstable_trace{version}',VARIANTS, MUTATION_FACTOR)
if __name__ == "__main__":
    version = int(sys.argv[1])
    main(version)