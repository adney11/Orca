from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import sys
import os
import time

import logging

LOG = None

CC_STATE_PORT = 8334

STATE_LOG = './orca_ood/orca_state/state'

def make_request_handler(input_dict):
    class Request_Handler(BaseHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            self.input_dict = input_dict
            self.statelog = input_dict['statelog']
            self.state_0 = []
            self.state_1 = []
            self.state_2 = []
            self.state_3 = []
            self.state_4 = []
            self.state_5 = []
            self.state_6 = []
            self.times = []
            BaseHTTPRequestHandler.__init__(self, *args, **kwargs)

        def do_POST(self):
            LOG.info("Got Post")
            content_length = int(self.headers['Content-Length'])
            #LOG.info(f"content length: {content_length}")
            payload = self.rfile.read(content_length)
            #LOG.info(f"payload: {payload}")
            post_data = json.loads(payload)
            LOG.info(f"post data: {post_data}")
            self.state_0.append(post_data['state_0'])
            self.state_1.append(post_data['state_1'])
            self.state_2.append(post_data['state_2'])
            self.state_3.append(post_data['state_3'])
            self.state_4.append(post_data['state_4'])
            self.state_5.append(post_data['state_5'])
            self.state_6.append(post_data['state_6'])
            now = post_data['time']
            send_data = f"recieved state for time: {now}"
            
            self.statelog.write(str(now) + ',' +
                                str(post_data['state_0']) + ',' + 
                                str(post_data['state_1']) + ',' + 
                                str(post_data['state_2']) + ',' + 
                                str(post_data['state_3']) + ',' + 
                                str(post_data['state_4']) + ',' + 
                                str(post_data['state_5']) + ',' + 
                                str(post_data['state_6']) + '\n') 
            self.statelog.flush()
            
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.send_header('Content-Length', len(send_data))
            self.send_header('Access-Control-Allow-Origin', "*")
            self.end_headers()
            self.wfile.write(send_data.encode())
        
        def do_GET(self):
            pass

        def log_message(self, format, *args):
            return

    return Request_Handler

    
def run(server_class=HTTPServer, statelog_path=STATE_LOG):
    with open(statelog_path, 'a') as statelog: 
        input_dict = {'statelog': statelog}
        handler = make_request_handler(input_dict)
        server_addr = ('localhost', CC_STATE_PORT)
    
        httpd = server_class(server_addr, handler)
        LOG.info("started CC state tracker")
        httpd.serve_forever()

def main():
    if len(sys.argv) == 2:
        logfilename = sys.argv[1]
        logging.basicConfig(filename=f'/newhome/Orca/orca_ood/logs/cc_state_tracker-{logfilename}.log', level=logging.DEBUG)
        global LOG
        LOG = logging.getLogger(__name__)
        print('state tracker log file set')
        run(statelog_path=STATE_LOG + '-' + logfilename)
    else:
        run()
        
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        LOG.error("Keyboard Interrupted")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)