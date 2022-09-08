#!/bin/bash


s=$1
for e in `seq 900 999`; 
do    
    echo "./03_orca-pensieve.sh 4 44444 $s $e"
    ./03_orca-pensieve.sh 4 44444 $s $e
    sleep 10
    done
done
