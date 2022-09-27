#!/bin/bash -x

for start_idx in `seq 20 20 580`
do
    echo "current orcapensieve train position: $start_idx" >> "orcapensieve_w_coord_train_progess.log"
    echo "[$0]: ./orca_train_dist.sh 2 44444 $start_idx"
    ./orcapensieve_w_coord_train_dist.sh 2 44444 $start_idx
    echo "[$0]: sleeping for 30 seconds to give rest"
    sleep 30
done
