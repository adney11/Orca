#!/bin/bash -x
if [ $# -eq 2 ]
then

    # Begin Training new model
    # ./06_0_0_dist-train-orca.sh bucket_orca 1 0 6to12mbps_train/

    # Continue Training most recent checkpoint model: make sure checkpoint file has full path
    # ./06_0_0_dist-train-orca.sh bucket_orca 3 0 6to12mbps_train/
    source setup.sh

    # Command Line Arguments
    orcadir=$1
    first_time=$2
    port_base=44444
    abr_algo='None'
    

    cur_dir=`pwd -P`
    scheme_="cubic"
    max_steps=50000         #Run untill you collect 50k samples per actor
    eval_duration=320
    num_actors=6
    memory_size=$((max_steps*num_actors))
    dir="${cur_dir}/${orcadir}"
    echo "[$0]: dir is: $dir"
    #exit
    orca_binary="orca-server-mahimahi"
    echo "[$0]: orca_binary is: $orca_binary"
    
    QUEUE_SIZE=50                                 # in number of packets
    DELAY=80                                      # in ms
    TRAINING_DURATION=0                           # seconds: set this to end training after these many seconds

    remote_output_dir="${dir}/remote_output_logs"

    #sed "s/\"num_actors\"\: 1/\"num_actors\"\: $num_actors/" $cur_dir/params_base.json > "${dir}/params.json"
    #sed -i "s/\"memsize\"\: 5320000/\"memsize\"\: $memory_size/" "${dir}/params.json"
    sed -i "s/\"num_actors\": [[:digit:]]\+,/\"num_actors\": $num_actors,/" "${dir}/params.json"
    sed -i "s/\"memsize\": [[:digit:]]\+,/\"memsize\": $memory_size,/" "${dir}/params.json"
    
    sudo killall -s9 python orca-server-mahimahi-http orca-server-mahimahi

    epoch=20
    act_port=$port_base
    
    #Bring up the learner:
    #echo "[$0]: ./learner.sh  $dir $first_time &"
    if [ $first_time -eq 1 ];
    then
        # Start the learning from the scratch
        echo "[$0]: /users/`logname`/venv/bin/python ${dir}/d5.py --job_name=learner --task=0 --base_path=${dir} &"
        /users/`logname`/venv/bin/python ${dir}/d5.py --job_name=learner --task=0 --base_path=${dir} &
        lpid=$!
    elif [ $first_time -eq 2 ];
    then
        # Continue the learning on top of previous model
        echo "[$0]: /users/`logname`/venv/bin/python ${dir}/d5.py --job_name=learner --task=0 --base_path=${dir} --load &"
        /users/`logname`/venv/bin/python ${dir}/d5.py --job_name=learner --task=0 --base_path=${dir} --load &
        lpid=$!
    elif [ $first_time -eq 4 ];
    then
        # Testing the model
        echo "setting single_actor_eval to true"
        sed -i "s/\"single_actor_eval\": false,/\"single_actor_eval\": true,/" "$dir/params.json"

        eval_duration=120
        run=2

        act_port=$port_base
        for i in `seq 0 9`;
        do
            downl="6to10mbps_test-$i-mahimahi"
            upl="wired12"
            act_id=0
            del=10
            qs=30
            ./actor.sh ${act_port} $epoch ${first_time} $scheme_ $dir $act_id $downl $upl $del $eval_duration $qs 0 $orca_binary $abr_algo "None" >> $dir/logs/"output-test-${i}"
            killall $orca_binary client python
            act_port=$((act_port+1))
            sleep 5
        done



        act_port=$port_base
        for i in 6 8 10
        do
            downl="constant-mbps-$i-mahimahi"
            upl="wired12"
            act_id=0
            del=10
            qs=30
            ./actor.sh ${act_port} $epoch ${first_time} $scheme_ $dir $act_id $downl $upl $del $eval_duration $qs 0 $orca_binary $abr_algo "None" >> $dir/logs/"output-train_eval-${i}"
            killall $orca_binary client python
            act_port=$((act_port+1))
            sleep 5
        done
        
        cp -r "${dir}/log" "${dir}/log_run-${run}"
        cp -r "${dir}/plots" "${dir}/plots_run-${run}"

        echo "setting single_actor_eval to false"
        sed -i "s/\"single_actor_eval\": true,/\"single_actor_eval\": false,/" "$dir/params.json"

        ./reset_directory.sh $orcadir/

        exit
    fi
    sleep 10
    echo "starting actors on remote machines"
    #Bring up the actors:
    act_id=0
    curr_node_idx=0
    act_port=$port_base
    training_duration=$TRAINING_DURATION
  
    for dl in 6 8 10
    do
        downl="constant-mbps-$dl-mahimahi"
        upl=$downl
        for del in 10 80
        do
            bdp=$((2*dl*del/12))      #12Mbps=1pkt per 1 ms ==> BDP=2*del*BW=2*del*dl/12
            for qs in $((2*bdp))
            do
                ./actor.sh ${act_port} $epoch ${first_time} $scheme_ $dir $act_id $downl $upl $del $training_duration $qs $max_steps $orca_binary $abr_algo "None" >> $remote_output_dir/"actor-$act_id.out" &
                pids="$pids $!"
                act_id=$((act_id+1))
                act_port=$((port_base+act_id))
                sleep 2
            done
        done
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

else
    echo "usage: $0 [{Learning from scratch=1} {Continue your learning=0} {Just Do Evaluation=4}] [base port number ] [abr_algo]"
fi

