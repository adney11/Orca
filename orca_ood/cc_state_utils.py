import requests
import time

def send_throughput_estimate(throughput, msg="cc_state"):
    data = {"throughput_estimate": throughput,
            "msg": msg}
    url = 'http://127.0.0.1:8334/post'
    post_req = requests.post(url=url, json=data)
    return post_req.text

def send_state(state):
    url = 'http://127.0.0.1:8334/post'
    data = {
        "state_0": state[0],
        "state_1": state[1],
        "state_2": state[2],
        "state_3": state[3],
        "state_4": state[4],
        "state_5": state[5],
        "state_6": state[6],
        "time": time.time()
    }
    post_req = requests.post(url=url, json=data)
    return post_req.text