#/bin/bash
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
