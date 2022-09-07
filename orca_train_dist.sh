if [ $# -eq 3 ]
then
    source setup.sh

    first_time=$1
    port_base=$2
    cur_dir=`pwd -P`
    scheme_="cubic"
    max_steps=500000         #Run untill you collect 50k samples per actor
    eval_duration=30
    num_actors=59
    memory_size=$((max_steps*num_actors))
    dir="${cur_dir}/rl-module"
    echo "[$0]: dir is: $dir"
    orca_binary="orca-server-mahimahi"
    echo "[$0]: orca_binary is: $orca_binary"

    time_start=$(date +%s)

    trace_name_prefix="low3mbps"
    trace_name_postfix="-sec-mahimahi"
    trace_start_idx=$3
    trace_name="$trace_name_prefix$trace_start_idx$trace_name_postfix"
    echo "[$0]: trace_name: $trace_name"

    abr_algo="RL"

    #actor_batch_size=59 # 60 actually

    sed "s/\"num_actors\"\: 1/\"num_actors\"\: $num_actors/" $cur_dir/params_base.json > "${dir}/params.json"
    sed -i "s/\"memsize\"\: 5320000/\"memsize\"\: $memory_size/" "${dir}/params.json"
    sudo killall -s9 python client orca-server-mahimahi

    epoch=20
    act_port=$port_base

    UPLINK_TRACE="wired6"
    QUEUE_SIZE=30
    DELAY=10
    TRAINING_DURATION=180
    

    if [ $1 -eq 4 ]
    then
        # If you are here: You are going to perform an evaluation over an emulated link
        num_actors=1
        sed "s/\"num_actors\"\: 1/\"num_actors\"\: $num_actors/" $cur_dir/params_base.json > "${dir}/params.json"

        echo "[$0]: ./learner.sh  $dir $first_time  &"
        ./learner.sh  $dir ${first_time} &
        #Bring up the actors:

        act_id=0
        downl=$trace_name
        del=$DELAY
        upl=$UPLINK_TRACE
        qs=$QUEUE_SIZE

        echo "[$0]: ./actor.sh ${act_port} $epoch ${first_time} $scheme_ $dir $act_id $downl $upl $del $eval_duration $qs 0 $orca_binary $abr_algo &"
        ./actor.sh ${act_port} $epoch ${first_time} $scheme_ $dir $act_id $downl $upl $del $eval_duration $qs 0 $orca_binary $abr_algo &
        pids="$pids $!"
        for pid in $pids
        do
            echo "[$0]: waiting for $pid"
            wait $pid
        done
        #Bring down the learner and actors ...
        for i in `seq 0 $((num_actors))`
        do
            sudo killall -s15 python
            sudo killall -s15 orca-server-mahimahi
            sudo killall -s15 client
        done
    else
    # If you are here: You are going to start/continue learning a better model!

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
       sleep 10

       #Bring up the actors:
       # Here, we go with single actor
        act_id=0
        
        del=$DELAY
        upl=$UPLINK_TRACE
        qs=$QUEUE_SIZE
        trace_idx=$trace_start_idx
       for i in `seq 0 $((num_actors))`
        do
            trace_idx=$((trace_start_idx+i))
            trace_name="$trace_name_prefix$trace_idx$trace_name_postfix"
            downl=$trace_name
            echo "[$0]: ./actor.sh ${act_port} $epoch ${first_time} $scheme_ $dir $act_id $downl $upl $del $TRAINING_DURATION $qs $max_steps $orca_binary $abr_algo &"
            ./actor.sh ${act_port} $epoch ${first_time} $scheme_ $dir $act_id $downl $upl $del $TRAINING_DURATION $qs $max_steps $orca_binary $abr_algo &
            pids="$pids $!"
            act_id=$((act_id+1))
            act_port=$((port_base+act_id))
            sleep 2
        done

       for pid in $pids
       do
           echo "[$0]: waiting for $pid"
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
           sudo killall -s15 orca-server-mahimahi
       done
    fi
    time_end=$(date +%s)
    time_tot=$((time_end-time_start))
    echo "[$0]: Script Duration: $time_tot"
else
    echo "[$0]: usage: $0 [{Learning from scratch=1} {Continue your learning=0} {Just Do Evaluation=4}] [base port number ]"
fi

