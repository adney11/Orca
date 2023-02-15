#!/bin/bash -x
if [ $# -eq 4 ]
then

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
    num_actors=60
    num_actors_per_node=30
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
    TRAINING_DURATION=0



    #sed "s/\"num_actors\"\: 1/\"num_actors\"\: $num_actors/" $cur_dir/params_base.json > "${dir}/params.json"
    #sed -i "s/\"memsize\"\: 5320000/\"memsize\"\: $memory_size/" "${dir}/params.json"
    sed -i "s/\"num_actors\": [[:digit:]]\+,/\"num_actors\": $num_actors,/" "${dir}/params.json"
    sed -i "s/\"memsize\": [[:digit:]]\+,/\"memsize\": $memory_size,/" "${dir}/params.json"
    
    sudo killall -s9 python orca-server-mahimahi-http

    epoch=20
    act_port=$port_base
     
    remote_output_dir="${dir}/remote_output_logs"
    if [ ! -f $remote_output_dir ];
    then
        mkdir $remote_output_dir
    fi

    # Send all traces to all the remotes if load_traces = 1
    if [ $2 -eq 1 ];
    then
        for node in ${remote_nodes[@]}
        do
            rsync -avz -e ssh $trace_dir $node:/newhome/Orca/traces/
        done
        echo "loaded traces on remote servers"
    fi

    # Send the most recent model files to remote servers
    if [ $1 -eq 2 ];
    then
        # find checkpoint file
        checkpoint_file="${dir}/train_dir/learner0/checkpoint"
        if [ ! -f $checkpoint_file ]
        then
            echo "checkpoint doesn't exist - pls check"
            exit
        fi
        modelname=$(head -n 1 $checkpoint_file | awk -F ' ' '{print $2}' | sed -e 's/^"//' -e 's/"$//')
        echo "got: $modelname"
        # required files
        modeldata="${modelname}.data-00000-of-00001"
        modelindex="${modelname}.index"
        modelmeta="${modelname}.meta"
        if [ ! -f $modeldata ]; 
        then
            echo "couldn't locate the data file: $modeldata"
            exit
        fi
        if [ ! -f $modelindex ]; 
        then
            echo "couldn't locate the index file: $modelindex"
            exit
        fi
        if [ ! -f $modelmeta ]; 
        then
            echo "couldn't locate the meta file: $modelmeta"
            exit
        fi

        for node in ${remote_nodes[@]}
        do
            rsync -avz -e ssh $modeldata $modelindex $modelmeta $checkpoint_file $node:$dir/train_dir/learner0/
        done
        echo "uploaded model to remote servers"
    fi

    # upload most recent params.json
    for node in ${remote_nodes[@]}
    do
        rsync -avz -e ssh "${dir}/params.json" $node:$dir/
    done
    
    #Bring up the learner:
    echo "[$0]: ./learner.sh  $dir $first_time &"
    if [ $1 -eq 1 ];
    then
        # Start the learning from the scratch
         /users/`logname`/venv/bin/python ${dir}/d5.py --job_name=learner --task=0 --base_path=${dir} &
         lpid=$!
    elif [ $1 -eq 2 ];
    then
        # Continue the learning on top of previous model
        /users/`logname`/venv/bin/python ${dir}/d5.py --job_name=learner --task=0 --base_path=${dir} --load &
        lpid=$!
    fi
    sleep 10
    echo "starting actors on remote machines"
    #Bring up the actors:
    act_id=0
    curr_node_idx=0
    act_port=$port_base
    for node in ${remote_nodes[@]}
    do
        upl=$UPLINK_TRACE
        qs=$QUEUE_SIZE
        del=$DELAY

        echo "starting actors $act_id - $((act_id+num_actors_per_node)) on $node"
        echo "ssh $node \"bash -c 'cd /newhome/Orca/; nohup ./05_1_start_batch_of_actors.sh ${num_actors_per_node} ${port_base} $epoch ${first_time} $scheme_ $dir $trace_name $upl $del $TRAINING_DURATION $qs $max_steps $orca_binary $abr_algo $act_id'\" >> $remote_output_dir/\"node-$node.out\" &"
        ssh $node "bash -c 'cd /newhome/Orca/; nohup ./05_1_start_batch_of_actors.sh ${num_actors_per_node} ${port_base} $epoch ${first_time} $scheme_ $dir $trace_name $upl $del $TRAINING_DURATION $qs $max_steps $orca_binary $abr_algo $act_id'" >> $remote_output_dir/"node-$node.out" &
        pids="$pids $!"
        act_id=$((act_id+num_actors_per_node))
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
        ssh $node "bash -c 'cd /newhome/Orca; nohup ./clean_shmem.sh'"
    done
else
    echo "usage: $0 [{Learning from scratch=1} {Continue your learning=0} {Just Do Evaluation=4}] [base port number ] [abr_algo]"
fi

