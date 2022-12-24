import os
import sys
import signal
import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from pyvirtualdisplay import Display
from time import sleep

# TO RUN: download https://pypi.python.org/packages/source/s/selenium/selenium-2.39.0.tar.gz
# run sudo apt-get install python-setuptools
# run sudo apt-get install xvfb
# after untar, run sudo python setup.py install
# follow directions here: https://pypi.python.org/pypi/PyVirtualDisplay to install pyvirtualdisplay

# For chrome, need chrome driver: https://code.google.com/p/selenium/wiki/ChromeDriver
# chromedriver variable should be path to the chromedriver
# the default location for firefox is /usr/bin/firefox and chrome binary is /usr/bin/google-chrome
# if they are at those locations, don't need to specify

import random
import logging

def dp(msg):
	LOG.debug(msg)

def timeout_handler(signum, frame):
	raise Exception("Timeout")




ip = sys.argv[1]
port = sys.argv[2]
run_time = 200
process_id = sys.argv[3]
logfilename = sys.argv[4]
abr_algo = sys.argv[5] #"RL"
sleep_time = random.randint(1,5)
FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(filename=f'./orca_pensieve/logs/orca_pensieve-{logfilename}-run_video.log', level=logging.DEBUG,format=FORMAT)
LOG = logging.getLogger(__name__)
LOG.debug("starting run_video")
	
# prevent multiple process from being synchronized
sleep(int(sleep_time))
	
# generate url
url = 'http://' + ip + ':' + port + '/' + 'myindex_' + abr_algo + '.html'
LOG.debug(f"url is: {url}")

# timeout signal
signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(run_time + 40)
	
try:
	# copy over the chrome user dir
	dp("copy over the chrome user dir...")
	default_chrome_user_dir = '/newhome/Orca/orca_pensieve/pensieve/abr_browser_dir/chrome_data_dir'
	chrome_user_dir = '/tmp/chrome_user_dir_id_' + process_id
	os.system('rm -r ' + chrome_user_dir)
	os.system('cp -r ' + default_chrome_user_dir + ' ' + chrome_user_dir)
	os.system('sudo chown -R acardoza ' + chrome_user_dir)
	
	# start abr algorithm server
	dp("start abr algorithm server...")
	python_binary = "/users/acardoza/venv/bin/python"
	rl_server_dir = "/newhome/Orca/orca_pensieve/pensieve"
	
	if abr_algo == 'RL':
		command = 'exec ' + python_binary + ' ' + rl_server_dir +'/rl_server_no_training.py ' + logfilename
	elif abr_algo == 'fastMPC':
		command = 'exec ' + python_binary + ' ' + rl_server_dir +'/mpc_server.py ' + logfilename
	elif abr_algo == 'robustMPC':
		command = 'exec ' + python_binary + ' ' + rl_server_dir +'/robust_mpc_server.py ' + logfilename
	else:
		command = 'exec ' + python_binary + ' ' + rl_server_dir +'/simple_server.py ' + abr_algo + ' ' + logfilename
	LOG.debug(f"rl server command is: {command}")
	proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
	sleep(2)
	
	# to not display the page in browser
	dp("starting display...")
	display = Display(visible=0, size=(800,600))
	display.start()
	dp("display started...")

	# initialize chrome driver
	dp("initialize chrome driver")
	#options=Options()
	options=webdriver.ChromeOptions()
	chrome_driver = '/newhome/Orca/orca_pensieve/pensieve/abr_browser_dir/chromedriver'
	options.add_argument('--no-sandbox')
	options.add_argument('--headless')
	options.add_argument('--user-data-dir=' + chrome_user_dir)	
	options.add_argument('--ignore-certificate-errors')
	options.add_argument('--disable-web-security')
	options.add_argument('--disable-gpu')
	options.add_argument('--disable-software-rasterizer')
	options.add_argument('--autoplay-policy=no-user-gesture-required')
	options.add_argument('--dns-prefetch-disable')
	experimentalFlags = ['block-insecure-private-network-requests@2']
	chromeLocalStatePrefs = {'browser.enabled_labs_experiments': experimentalFlags}	
	options.add_experimental_option('localState', chromeLocalStatePrefs)
	try:
		driver=webdriver.Chrome(chrome_driver, chrome_options=options)
	except:
		dp("failed to start driver - trying again")
		driver=webdriver.Chrome(chrome_driver, chrome_options=options)
	#chromeservice=Service(executable_path=chrome_driver)
	#driver=webdriver.Chrome(service=chromeservice, options=options)
	dp("chrome driver initialized...")


	# run chrome
	driver.set_page_load_timeout(10)
	dp("page parameters set")
	sleep(10)
	dp("getting url after sleeping 10 seconds")
	try:
		driver.get(url)
	except TimeoutException as to_ex:
		dp(f'FAILED TO GET URL: {to_ex}')
		driver.refresh()
	dp("got url")
	dp(f"sleeping for {run_time} seconds")
	sleep(run_time)
	#input("press enter to end")
	driver.quit()
	display.stop()
	
	
	dp("stopped chrome driver")

	# kill abr algorithm server
	proc.send_signal(signal.SIGINT)
	# proc.kill()
	
	print('done')
	
except Exception as e:
	dp(f'got exception {e}')
	try: 
		display.stop()
	except:
		dp("tried to stop display but failed..")
	try:
		driver.quit()
	except:
		dp("tried to quit driver but failed....")
	try:
		proc.send_signal(signal.SIGINT)
	except:
		dp("tried to send signal to rl process but failed")
	
	LOG.error(e)

