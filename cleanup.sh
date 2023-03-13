#/bin/bash

# Script will clean up any stray python processes, and empty out logs, plots, remote_output_logs
# and any stray files.

# Be sure to save logs, before calling this with 1 option

if [ $# -lt 1 ];
then
    echo "enter directory to clean"
    exit
fi
curr_dir=$1
echo "Cleaning ${curr_dir}"

echo "Warning - this script will kill all python programs"
pids=$(pgrep python)
pids+=" $(pgrep chrome)"
pids+=" $(pgrep orca-server)"

if [ ! -z "$pids" ]
then
    echo "killing $pids"
    kill -9 $pids
else
    echo "Nothing to kill - you're good to go!"
fi

if [ $# -eq 2 ];
then
    rm -r ./state_action ./rl_logging 
    rm {curr_dir}logs/* ./${curr_dir}/plots/*
    rm ${curr_dir}remote_output_logs/*
    rm -r ${curr_dir}log/*
    rm nohup.out
    rm ${curr_dir}remote_output_logs/*
    rm -r ${curr_dir}smax_distributions ${curr_dir}action_conf_pairs
fi

