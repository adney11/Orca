max_trace_id=99
trace_basename='6to12mbps_test'
port=44444
abr_algo='RL'

for trace_id in `seq 0 $max_trace_id`
do
    ./05_2_test_orca_ood.sh $trace_id $port $abr_algo $trace_basename
done