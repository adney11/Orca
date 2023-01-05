#!/bin/bash
abrs=("RL")
traces=$1
donelog="./"


done_dir="${traces:0:$((len-1))}_done/"
#echo "$done_dir"
if [ ! -d $done_dir ]
then
    mkdir $done_dir
fi  

for abr in ${abrs[@]}
do
    for trace in $traces*
    do
        tracename=$(basename $trace)
        echo "./03_orca_pensieve.sh 4 44444 $abr $tracename"
        ./03_orca-pensieve.sh 4 44444 $abr $tracename
        mv $trace $done_dir
        sleep 10
    done

done
