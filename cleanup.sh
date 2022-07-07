pids=$(pgrep chrome)

for pid in $pids
do

    echo $pid
    kill -9 $pid
done
