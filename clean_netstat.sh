#!/bin/bash 
pids=$(sudo netstat -tlnp | grep mm-delay | awk -F ' ' '{print $7}' | awk -F '/' '{print $1}')
kill -9 $pids