for i in $(ls -d ./traces/*/)
do
    echo ${i%%/}
    pushd ${i%%/}
    pwd
    mkdir mahimahi_traces
    mv *mahimahi ./mahimahi_traces
    popd
done