#!/bin/bash

# Please check 06_1_1_test_orca_isolated.sh for proper DELAY, QUEUE_SIZE, UPLINK_TRACE parameters.

start_trace_id=0
max_trace_id=99
trace_basename='below6mbps_test'
port=44444
abr_algo='None'
orcadir="bucket_orca"

cur_dir=`pwd -P`
dir="$cur_dir/${orcadir}"

echo "setting single_actor_eval to true"
sed -i "s/\"single_actor_eval\": false,/\"single_actor_eval\": true,/" "$dir/params.json"

for trace_id in `seq $start_trace_id $max_trace_id`
do
    ./06_1_1_test_orca_isolated.sh $trace_id $port $abr_algo $trace_basename $orcadir &
    pids="$pids $!"
    sleep 2
done

for pid in $pids
do
    wait $pid
done

sleep 10

sudo killall -s15 python orca-server-mahimahi client

echo "setting single_actor_eval to false"
sed -i "s/\"single_actor_eval\": true,/\"single_actor_eval\": false,/" "$dir/params.json"