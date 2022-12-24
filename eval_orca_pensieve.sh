#!/bin/bash
abrs=("RL")
traces=$1
donelog="./"


for abr in ${abrs[@]}
do
    for trace in $traces*
    do
        tracename=$(basename $trace)
        echo "./03_orca_pensieve.sh 4 44444 $abr $tracename"
        ./03_orca-pensieve.sh 4 44444 $abr $tracename
        mv $trace /newhome/Orca/fcc_traces_done/
        sleep 10
    done

done
