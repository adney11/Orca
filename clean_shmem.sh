#!/bin/bash -x 

shids=$(ipcs -m -p --human -b | grep acardoza | awk -F ' ' '{print $1}')
for shid in $shids; do ipcrm -m $shid; done;