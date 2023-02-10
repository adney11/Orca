#!/bin/bash -x

# This will be called from inside another script to start a batch of actors on
# this node (Avoids multiple ssh for each actor)


num_actors=$1
port_base=$2
epoch=$3
first_time=$4
scheme_=$5
dir=$6
trace_basename=$7
uplink=$8
del=$9
training_duration=$10
qs=$11

max_steps=$12
orca_binary=$13
abr_algo=$14
actor_id_start=$15

trace_postfix="-mahimahi"

cur_dir=`pwd -P`


remote_output_dir="${dir}/remote_output_logs"
if [ ! -f $remote_output_dir ];
then
    mkdir $remote_output_dir
fi

echo "start $num_actors actors"
act_port=$port_base
for i in `seq 0 $((num_actors-1))`
do
    act_id=$((actor_id_start+i))
    downl="$trace_basename-$act_id$trace_postfix"
    echo "starting actor $act_id with port $act_port on trace $downl"
    echo "./actor.sh ${act_port} $epoch ${first_time} $scheme_ $dir $act_id $downl $upl $del $training_duration $qs $max_steps $orca_binary $abr_algo >> $remote_output_dir/\"actor-$act_id.out\" &"
    ./actor.sh ${act_port} $epoch ${first_time} $scheme_ $dir $act_id $downl $upl $del $training_duration $qs $max_steps $orca_binary $abr_algo >> $remote_output_dir/"actor-$act_id.out" &
    pids="$pids $!"
    act_port=$((act_port+1))
done

for pid in $pids
do
    echo "[$0]: waiting for $pid"
    wait $pid
done

# done
