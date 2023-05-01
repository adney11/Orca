#!/bin/bash

if [ $# -ne 1 ]; then
    echo "[usage]: provide directory to reset"
    exit
fi

dir=$1

# needed directories inside $dir
dir_log="${dir}log"
dir_logs="${dir}logs"
dir_plots="${dir}plots"
dir_results="${dir}results"
dir_traindir="${dir}train_dir"
dir_traindir_learner0="${dir_traindir}/learner0"
dir_remote_output="${dir}remote_output_logs"

needed_dirs=($dir_log $dir_logs $dir_plots $dir_results $dir_traindir $dir_traindir_learner0 $dir_remote_output)

# check if all these directories exist, if not, make them, if yes, rm contents
for d in ${needed_dirs[@]}; do
    if [ ! -d $d ]; then
        echo "making $d"
        mkdir $d
    else
        if [ $d == $dir_traindir ]; then
            mv $d/learner0 $d/..
            rm -r $d/*
            mv $d/../learner0 $d
        elif [ $d == $dir_traindir_learner0 ]; then
            echo "saving learner0 contents"
        else
            rm $d/*
        fi  
    fi
done