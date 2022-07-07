#!/usr/bin/python3.8
# script to add demarkation line to log file - to differentiate runs
# takes title of new test, put config and stuff here as input

import os
import sys
from datetime import datetime


resultsdir = './results/'
logDir = './logs/'
logsDir = './log/'


dirs = {resultsdir, logDir, logsDir, './orca_pensieve/log/'}
for dir in dirs:
    for filename in os.listdir(dir):
        with open(os.path.join(dir, filename), 'a') as f:
            now = datetime.now().strftime("-------- [ %d-%m-%Y %H:%M ] --------")
            f.write(f'{now}\n')


with open('chrome_retry_log', 'a') as f:
    now = datetime.now().strftime("-------- [ %d-%m-%Y %H:%M ] --------")
    f.write(f'{now}\n') 
    
print('book keeping done')