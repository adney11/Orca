#!/bin/bash

# Please check 06_2_1_test_orca_pensieve.sh for proper DELAY, QUEUE_SIZE, UPLINK_TRACE parameters.

start_trace_id=0
max_trace_id=99
trace_basename='6to12mbps_test'
port=44444
abr_algo='RL'

orcadir='bucket_orca'

for trace_id in `seq $start_trace_id $max_trace_id`
do
    ./06_2_1_test_orca_pensieve.sh $trace_id $port $abr_algo $trace_basename $orca_dir
done