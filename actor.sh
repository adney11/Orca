#!/bin/bash -x
if [ $# != 14 ]
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

abr_algo=${14}

echo "[$0]: Running orca-$scheme: $down"
echo "[$0]: orca_binary is: $orca_binary"
echo "[$0]: full path is: $path/$orca_binary"
#exit

trace=""
scheme_des="orca-$scheme-$latency-$period-$qsize"
log="orca-$scheme-$down-$up-$latency-${period}-$qsize-$abr_algo"

#Bring up the actor i:
echo "[$0]: will be done in $finish_time seconds ..."
echo "[$0]: $path/$orca_binary $port $path ${period} ${first_time} $scheme $id $down $up $latency $log $finish_time $qsize $max_it $abr_algo"

echo "[$0]: sleeping in hopes that learner is ready"

echo "[$0]: slept, now calling actor stuff"
echo "[$0]: $path/$orca_binary $port $path ${period} ${first_time} $scheme $id $down $up $latency $log $finish_time $qsize $max_it $abr_algo"
$path/$orca_binary $port $path ${period} ${first_time} $scheme $id $down $up $latency $log $finish_time $qsize $max_it $abr_algo
echo "[$0]: finished running $orca_binary" 
sudo killall -s15 python $orca_binary Xvfb chrome chromedriver
sleep 10
echo "[$0]: Finished."
if [ ${first_time} -eq 2 ] || [ ${first_time} -eq 4 ]
then
    echo "[$0]: Doing Some Analysis ..."
    echo "[$0]: path: $path"
    out="sum-${log}.tr"
    echo "[$0]: out: $out"
    sudo echo $log >> $path/log/$out
    sudo perl $path/mm-thr 500 $path/log/down-${log} 1>$path/plots/plot-${log}.svg 2>res_tmp
    sudo cat res_tmp >>$path/log/$out
    sudo echo "------------------------------" >> $path/log/$out
    rm *tmp
fi
echo "[$0]: Done"

