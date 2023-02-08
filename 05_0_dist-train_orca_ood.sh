#!/bin/bash -x
if [ $# -eq 4 ]

    source setup.sh

    # Command Line Arguments
    first_time=$1
    load_traces=$2
    trace_dir=$3
    port_base=44444
    abr_algo='RL'
    
    remote_nodes=("cl0" "cl1") # make sure your config file has these set up
    
    
    trace_name="${trace_dir:0:-1}"
    trace_postfix="-mahimahi"

    cur_dir=`pwd -P`
    scheme_="cubic"
    max_steps=500000         #Run untill you collect 50k samples per actor
    eval_duration=320
    num_actors=2
    num_actors_per_node=1
    memory_size=$((max_steps*num_actors))
    dir="${cur_dir}/orca_ood"
    echo "[$0]: dir is: $dir"
    #exit
    orca_binary="orca-server-mahimahi"
    echo "[$0]: orca_binary is: $orca_binary"
    
    DOWNLINK_TRACE=$trace_name
    UPLINK_TRACE="wired6"
    QUEUE_SIZE=30                                 # in number of packets
    DELAY=10                                      # in ms
    TRAINING_DURATION=600



    #sed "s/\"num_actors\"\: 1/\"num_actors\"\: $num_actors/" $cur_dir/params_base.json > "${dir}/params.json"
    #sed -i "s/\"memsize\"\: 5320000/\"memsize\"\: $memory_size/" "${dir}/params.json"
    sed -i "s/\"memsize\": [[:digit:]]\+,/\"memsize\": $memory_size,/" "${dir}/params.json"
    sudo killall -s9 python orca-server-mahimahi-http

    epoch=20
    act_port=$port_base
     
  

    # Send all traces to all the remotes if load_traces = 1
    if [ $2 -eq 1 ]:
    then
        for node in ${remote_nodes[@]}
        do
            rsync -avz -e ssh $trace_dir $node:/newhome/Orca/traces/
        done
        echo "loaded traces on remote servers"
    fi
    
    #Bring up the learner:
    echo "[$0]: ./learner.sh  $dir $first_time &"
    if [ $1 -eq 1 ];
    then
        # Start the learning from the scratch
         /users/`logname`/venv/bin/python ${dir}/d5.py --job_name=learner --task=0 --base_path=${dir} &
         lpid=$!
    else if [ $1 -eq 2 ];
    then
        # Continue the learning on top of previous model
        /users/`logname`/venv/bin/python ${dir}/d5.py --job_name=learner --task=0 --base_path=${dir} --load &
        lpid=$!
    fi
    sleep 20
    echo "starting actors on remote machines"
    #Bring up the actors:
    act_id=0
    curr_node_idx=0
    act_port=$port_base
    for i in `seq 0 $((num_actors-1))`
    do
        node=${remote_nodes[$curr_node_idx]}
        downl="$trace_name-$i$trace_postfix"
        upl=$UPLINK_TRACE
        qs=$QUEUE_SIZE
        del=$DELAY


        echo "starting actor $actor_id ($i) on $node ($curr_node_idx)"
        ssh $node "bash -c 'cd /newhome/Orca/; nohup ./actor.sh ${act_port} $epoch ${first_time} $scheme_ $dir $act_id $downl $upl $del 0 $qs $max_steps $orca_binary $abr_algo'" &
        pids="$pids $!"
        act_id=$((act_id+1))
        act_port=$((act_port+1))
        if [ $act_id%$num_actors_per_node -eq 0 ];
        then
            curr_node_idx=$((curr_node_idx+1))
            act_id=0
            act_port=$port_base
        fi

    done

    for pid in $pids
    do
        echo "[$0]:  waiting for $pid"
        wait $pid
    done

    #Kill the learner
    sudo kill -s15 $lpid

    #Wait if it needs to save somthing!
    sleep 30

    #Make sure all are down ...
    sudo killall -s15 python # for learner
    for node in ${remote_nodes[@]}
    do
        ssh $node "bash -c 'sudo killall -s15 python orca-server-mahimahi'"
    done
else
    echo "usage: $0 [{Learning from scratch=1} {Continue your learning=0} {Just Do Evaluation=4}] [base port number ] [abr_algo]"
fi

