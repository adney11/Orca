#!/bin/bash -x
if [ $# -eq 4 ]
then
    source setup.sh

    first_time=$1
    port_base=$2

    abr_algo=$3
   
    trace_name=$4

    cur_dir=`pwd -P`
    scheme_="cubic"
    max_steps=500000         #Run untill you collect 50k samples per actor
    eval_duration=200
    num_actors=1
    memory_size=$((max_steps*num_actors))
    dir="${cur_dir}/orca_pensieve"
    echo "[$0]: dir is: $dir"
    #exit
    orca_binary="orca-server-mahimahi-http"
    echo "[$0]: orca_binary is: $orca_binary"
    
    DOWNLINK_TRACE=$trace_name
    
    UPLINK_TRACE="wired6"
    QUEUE_SIZE=30                                 # in number of packets
    DELAY=10                                      # in ms
    TRAINING_DURATION=600



    #sed "s/\"num_actors\"\: 1/\"num_actors\"\: $num_actors/" $cur_dir/params_base.json > "${dir}/params.json"
    #sed -i "s/\"memsize\"\: 5320000/\"memsize\"\: $memory_size/" "${dir}/params.json"
    sudo killall -s9 python orca-server-mahimahi-http

    epoch=20
    act_port=$port_base

    if [ $1 -eq 4 ]
    then

        # If you are here: You are going to perform an evaluation over an emulated link
        num_actors=1
        #sed "s/\"num_actors\"\: 1/\"num_actors\"\: $num_actors/" $cur_dir/params_base.json > "${dir}/params.json"

        #echo "[$0]: ./learner.sh  $dir $first_time  &"
        ./learner.sh  $dir ${first_time} &
        #echo "sleeping 20 seconds"
        sleep 20
        echo "[$0]: bringing up actor"
        #Bring up the actors:
        #act_id=$(($RANDOM % 5))
        #echo "act_id is: $act_id"
        act_id=0
        downl=$DOWNLINK_TRACE
        upl=$UPLINK_TRACE
        del=$DELAY
        qs=$QUEUE_SIZE
        echo "./actor.sh ${act_port} $epoch ${first_time} $scheme_ $dir $act_id $downl $upl $del $eval_duration $qs 0 $orca_binary $abr_algo &"
        ./actor.sh ${act_port} $epoch ${first_time} $scheme_ $dir $act_id $downl $upl $del $eval_duration $qs 0 $orca_binary $abr_algo & # add abr_algo here
        pids="$pids $!"
        #act_id=$((act_id+1))
        #act_port=$((port_base+act_id))
        sleep 2

        #SECONDS=20
        for pid in $pids
        do
            echo "[$0]: waiting for $pid"
            wait $pid
        done
        #Bring down the learner and actors ...
        #echo "sleeping for 315 seconds before killing actors and learner"
        sleep 20
        echo "[$0]: waited for 20 seconds.."
        echo "killing actors and learner"
        for i in `seq 0 $((num_actors))`
        do
            sudo killall -s15 orca-server-mahimahi-http
            sudo killall -s15 python
            sudo killall chromedriver
            sudo killall chrome
            sudo killall Xvfb
        done
    else
    # If you are here: You are going to start/continue learning a better model!
        echo "[$0]: WARNING: Proceed with caution - buggy code ahead"
      #Bring up the learner:
      echo "[$0]: ./learner.sh  $dir $first_time &"
      if [ $1 -eq 1 ];
      then
          # Start the learning from the scratch
           /users/`logname`/venv/bin/python ${dir}/d5.py --job_name=learner --task=0 --base_path=${dir} &
           lpid=$!
       else
          # Continue the learning on top of previous model
           /users/`logname`/venv/bin/python ${dir}/d5.py --job_name=learner --task=0 --base_path=${dir} --load &
           lpid=$!
       fi
       sleep 20
       echo "calling actors"

        echo "[$0]: REMINDER: Training Orca Pensieve with multiple actors not debugged yet..."
        echo "[$0]: REMINDER: This training session will be with one actor!"
       #Bring up the actors:
       # Here, we go with single actor
        act_id=0
     
        downl=$DOWNLINK_TRACE
        upl=$UPLINK_TRACE
        qs=$QUEUE_SIZE
        del=$DELAY

        echo "[$0]: ./actor.sh ${act_port} $epoch ${first_time} $scheme_ $dir $act_id $downl $upl $del 0 $qs $max_steps $orca_binary"
        ./actor.sh ${act_port} $epoch ${first_time} $scheme_ $dir $act_id $downl $upl $del 0 $qs $max_steps $orca_binary
        pids="$pids $!"
        echo "[$0]: initialised actor with pid: $!"
        act_id=$((act_id+1))
        act_port=$((port_base+act_id))
        sleep 5
       

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
        for i in `seq 0 $((num_actors))`
       do
           sudo killall -s15 python
           sudo killall -s15 orca-server-mahimahi-http
       done
    fi
else
    echo "usage: $0 [{Learning from scratch=1} {Continue your learning=0} {Just Do Evaluation=4}] [base port number ] [abr_algo]"
fi

