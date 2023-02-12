#!/bin/bash 

source setup.sh

trace_id=$1
port_base=$2
abr_algo=$3
trace_basename=$4
trace_postfix="-mahimahi"

cur_dir=`pwd -P`
scheme_="cubic"
max_steps=500000         #Run untill you collect 50k samples per actor
eval_duration=320
num_actors=1
memory_size=$((max_steps*num_actors))
dir="${cur_dir}/orca_ood"
echo "[$0]: dir is: $dir"
#exit
orca_binary="orca-server-mahimahi-http"
echo "[$0]: orca_binary is: $orca_binary"

DOWNLINK_TRACE=$trace_name

UPLINK_TRACE="wired6"
QUEUE_SIZE=30                                 # in number of packets
DELAY=10                                      # in ms
TRAINING_DURATION=600

sudo killall -s9 python orca-server-mahimahi-http

epoch=20
act_id=0
act_port=$port_base

echo "setting single_actor_eval to true"
sed -i "s/\"single_actor_eval\": false,/\"single_actor_eval\": true,/" "$dir/params.json"

downl="$trace_basename-$trace_id$trace_postfix"
upl=$UPLINK_TRACE
del=$DELAY
qs=$QUEUE_SIZE
training_duration=$TRAINING_DURATION

first_time=4

echo "./actor.sh ${act_port} $epoch ${first_time} $scheme_ $dir $act_id $downl $upl $del $eval_duration $qs 0 $orca_binary $abr_algo &"
./actor.sh ${act_port} $epoch ${first_time} $scheme_ $dir $act_id $downl $upl $del $eval_duration $qs 0 $orca_binary $abr_algo &
pids="$pids $!"

for pid in $pids
do
    echo "waiting for $pid"
    wait $pid
done

echo "sleeping 30, and then cleaning"
sleep 10
sudo killall -s15 python orca-server-mahimahi-http client

sed -i "s/\"single_actor_eval\": true,/\"single_actor_eval\": false,/" "$dir/params.json"
echo "Done"