#!/bin/bash -x
abrs=("RL")
traces="./compmon_debug_traces/"
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
        echo "./04_op_compmon.sh 4 44444 $abr $tracename"
        ./04_op_compmon.sh 4 44444 $abr $tracename
        #mv $trace $done_dir
        exit    
    done

done
