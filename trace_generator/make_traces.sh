#!/bin/bash -x


organize() {
    trace_name=$1
    mkdir ./traces/$trace_name

    mkdir ./traces/$trace_name/mahimahi
    mv *mahimahi ./traces/$trace_name/mahimahi

    mkdir ./traces/$trace_name/sec
    mv *sec ./traces/$trace_name/sec
    
    mkdir ./traces/$trace_name/ms
    mv *ms ./traces/$trace_name/ms

    mv $trace_name* ./traces/$trace_name
}

num_variants=20
#python trace_generator.py start_thr duration change_time change_type jitter min_thr max_thr trace_name num_variants

trace_name="6mbps_nochange_baseline"
python trace_generator.py 6 180 "" "" 0.2 0.2 6 $trace_name $num_variants
organize $trace_name

trace_name="6mbps_random_decrease_big"
python trace_generator.py 6 180 "80" "random-decrease-big" 0.2 0.2 6 $trace_name $num_variants
organize $trace_name

trace_name="6mbps_random"
python trace_generator.py 6 180 "40 80" "random-small random-big" 0.2 0.2 6 $trace_name $num_variants
organize $trace_name

trace_name="6mbps_3mbps_gradual"
python trace_generator.py 6 180 "85 86 87 88 89 90 91 92 93 94" "decrease-0.3 decrease-0.3 decrease-0.3 decrease-0.3 decrease-0.3 decrease-0.3 decrease-0.3 decrease-0.3 decrease-0.3 decrease-0.3" 0.2 0.2 6 $trace_name $num_variants
organize $trace_name

trace_name="6mbps_3mbps_oscillating"
python trace_generator.py 6 180 "10 20 30 40 50 60 70 80 90 100 110" "set-3 set-6 set-3 set-6 set-3 set-6 set-3 set-6 set-3 set-6 set-3" 0.2 0.2 6 $trace_name $num_variants
organize $trace_name

trace_name="3mbps_nochange_baseline"
python trace_generator.py 3 180 "" "" 0.2 0.2 6 $trace_name $num_variants
organize $trace_name

trace_name="3mbps_random_increase_big"
python trace_generator.py 3 180 "90" "random-increase-big" 0.2 0.2 6 $trace_name $num_variants
organize $trace_name

trace_name="3mbps_random_6mbps_max"
python trace_generator.py 3 180 "40 60 80 100" "random-small random-small random-small random-small" 0.2 0.2 6 $trace_name $num_variants
organize $trace_name








####### v1 ########

#trace_name="6mbps_random_increase_big"
#python trace_generator.py 6 320 "125" "random-increase-big" 0.2 2 24 $trace_name 20
#mkdir ./traces/$trace_name
#mv $trace_name* ./traces/$trace_name

#trace_name="6mbps_random_increase_small"
#python trace_generator.py 6 320 "125" "random-increase-small" 0.2 2 24 $trace_name 20
#mkdir ./traces/$trace_name
#mv $trace_name* ./traces/$trace_name
#
#trace_name="12mbps_random_increase_big"
#python trace_generator.py 12 320 "125" "random-increase-big" 0.2 2 24 $trace_name 20
#mkdir ./traces/$trace_name
#mv $trace_name* ./traces/$trace_name
#
#trace_name="12mbps_random_decrease_big"
#python trace_generator.py 12 320 "125" "random-decrease-big" 0.2 2 24 $trace_name 20*
#mkdir ./traces/$trace_name
#mv $trace_name* ./traces/$trace_name
#
#trace_name="24mbps_random_decrease_big"
#python trace_generator.py 24 320 "125" "random-decrease-big" 0.2 2 24 $trace_name 20
#mkdir ./traces/$trace_name
#mv $trace_name* ./traces/$trace_name
#
#trace_name="24mbps_random_decrease_big_with_3_random_small_increase"
#python trace_generator.py 24 320 "10 50 90 150" "random-decrease-big random-increase-small random-increase-small random-increase-small" 0.2 2 24 $trace_name 20
#mkdir ./traces/$trace_name
#mv $trace_name* ./traces/$trace_name
#
#trace_name="24mbps_with_multiple_random_small_decrease"
#python trace_generator.py 24 320 "10 50 80 150" "random-decrease-small random-decrease-small random-decrease-small random-decrease-small" 0.2 2 24 $trace_name 20
#mkdir ./traces/$trace_name
#mv $trace_name* ./traces/$trace_name
#
#trace_name="random_change_between_24_and_2mbps"
#python trace_generator.py 24 320 "10 40 80 150 200" "random-small random-big random-small random-big random-small" 0.2 2 24 $trace_name 20
#mkdir ./traces/$trace_name
#mv $trace_name* ./traces/$trace_name