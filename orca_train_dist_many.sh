#!/bin/bash -x

for start_idx in `seq 300 60 540`
do
    echo "[$0]: ./orca_train_dist.sh 2 44444 $start_idx"
    ./orca_train_dist.sh 2 44444 $start_idx
    echo "[$0]: sleeping for 60 seconds"
    sleep 60
done
