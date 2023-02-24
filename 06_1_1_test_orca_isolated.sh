#!/bin/bash 


# TODO: Can change this to spawn multiple actors, to reduce testing time.

source setup.sh

trace_id=$1
port_base=$2
abr_algo=$3
trace_basename=$4
orcadir=$5
trace_postfix="-mahimahi"

cur_dir=`pwd -P`
scheme_="cubic"
max_steps=50000         #Run untill you collect 50k samples per actor
eval_duration=320
num_actors=1
memory_size=$((max_steps*num_actors))
dir="${cur_dir}/${orca_dir}"
echo "[$0]: dir is: $dir"
#exit
orca_binary="orca-server-mahimahi"
echo "[$0]: orca_binary is: $orca_binary"


UPLINK_TRACE="wired6"
QUEUE_SIZE=30                                 # in number of packets
DELAY=80                                      # in ms
TRAINING_DURATION=600

#sudo killall -s9 python orca-server-mahimahi

epoch=20
act_id=${trace_id}
act_port=$((port_base+act_id))



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

echo "sleeping 10, and then cleaning"
sleep 10
#sudo killall -s15 python orca-server-mahimahi-http client



# make seperate directory for softmax distribution and action, confidence files
smax_dir="${dir}/smax_distributions"
if [ ! -f $smax_dir ];
then
    mkdir $smax_dir
fi

action_conf_dir = "${dir}/action_conf_pairs"
if [ ! -f $action_conf_dir ];
then
    mkdir $action_conf_dir
fi

mv "$dir/logs/ood-$actor_id.log" "$action_conf_dir/$trace_basename-$trace_id"
mv "$dir/logs/softmax_values_actor-$actor_id.log" "$smax_dir/$trace_basename-$trace_id"
#rm "$dir/logs/*"
echo "[$0]: Done"