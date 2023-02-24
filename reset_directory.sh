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

needed_dirs=($dir_log $dir_logs $dir_plots $dir_results $dir_traindir $dir_traindir_learner0)

# check if all these directories exist, if not, make them, if yes, rm contents
for d in ${needed_dirs[@]}; do
    if [ ! -d $d ]; then
        echo "making $d"
        mkdir $d
    else
        find "$d/" -type f -not -name "learner0" -delete
    fi
done