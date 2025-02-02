#!/bin/bash -x
if [ $# != 13 ]
then
    echo -e "usage:$0 port period first_time [underlying scheme:cubic , vegas , westwood , illinois , bbr, yeah , veno, scal , htcp , cdg , hybla ,... ] [path to ddpg.py] [actor id] [downlink] [uplink] [one-way link delay] [time time] [Qsize] [Max iterations per run]"
    exit
fi

port=$1
period=$2
first_time=$3
x=100
scheme=$4
path=$5
id=$6
down=$7
up=$8
latency=$9
finish_time=${10}
qsize=${11}
max_it=${12}
orca_binary=${13}

echo "[$0]: Running orca-$scheme: $down"
echo "[$0]: orca_binary is: $orca_binary"
echo "[$0]: full path is: $path/$orca_binary"
#exit

trace=""
scheme_des="orca-$scheme-$latency-$period-$qsize"
log="orca-$scheme-$down-$up-$latency-${period}-$qsize"

#Bring up the actor i:
echo "[$0]: will be done in $finish_time seconds ..."
echo "[$0]: $path/$orca_binary $port $path ${period} ${first_time} $scheme $id $down $up $latency $log $finish_time $qsize $max_it"

$path/$orca_binary $port $path ${period} ${first_time} $scheme $id $down $up $latency $log $finish_time $qsize $max_it
echo "[$0]: finished running $orca_binary" 
#sudo killall -s15 python
#sleep 10
echo "[$0]: Finished."
if [ ${first_time} -eq 2 ] || [ ${first_time} -eq 4 ]
then
    echo "Doing Some Analysis ..."
    echo "path: $path"
    out="sum-${log}.tr"
    echo "out: $out"
    sudo echo $log >> $path/log/$out
    sudo perl $path/mm-thr 500 $path/log/down-${log} 1>$path/plots/plot-${log}.svg 2>res_tmp
    sudo cat res_tmp >>$path/log/$out
    sudo echo "------------------------------" >> $path/log/$out
    rm *tmp
fi
echo "Done"

