#!/bin/bash
# 902
toeval=(906 907 908 909 911 913 914)
schemes=("BB" "RB" "BOLA" "fastMPC" "robustMPC" "RL")
for e in ${toeval[@]}; do
    for s in ${schemes[@]}; do
    if [$e == 906]; then
        if [$s == "BB"] || [$s == "BOLA"] || [$s == "fastMPC"] || [$s == "RB"]; then
            echo "skipping $s $e"
            continue
        fi
    fi
    echo "./03_orca-pensieve.sh 4 44444 $s $e"
    ./03_orca-pensieve.sh 4 44444 $s $e
    sleep 10
    done
done
