#!/bin/bash -x

#traces="./compmon_debug_traces/"

do_test() {
    done_dir="${traces:0:$((len-1))}_done/"
    #echo "$done_dir"
    if [ ! -d $done_dir ]
    then
        mkdir $done_dir
    fi  

    data_dir="${traces:0:$((len-1))}_data/"
    if [ ! -d $data_dir ]
    then
        mkdir $data_dir
    fi  

    for abr in ${abrs[@]}
    do
        for trace in $traces*
        do
            tracename=$(basename $trace)
            echo "./03_orca-pensieve.sh 1 44444 $abr $tracename"
            ./03_orca-pensieve.sh 1 44444 $abr $tracename
            mv ./orca_pensieve/logs/actions.log ./orca_pensieve/data/$tracename-actions.data
            mv $trace $done_dir
        done

    done
    mv ./orca_pensieve/data/* $data_dir
    echo "[$0]: Done Test for $traces"
}

abrs=("RL")
#traces="./6to12mbps_test_mahimahi/"
#do_test


#traces="./below6mbps_test_mahimahi/"
#do_test

traces="./compmon_debug_traces/"
do_test